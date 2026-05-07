# Contributing to climbing-resources-db

Thank you for helping keep this database accurate and growing. All contributions are welcome: fixing a broken URL, correcting an ISBN, or adding a new book or course.

---

## Table of Contents

1. [Quick Ways to Contribute](#quick-ways-to-contribute)
2. [Selection Criteria](#selection-criteria)
3. [Adding a New Resource](#adding-a-new-resource)
4. [Fixing an Existing Entry](#fixing-an-existing-entry)
5. [Schema Reference](#schema-reference)
6. [Running Validation Locally](#running-validation-locally)
7. [Pull Request Checklist](#pull-request-checklist)
8. [Code of Conduct](#code-of-conduct)

---

## Quick Ways to Contribute

**No coding required:**
- Open an [Add Resource issue](../../issues/new?template=add_resource.md) to suggest a new entry.
- Open a [Fix Data issue](../../issues/new?template=fix_data.md) to report a wrong ISBN, broken URL, or incorrect field.

**With a pull request:**
- Edit the CSVs in `data/` directly. (A master XLSX in `source/` is planned for a future release; once it lands, `python scripts/export_csv.py` will regenerate the CSVs from it.)
- All PRs must pass the schema validation workflow before merging.

---

## Selection Criteria

A resource must meet **all** of the following to be included:

1. **Technique focus.** The resource must focus substantially on climbing movement, technique, or the mental skills directly tied to movement. Pure training volume programmes, gear reviews, expedition accounts, and guidebooks are out of scope.
2. **Currently available.** The resource must be obtainable or accessible right now: in print, in stock, or at an active URL.
3. **Verifiable.** Books must have a confirmed ISBN traceable to a real published edition. Courses and websites must have a working URL.
4. **Rock climbing disciplines.** The resource must cover at least one of: sport/lead, bouldering, trad, or top rope. Mountaineering, ice, and aid-only resources are generally excluded unless they have strong rock technique content.

Resources do **not** need to be free, English-language, or from a professional publisher. Self-published books and independent YouTube channels are welcome.

---

## Adding a New Resource

### Step 1 - Verify the resource

Before adding any entry, confirm:

- The URL is live and points directly to the resource (not a search result or affiliate redirect).
- For books: the ISBN is for the exact edition you are adding. Look it up on Amazon or AbeBooks and confirm the title, author, and edition match. Do not use placeholder or guessed ISBNs.
- For YouTube: the channel is active and primarily focused on technique (not a general vlog with occasional climbing content).

### Step 2 - Choose a resource_id

IDs follow the pattern `TYPE-NNN` where `TYPE` is `BK`, `YT`, `CR`, `WB`, or `PD` and `NNN` is the next sequential number in that category. Check the existing CSVs to find the current maximum.

### Step 3 - Fill all required fields

All of the following fields are required. See [Schema Reference](#schema-reference) for allowed values.

`resource_id`, `resource_type`, `title`, `creator`, `year`, `disciplines`, `technique_tags`, `skill_level_min`, `skill_level_max`, `is_free`, `url`, `language`, `country`, `description`, `date_added`, `last_verified`

For books, `isbn` is also required. For non-book resources, leave `isbn` blank.

`price_usd` is optional but encouraged for paid resources.

### Step 4 - Add the row

Edit `data/all_resources.csv` directly and add a matching row to the per-type CSV (`data/books.csv`, `data/youtube.csv`, etc.).

If a master XLSX exists at `source/climbing_resources_database.xlsx` (planned for a future release), edit the appropriate tab and run:

```bash
python scripts/export_csv.py
```

### Step 5 - Run validation

```bash
python scripts/validate.py
```

Fix any errors before opening your pull request.

---

## Fixing an Existing Entry

Common fixes:

- **Broken URL:** update `url` and set `last_verified` to today's date.
- **Wrong ISBN:** check Amazon/AbeBooks for the correct ISBN-13 for the exact edition listed.
- **Wrong technique tags:** add or remove tags from the 25-topic taxonomy.
- **Outdated price:** update `price_usd` and `last_verified`.

For any fix, update `last_verified` to today's date (`YYYY-MM-DD`).

---

## Schema Reference

### `resource_type`
`book` · `youtube` · `course` · `website` · `podcast`

### `disciplines`
Pipe-separated combination of: `sport` · `bouldering` · `trad` · `top_rope` · `all`

Use `all` only when the resource covers all four disciplines equally. Otherwise list the specific disciplines. Example: `sport|bouldering`.

### `technique_tags`
Pipe-separated tags chosen from the 25-topic taxonomy:

`footwork` · `hip_rotation` · `drop_knee` · `flagging` · `heel_hooks` · `toe_hooks` · `knee_bars` · `crimp_grip` · `slopers` · `pinches` · `underclings` · `slab` · `overhang` · `crack_climbing` · `offwidth` · `dynamic_movement` · `route_reading` · `strength` · `gear_placement` · `anchors` · `finger_training` · `periodization` · `mental_game` · `lead_falling` · `injury_rehab`

Add at least 2 and at most 10 tags per resource. Do not invent new tags; open an issue to propose an extension to the taxonomy if a topic is missing.

### `skill_level_min` / `skill_level_max`
`beginner` · `intermediate` · `advanced` · `elite`

`skill_level_min` is the lowest level that would find the resource useful. `skill_level_max` is the highest level that would still find it useful. A book like *The Self-Coached Climber* targets `intermediate` through `advanced`; a beginner YouTube channel might be `beginner` through `intermediate`.

### `is_free`
`True` if the resource is freely accessible without payment or subscription. `False` otherwise. YouTube channels are always `True`. A course behind a paywall is `False` even if it has a free preview.

### `isbn`
13-digit ISBN with hyphens: `978-XXXXXXXXXX`. Do not use ISBN-10. Verify against a reliable retailer before adding.

### `date_added` / `last_verified`
ISO 8601 format: `YYYY-MM-DD`.

---

## Running Validation Locally

```bash
# Install dependencies
pip install pandas pyarrow requests

# Validate schema
python scripts/validate.py

# Check URL health (slow; makes real HTTP requests)
python scripts/check_urls.py

# Regenerate CSVs and Parquet from the master XLSX
python scripts/export_csv.py
```

The validate script checks:

- All required fields are present and non-empty for every row.
- `resource_type`, `skill_level_min`, `skill_level_max`, `is_free`, `language` conform to their enums.
- All `technique_tags` values are from the approved 25-topic taxonomy.
- `disciplines` values are from the approved set.
- `isbn` fields match the pattern `\d{3}-\d{10}` (books only).
- No duplicate `resource_id` values.
- `date_added` and `last_verified` are valid ISO 8601 dates.
- URLs start with `https://`.

---

## Pull Request Checklist

Before opening a PR:

- [ ] `python scripts/validate.py` passes with zero errors.
- [ ] Any new book entry has an ISBN verified against Amazon or AbeBooks.
- [ ] `last_verified` is set to today's date for all changed or new rows.
- [ ] The PR title is descriptive (e.g. `Add: Smooth by Xian Goh (BK-031)` or `Fix: BK-015 ISBN correction`).
- [ ] The PR description explains what was added or changed and how it was verified.

---

## Code of Conduct

Be respectful. This project exists to help climbers find good learning resources. Reviews and discussions should focus on the accuracy and quality of the data, not on the person submitting it.
