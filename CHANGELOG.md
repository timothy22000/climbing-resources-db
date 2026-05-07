# Changelog

All notable changes to this dataset are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
`MAJOR.MINOR.PATCH` where MAJOR = breaking schema change, MINOR = new entries, PATCH = data corrections.

---

## [1.0.0] 2026-05-07

Initial public release.

### Added

**114 resources across 5 categories:**

- 30 books (1993–2024), all with verified ISBN-13s
- 25 YouTube channels, all verified as active
- 20 online courses across Altitude Climbing, TrainingBeta, Power Company, and others
- 20 websites and blogs including Lattice Training, Climb Strong, and Dave MacLeod's blog
- 19 podcasts verified against Spotify

**Infrastructure:**
- Unified 18-column schema with controlled vocabularies for `resource_type`, `disciplines`, `technique_tags`, `skill_level_min`, `skill_level_max`, and `is_free`.
- 25-topic technique tag taxonomy.
- Per-type CSV views (`books.csv`, `youtube.csv`, `courses.csv`, `websites.csv`, `podcasts.csv`).
- Snappy-compressed Parquet file (`all_resources.parquet`) for HuggingFace viewer compatibility.
- Master XLSX source with 6 sheets including a Topic Coverage Map.
- GitHub Actions: `validate-pr.yml`, `url-checker.yml`, `export.yml`.
- Issue templates: `add_resource.md`, `fix_data.md`.

### Data Quality Work (pre-release)

During ISBN verification against Amazon, AbeBooks, and publisher catalogues, 13 ISBNs were corrected and 6 entries were removed:

**ISBNs corrected:**
- BK-015 Make or Break: `978-0956428110` → `978-0956428134`
- BK-017 The Trad Climber's Bible: `978-0762787272` → `978-0762783724`
- BK-018 AMGA Single Pitch Manual: `978-1493015023` → `978-0762790043`
- BK-019 Logical Progression: `978-1495201530` → `978-1544119533` (old ISBN belonged to a different Bechtel book)
- BK-020 The Climbing Bible: `978-1839810077` → `978-1912560707`
- BK-022 Climbing: From Gym to Crag: `978-0898867466` → `978-0898866827`
- BK-025 Freedom of the Hills (9th ed.): `978-1594859625` → `978-1680510041`
- BK-030 High Exposure: `978-0684809953` → `978-0684853612` (also corrected: Salkeld is not a co-author)
- BK-033 The Climbing Bible: Practical Exercises: `978-1839810596` → `978-1839811043`
- BK-034 The Climbing Bible: Managing Injuries: `978-1839810961` → `978-1839812002`
- BK-035 Science of Climbing Training: placeholder → `978-1839811821`
- BK-036 Rock Climbing Technique (Kettle): `978-1906095901` → `978-1999654405`
- BK-024 Rock Climbing Technique (The Vertical Dimension): original ISBN belonged to a Yosemite guidebook

**Entries removed (unverifiable or fabricated):**
- *Climb! (The History and Techniques)* by "Blyth Wright" - no record found on any retailer or library catalogue
- *The Knot Bible* by "Alastair Sherwood" (Pesda Press) - no record found
- *Rock Climbing Technique (The Vertical Dimension)* by "John Gill" - title does not correspond to any known Gill publication
- *Trad Climber's Friend* by "Josh Hurst" (Helios) - no record found
- *On the Rocks* by "Ron Fawcett et al." (Oxford Illustrated Press, 1987) - ISBN could not be verified
- *The Art of Falling: A Memoir* by "Pamela Shaintall" - author name and title return no results on any platform; confirmed fabricated

---

## [1.1.0] 2026-05-07

### Added

**Technique taxonomy expanded from 25 to 33 tags.** Eight new tags added:

- **Hold shapes:** `jugs` (large positive holds), `pockets` (one/two/three-finger pockets), `edges` (small flat positive holds, distinct from crimps).
- **Grip variants (crimp sub-types):** `half_crimp`, `full_crimp`, `finger_drag`. Used for resources that distinguish grip mechanics, common in finger-training and physiology literature.
- **Hold orientations:** `gastons` (pulling outward), `side_pulls`. Match the orientation pattern of the existing `underclings` tag.

The change is backwards compatible: every existing tag still validates. Existing rows have been retagged where the resource clearly covers the new topic; rows are conservative additions only.

### Changed

- `scripts/validate.py`, `README.md` taxonomy section, `CONTRIBUTING.md` tag list, `CLAUDE.md` count reference all updated together.

---

## [Unreleased]

Planned for v1.2.0:
- Add non-English resources (French, German, Spanish).
- Add mobile app category (Crimpd, Mountain Project app, 8a.nu).
- Expand podcast coverage for non-English speaking markets.
