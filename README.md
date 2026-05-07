---
# ── HuggingFace Dataset Card ─────────────────────────────────────────────────
annotations_creators:
  - expert-generated
language:
  - en
license: cc-by-4.0
multilinguality:
  - monolingual
size_categories:
  - n<1K
source_datasets:
  - original
task_categories:
  - other
task_ids: []
pretty_name: Climbing Movement & Technique Resources
tags:
  - climbing
  - rock-climbing
  - technique
  - training
  - books
  - youtube
  - courses
  - podcasts
  - curated-dataset
dataset_info:
  features:
    - name: resource_id
      dtype: string
    - name: resource_type
      dtype: string
    - name: title
      dtype: string
    - name: creator
      dtype: string
    - name: year
      dtype: int32
    - name: disciplines
      dtype: string
    - name: technique_tags
      dtype: string
    - name: skill_level_min
      dtype: string
    - name: skill_level_max
      dtype: string
    - name: is_free
      dtype: bool
    - name: price_usd
      dtype: float32
    - name: url
      dtype: string
    - name: isbn
      dtype: string
    - name: language
      dtype: string
    - name: country
      dtype: string
    - name: description
      dtype: string
    - name: date_added
      dtype: string
    - name: last_verified
      dtype: string
  splits:
    - name: train
      num_examples: 114
---

# Climbing Movement & Technique Resources

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Validate & Export](https://github.com/timothy22000/climbing-resources-db/actions/workflows/validate-pr.yml/badge.svg)](https://github.com/timothy22000/climbing-resources-db/actions/workflows/validate-pr.yml)
[![URL Health](https://github.com/timothy22000/climbing-resources-db/actions/workflows/url-checker.yml/badge.svg)](https://github.com/timothy22000/climbing-resources-db/actions/workflows/url-checker.yml)

A curated, open-source database of **114 resources** covering books, YouTube channels, online courses, websites/blogs, and podcasts, focused on **rock climbing movement and technique**. Every entry has been manually selected and verified, with book ISBNs cross-referenced against Amazon, AbeBooks, and publisher catalogues.

Covers all major disciplines: sport/lead, bouldering, trad, and top rope. Skill levels span complete beginner to elite. Every entry carries a 33-topic technique taxonomy so you can filter precisely for what you need.

---

## Why I built this

I wanted one place to search for climbing resources. Recommendations for specific techniques (heel hooks, drop knees, crack jamming) were scattered across YouTube comments, gym chat, and Reddit threads, with nothing I could actually filter or query. So I built it: a single tagged file I can grep to find every resource that matches what I'm working on right now.

---

## At a Glance

| Category          |  Count | Free | % Free | Notes                                                    |
| :---------------- | -----: | :--: | :----: | :------------------------------------------------------- |
| Books             |     30 |  n/a |   n/a  | Publication span 1993 to 2024; every ISBN-13 verified    |
| YouTube channels  |     25 |   25 |  100%  | All verified active                                      |
| Online courses    |     20 |    1 |    5%  | Altitude Climbing, TrainingBeta, Power Company, et al.   |
| Websites & blogs  |     20 |   10 |   50%  | Mix of free articles and paid training programmes        |
| Podcasts          |     19 |   17 |   89%  | Verified on Spotify                                      |
| **Total**         | **114** | **53** | **46%** |                                                       |

---

## Schema

Each row in `all_resources.csv` / `all_resources.parquet` contains 18 fields:

| Field | Type | Description |
|---|---|---|
| `resource_id` | string | Stable ID, e.g. `BK-001`, `YT-012`, `CR-005` |
| `resource_type` | string | `book` · `youtube` · `course` · `website` · `podcast` |
| `title` | string | Full title |
| `creator` | string | Author(s), channel name, or instructor |
| `year` | int | Year of publication or channel launch |
| `disciplines` | string | Pipe-separated: `sport` · `bouldering` · `trad` · `top_rope` · `all` |
| `technique_tags` | string | Pipe-separated tags from the 25-topic taxonomy |
| `skill_level_min` | string | `beginner` · `intermediate` · `advanced` · `elite` |
| `skill_level_max` | string | Same enum as `skill_level_min` |
| `is_free` | bool | Whether the resource is freely accessible |
| `price_usd` | float | Approximate price in USD (null if free or variable) |
| `url` | string | Primary URL |
| `isbn` | string | ISBN-13 (books only; all manually verified) |
| `language` | string | ISO 639-1 language code |
| `country` | string | Country of origin |
| `description` | string | 1–3 sentence editorial description |
| `date_added` | string | ISO 8601 date the entry was added |
| `last_verified` | string | ISO 8601 date the entry was last checked |

### Technique Tag Taxonomy (33 topics)

**Movement positions & body mechanics:**
`footwork` · `hip_rotation` · `drop_knee` · `flagging` · `heel_hooks` · `toe_hooks` · `knee_bars`

**Hold shapes:**
`crimp_grip` · `slopers` · `pinches` · `underclings` · `jugs` · `pockets` · `edges`

**Grip variants (crimp sub-types):**
`half_crimp` · `full_crimp` · `finger_drag`

**Hold orientations:**
`gastons` · `side_pulls`

**Route / terrain types:**
`slab` · `overhang` · `crack_climbing` · `offwidth`

**Movement quality:**
`dynamic_movement` · `route_reading` · `strength`

**Technical gear skills:**
`gear_placement` · `anchors`

**Training methods:**
`finger_training` · `periodization`

**Mental & rehabilitation:**
`mental_game` · `lead_falling` · `injury_rehab`

---

## Repository Layout

```
climbing-resources-db/
├── README.md                     # This file + HuggingFace dataset card
├── LICENSE                       # CC BY 4.0
├── CONTRIBUTING.md               # How to add or fix entries
├── CHANGELOG.md                  # Version history
├── data/
│   ├── all_resources.csv         # Unified flat table (primary file)
│   ├── all_resources.parquet     # Snappy-compressed, typed (HF viewer-ready)
│   ├── books.csv
│   ├── youtube.csv
│   ├── courses.csv
│   ├── websites.csv
│   └── podcasts.csv
├── source/
│   └── climbing_resources_database.xlsx
├── scripts/
│   ├── export_csv.py             # XLSX → CSV + Parquet export
│   ├── validate.py               # CI validation script
│   └── check_urls.py             # Parallel URL health checker
└── .github/
    ├── workflows/
    │   ├── validate-pr.yml       # Schema validation on every PR
    │   ├── url-checker.yml       # Weekly URL health check
    │   └── export.yml            # Auto-regenerate CSVs on push to main
    └── ISSUE_TEMPLATE/
        ├── add_resource.md
        └── fix_data.md
```

---

## Quick Start

```python
import pandas as pd

# CSV
df = pd.read_csv("data/all_resources.csv")

# Parquet (faster, typed)
df = pd.read_parquet("data/all_resources.parquet")

# All free resources tagged with footwork
free_footwork = df[
    (df["is_free"] == True) &
    (df["technique_tags"].str.contains("footwork"))
]

# Books for beginner–intermediate bouldering
bouldering_books = df[
    (df["resource_type"] == "book") &
    (df["disciplines"].str.contains("bouldering")) &
    (df["skill_level_min"] == "beginner")
]

# Everything covering crack technique, sorted by year
cracks = df[df["technique_tags"].str.contains("crack_technique")].sort_values("year")
```

### Load from HuggingFace

```python
from datasets import load_dataset
ds = load_dataset("t22000t/climbing-resources-db")
df = ds["train"].to_pandas()
```

---

## Highlighted Resources

**Books:** The Self-Coached Climber (Hague & Hunter, 2006), The Climbing Bible (Mobråten & Christophersen, 2020), 9 Out of 10 Climbers Make the Same Mistakes (Dave MacLeod, 2009), Smooth (Xian Goh, 2024), Crack Climbing: The Definitive Guide (Pete Whittaker, 2020), Performance Rock Climbing (Goddard & Neumann, 1993).

**YouTube:** Hooper's Beta, Lattice Training, Neil Gresham Masterclass, Wide Boyz, Movement for Climbers, Hannah Morris, Catalyst Climbing.

**Courses:** Dave MacLeod's Technique Course (Altitude Climbing), Fear of Falling (Hazel Findlay), Wide Boyz Global Crack School, Bouldering Blueprint (Magnus Midtbø).

**Podcasts:** The Nugget, TrainingBeta, Power Company, Careless Talk (Aidan Roberts), Climbing Gold (Alex Honnold), Circle Up! (Kyra Condie).

---

## Data Quality & Verification

All 30 book ISBNs were manually verified against Amazon, AbeBooks, publisher websites, and library catalogues. During the initial verification pass: 13 ISBNs were corrected (the Climbing Bible series had systematic ISBN errors; several Falcon Guides had wrong edition numbers), and 6 entries were removed as unverifiable or fabricated. YouTube channels and podcasts were verified as active; online courses were confirmed available on their respective platforms. URL health checks run automatically on a weekly schedule.

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Use the issue templates to suggest new resources or report data errors. Selection criteria: the resource must focus substantially on **movement and technique**, must be currently available, and books must have a verifiable ISBN.

---

## Citation

```bibtex
@dataset{climbing_resources_db_2026,
  title   = {Climbing Movement \& Technique Resources},
  year    = {2026},
  url     = {https://github.com/timothy22000/climbing-resources-db},
  license = {CC BY 4.0},
  note    = {Curated open dataset of 114 rock climbing technique resources.},
}
```

---

## Licence

[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE). You are free to share and adapt the data for any purpose, provided you give appropriate credit and indicate any changes made.

---

## Limitations & Bias

Coverage is weighted toward English-language resources from the US and UK. Non-English content (French, German, Spanish) is under-represented. YouTube and podcast links can break without notice; the weekly URL checker mitigates but does not eliminate stale entries. Resource selection involves editorial judgement and may under-represent creators with smaller audiences. Prices are approximate at the time of verification. Mobile apps (Crimpd, Mountain Project) and print magazines are out of scope for this version.
