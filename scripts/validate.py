#!/usr/bin/env python3
"""
validate.py
===========
Schema and data quality validation for all_resources.csv.
Exits with code 1 if any critical errors are found.

Usage:
    python scripts/validate.py [--csv data/all_resources.csv]
"""

import argparse
import re
import sys
from datetime import datetime

import pandas as pd

# ── Controlled vocabularies ───────────────────────────────────────────────────

RESOURCE_TYPES  = {"book", "youtube", "course", "website", "podcast"}
SKILL_LEVELS    = {"beginner", "intermediate", "advanced", "elite"}
DISCIPLINE_VALS = {"sport", "bouldering", "trad", "top_rope", "all"}
BOOL_VALS       = {"True", "False", "true", "false", "TRUE", "FALSE", "1", "0"}
LANGUAGES       = {"en", "de", "fr", "es", "nb", "ja", "pt", "it", "nl", "sv"}

TECHNIQUE_TAGS = {
    # Movement positions & body mechanics
    "footwork", "hip_rotation", "drop_knee", "flagging", "heel_hooks",
    "toe_hooks", "knee_bars",
    # Hold types
    "crimp_grip", "slopers", "pinches", "underclings",
    # Route / terrain types
    "slab", "overhang", "crack_climbing", "offwidth",
    # Movement quality
    "dynamic_movement", "route_reading", "strength",
    # Technical gear skills
    "gear_placement", "anchors",
    # Training methods
    "finger_training", "periodization",
    # Mental / rehab
    "mental_game", "lead_falling", "injury_rehab",
}

# Fields required for every resource
REQUIRED_FIELDS = [
    "resource_id", "resource_type", "title", "creator",
    "disciplines", "technique_tags", "skill_level_min", "skill_level_max",
    "is_free", "url", "language", "country", "description",
    "date_added", "last_verified",
]

# Fields required only for books
BOOK_REQUIRED_FIELDS = ["isbn", "year"]

ISBN_RE   = re.compile(r"^\d{3}-\d{10}$")
ID_RE     = re.compile(r"^(BK|YT|CR|WB|PD)-\d{3}$")
DATE_RE   = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE    = re.compile(r"^https://")


def validate(csv_path: str) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    df = pd.read_csv(csv_path, dtype=str).fillna("")

    # ── Missing columns ───────────────────────────────────────────────────────
    missing_cols = [c for c in REQUIRED_FIELDS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing columns: {missing_cols}")
        return errors  # can't continue without columns

    # ── Row-level checks ──────────────────────────────────────────────────────
    seen_ids: set[str] = set()

    for idx, row in df.iterrows():
        n = idx + 2  # 1-indexed + header row

        rid   = row["resource_id"].strip()
        rtype = row["resource_type"].strip()

        # Required fields must be non-empty
        for field in REQUIRED_FIELDS:
            if not row[field].strip():
                errors.append(f"Row {n} ({rid}): '{field}' is empty")

        # year is required for books, optional for others
        if rtype == "book" and not row.get("year", "").strip():
            errors.append(f"Row {n} ({rid}): 'year' is empty for a book")

        # resource_id format
        if rid and not ID_RE.match(rid):
            errors.append(f"Row {n}: resource_id '{rid}' does not match pattern TYPE-NNN")

        # Duplicate IDs
        if rid in seen_ids:
            errors.append(f"Row {n}: duplicate resource_id '{rid}'")
        seen_ids.add(rid)

        # resource_type
        if rtype not in RESOURCE_TYPES:
            errors.append(f"Row {n} ({rid}): resource_type '{rtype}' not in {RESOURCE_TYPES}")

        # skill levels
        for field in ("skill_level_min", "skill_level_max"):
            val = row[field].strip()
            if val and val not in SKILL_LEVELS:
                errors.append(f"Row {n} ({rid}): {field} '{val}' not in {SKILL_LEVELS}")

        # disciplines
        for disc in row["disciplines"].split("|"):
            d = disc.strip()
            if d and d not in DISCIPLINE_VALS:
                errors.append(f"Row {n} ({rid}): discipline '{d}' not in {DISCIPLINE_VALS}")

        # technique_tags
        tags = [t.strip() for t in row["technique_tags"].split("|") if t.strip()]
        for tag in tags:
            if tag not in TECHNIQUE_TAGS:
                errors.append(f"Row {n} ({rid}): technique_tag '{tag}' not in approved taxonomy")
        if len(tags) < 2:
            warnings.append(f"Row {n} ({rid}): only {len(tags)} technique_tag(s). Recommend at least 2.")

        # is_free
        if row["is_free"].strip() not in BOOL_VALS:
            errors.append(f"Row {n} ({rid}): is_free '{row['is_free']}' must be True or False")

        # URL
        url = row["url"].strip()
        if url and not URL_RE.match(url):
            errors.append(f"Row {n} ({rid}): url must start with 'https://'")

        # ISBN (books only)
        isbn = row.get("isbn", "").strip()
        if rtype == "book":
            if not isbn:
                errors.append(f"Row {n} ({rid}): book is missing isbn")
            elif not ISBN_RE.match(isbn):
                errors.append(f"Row {n} ({rid}): isbn '{isbn}' does not match 978-XXXXXXXXXX format")

        # language
        lang = row["language"].strip()
        if lang and lang not in LANGUAGES:
            warnings.append(f"Row {n} ({rid}): language '{lang}' not in common set. Verify it is a valid ISO 639-1 code.")

        # Dates
        for field in ("date_added", "last_verified"):
            val = row[field].strip()
            if val:
                if not DATE_RE.match(val):
                    errors.append(f"Row {n} ({rid}): {field} '{val}' is not ISO 8601 (YYYY-MM-DD)")
                else:
                    try:
                        datetime.strptime(val, "%Y-%m-%d")
                    except ValueError:
                        errors.append(f"Row {n} ({rid}): {field} '{val}' is not a valid date")

    # ── Summary ───────────────────────────────────────────────────────────────
    if warnings:
        print(f"⚠  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   {w}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate climbing resources CSV")
    parser.add_argument("--csv", default="data/all_resources.csv")
    args = parser.parse_args()

    print(f"Validating {args.csv} …")
    errors = validate(args.csv)

    if errors:
        print(f"\n✗ {len(errors)} error(s):")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("✓ All checks passed. No errors.")


if __name__ == "__main__":
    main()
