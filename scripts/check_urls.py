#!/usr/bin/env python3
"""
check_urls.py
=============
Check all URLs in all_resources.csv are reachable.
Uses a HEAD request first, falls back to GET on failure.
Prints a markdown report and exits with code 1 if dead URLs are found.

Usage:
    python scripts/check_urls.py [--csv data/all_resources.csv]
                                 [--output url_report.md]
                                 [--workers 20]
                                 [--timeout 12]
"""

import argparse
import concurrent.futures
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# Suppress InsecureRequestWarning if SSL verification is skipped
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class CheckResult:
    resource_id: str
    resource_type: str
    title: str
    url: str
    status: int | None
    ok: bool
    method: str
    error: str = ""
    elapsed_ms: float = 0.0


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; climbing-resources-db URL checker; "
        "+https://github.com/timothy22000/climbing-resources-db)"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*",
}

# Status codes considered "alive" even though they are not 200
ALIVE_STATUSES = {200, 201, 204, 301, 302, 303, 307, 308, 401, 403, 405, 429}


def check_url(row: dict, timeout: int) -> CheckResult:
    url = row["url"].strip()
    if not url:
        return CheckResult(
            resource_id=row["resource_id"],
            resource_type=row["resource_type"],
            title=row["title"],
            url=url,
            status=None,
            ok=False,
            method="-",
            error="empty URL",
        )

    start = time.time()
    session = requests.Session()

    for method in ("HEAD", "GET"):
        try:
            resp = session.request(
                method,
                url,
                headers=HEADERS,
                timeout=timeout,
                allow_redirects=True,
                verify=True,
            )
            elapsed = (time.time() - start) * 1000
            ok = resp.status_code in ALIVE_STATUSES
            return CheckResult(
                resource_id=row["resource_id"],
                resource_type=row["resource_type"],
                title=row["title"],
                url=url,
                status=resp.status_code,
                ok=ok,
                method=method,
                elapsed_ms=elapsed,
            )
        except requests.exceptions.SSLError:
            # Retry without SSL verification
            try:
                resp = session.request(
                    method,
                    url,
                    headers=HEADERS,
                    timeout=timeout,
                    allow_redirects=True,
                    verify=False,
                )
                elapsed = (time.time() - start) * 1000
                ok = resp.status_code in ALIVE_STATUSES
                return CheckResult(
                    resource_id=row["resource_id"],
                    resource_type=row["resource_type"],
                    title=row["title"],
                    url=url,
                    status=resp.status_code,
                    ok=ok,
                    method=f"{method}(no-ssl)",
                    elapsed_ms=elapsed,
                )
            except Exception as e:
                if method == "HEAD":
                    continue
                return CheckResult(
                    resource_id=row["resource_id"],
                    resource_type=row["resource_type"],
                    title=row["title"],
                    url=url,
                    status=None,
                    ok=False,
                    method=method,
                    error=str(e),
                )
        except requests.exceptions.ConnectionError as e:
            if method == "HEAD":
                continue
            return CheckResult(
                resource_id=row["resource_id"],
                resource_type=row["resource_type"],
                title=row["title"],
                url=url,
                status=None,
                ok=False,
                method=method,
                error=f"ConnectionError: {e}",
            )
        except requests.exceptions.Timeout:
            if method == "HEAD":
                continue
            return CheckResult(
                resource_id=row["resource_id"],
                resource_type=row["resource_type"],
                title=row["title"],
                url=url,
                status=None,
                ok=False,
                method=method,
                error="Timeout",
            )
        except Exception as e:
            if method == "HEAD":
                continue
            return CheckResult(
                resource_id=row["resource_id"],
                resource_type=row["resource_type"],
                title=row["title"],
                url=url,
                status=None,
                ok=False,
                method=method,
                error=str(e),
            )

    return CheckResult(
        resource_id=row["resource_id"],
        resource_type=row["resource_type"],
        title=row["title"],
        url=url,
        status=None,
        ok=False,
        method="-",
        error="All methods failed",
    )


def build_report(results: list[CheckResult], elapsed_total: float) -> str:
    dead  = [r for r in results if not r.ok]
    alive = [r for r in results if r.ok]
    ts    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# URL Health Report",
        "",
        f"**Run:** {ts}  |  "
        f"**Total:** {len(results)}  |  "
        f"**OK:** {len(alive)}  |  "
        f"**Dead:** {len(dead)}  |  "
        f"**Duration:** {elapsed_total:.1f}s",
        "",
    ]

    if dead:
        lines += [
            f"## ✗ Dead / unreachable ({len(dead)})",
            "",
            "| ID | Type | Title | URL | Status | Error |",
            "|---|---|---|---|---|---|",
        ]
        for r in sorted(dead, key=lambda x: x.resource_id):
            status = str(r.status) if r.status else "-"
            err    = (r.error[:60] + "…") if len(r.error) > 60 else r.error
            title  = r.title[:40] + "…" if len(r.title) > 40 else r.title
            lines.append(f"| {r.resource_id} | {r.resource_type} | {title} | {r.url} | {status} | {err} |")
        lines.append("")
    else:
        lines += ["## ✓ All URLs are alive", ""]

    lines += [
        "## All results",
        "",
        "| ID | Type | Status | Method | ms | URL |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(results, key=lambda x: x.resource_id):
        icon   = "✓" if r.ok else "✗"
        status = str(r.status) if r.status else "-"
        ms     = f"{r.elapsed_ms:.0f}" if r.elapsed_ms else "-"
        lines.append(f"| {icon} {r.resource_id} | {r.resource_type} | {status} | {r.method} | {ms} | {r.url} |")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Check all resource URLs")
    parser.add_argument("--csv",     default="data/all_resources.csv")
    parser.add_argument("--output",  default="url_report.md")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args()

    df = pd.read_csv(args.csv, dtype=str).fillna("")
    rows = df.to_dict("records")
    print(f"Checking {len(rows)} URLs with {args.workers} workers …")

    t0 = time.time()
    results: list[CheckResult] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(check_url, r, args.timeout): r for r in rows}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            icon = "✓" if result.ok else "✗"
            status = result.status or "-"
            print(f"  [{i:>3}/{len(rows)}] {icon} {result.resource_id:<8} {status}", flush=True)
            results.append(result)

    elapsed = time.time() - t0
    report  = build_report(results, elapsed)

    out = Path(args.output)
    out.write_text(report, encoding="utf-8")
    print(f"\nReport written to {out}")

    dead = [r for r in results if not r.ok]
    if dead:
        print(f"\n✗ {len(dead)} dead URL(s). Report: {out}")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} URLs are alive.")


if __name__ == "__main__":
    main()
