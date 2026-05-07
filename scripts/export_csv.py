#!/usr/bin/env python3
"""
export_csv.py
=============
Regenerate all data files from the master XLSX source.

Usage:
    python scripts/export_csv.py [--source path/to/xlsx] [--out path/to/data/]

Defaults to source/climbing_resources_database.xlsx → data/.
"""

import argparse
import pathlib
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

SHEET_MAP = {
    "books":    "book",
    "youtube":  "youtube",
    "courses":  "course",
    "websites": "website",
    "podcasts": "podcast",
}

REQUIRED_COLS = [
    "resource_id", "resource_type", "title", "creator", "year",
    "disciplines", "technique_tags", "skill_level_min", "skill_level_max",
    "is_free", "price_usd", "url", "isbn", "language", "country",
    "description", "date_added", "last_verified",
]


def load_sheet(xl: pd.ExcelFile, sheet_name: str, resource_type: str) -> pd.DataFrame:
    df = xl.parse(sheet_name, dtype=str).fillna("")
    df["resource_type"] = resource_type
    # Ensure all required columns exist (fill missing with "")
    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = ""
    return df[REQUIRED_COLS]


def export(source: pathlib.Path, out_dir: pathlib.Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    xl = pd.ExcelFile(source)

    frames = []
    for sheet, rtype in SHEET_MAP.items():
        if sheet in xl.sheet_names:
            df = load_sheet(xl, sheet, rtype)
            frames.append(df)
            csv_path = out_dir / f"{sheet}.csv"
            df.to_csv(csv_path, index=False)
            print(f"  ✓ {csv_path}  ({len(df)} rows)")
        else:
            print(f"  ⚠  Sheet '{sheet}' not found in XLSX. Skipping.")

    if not frames:
        raise SystemExit("No sheets found. Nothing exported.")

    all_df = pd.concat(frames, ignore_index=True)
    all_csv = out_dir / "all_resources.csv"
    all_df.to_csv(all_csv, index=False)
    print(f"  ✓ {all_csv}  ({len(all_df)} rows total)")

    # Parquet - apply types
    typed = all_df.copy()
    typed["year"]      = pd.to_numeric(typed["year"], errors="coerce").astype("Int64")
    typed["price_usd"] = pd.to_numeric(typed["price_usd"], errors="coerce").astype("float32")
    typed["is_free"]   = typed["is_free"].map({
        "True": True, "False": False, "TRUE": True, "FALSE": False, "true": True, "false": False
    })

    # Explicit Arrow schema avoids `large_string` (which the HF dataset viewer
    # sometimes rejects) and pins `year` to int64 to match the YAML dataset card.
    schema = pa.schema([
        ("resource_id",     pa.string()),
        ("resource_type",   pa.string()),
        ("title",           pa.string()),
        ("creator",         pa.string()),
        ("year",            pa.int64()),
        ("disciplines",     pa.string()),
        ("technique_tags",  pa.string()),
        ("skill_level_min", pa.string()),
        ("skill_level_max", pa.string()),
        ("is_free",         pa.bool_()),
        ("price_usd",       pa.float32()),
        ("url",             pa.string()),
        ("isbn",            pa.string()),
        ("language",        pa.string()),
        ("country",         pa.string()),
        ("description",     pa.string()),
        ("date_added",      pa.string()),
        ("last_verified",   pa.string()),
    ])

    pq_path = out_dir / "all_resources.parquet"
    table = pa.Table.from_pandas(typed, schema=schema, preserve_index=False)
    pq.write_table(table, pq_path, compression="snappy")
    print(f"  ✓ {pq_path}  (snappy-compressed)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export XLSX → CSV + Parquet")
    parser.add_argument("--source", default="source/climbing_resources_database.xlsx")
    parser.add_argument("--out",    default="data")
    args = parser.parse_args()

    source = pathlib.Path(args.source)
    out_dir = pathlib.Path(args.out)

    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    print(f"Exporting {source} → {out_dir}/")
    export(source, out_dir)
    print("Done.")


if __name__ == "__main__":
    main()
