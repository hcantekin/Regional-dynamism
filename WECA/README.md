# WECA analysis bundle

Everything needed to do analysis on WECA (West of England, `msa_abbrev`
`WECA`, `msa_name` "West of England") specifically: a standalone
geographic lookup for converting any UK geography into MSA/WECA level,
plus every indicator this project holds, at whichever geography it
already exists in (mostly LAD), **for all 21 MSAs and comparators** —
not pre-filtered to WECA, since WECA-specific analysis needs something to
compare against.

Data only at this stage — no charts, no workbooks. Each subfolder has
its own README with per-file geography, coverage and caveats; this file
is the index.

## WECA's 3 local authorities

| LAD name | LAD code |
|---|---|
| Bath and North East Somerset | E06000022 |
| Bristol, City of | E06000023 |
| South Gloucestershire | E06000025 |

All three are unitary authorities (no lower tier underneath them), so
LAD = UTLA for WECA specifically — but don't assume that generalises to
other MSAs when extending this bundle.

## Folders

- **`geographic_lookup/`** — the full chain, OA → LSOA → MSOA → LAD → MSA,
  plus LAD → County/UTLA and LAD → ITL1/2/3, and a postcode-district
  shortcut. Start here if you just need to find out which small areas are
  "in WECA," or to join a new dataset onto this project's MSA structure.
  Fully documented in its own README — in short, everything hinges on the
  `lad_code` column, and `lad_to_msa_county_itl.csv` is the one file most
  other joins go through.

- **`data/`** — one subfolder per indicator area, each a separate CSV per
  table (not one giant combined file), each with its own README:
  - `gva/` — GVA per hour/total, by MSA (1998-2023) and by devolution tier.
  - `productivity/` — GVA/hour index, **LAD-level 2004-2023 time series**
    (new extraction for this bundle) plus MSA snapshots and pay comparison.
  - `pay/` — ASHE median hourly pay (residence basis), MSA and **LAD**
    level, 2025 and 2023-25 pooled, with percentile breakdowns.
  - `rurality_population/` — % population in a rural LSOA, land area,
    by MSA.
  - `travel_to_work/` — Census 2021 mode of travel to work, **LAD-level**
    full mode-share breakdown (new extraction) plus MSA PT-vs-rurality.
  - `finance/` — MSA-level revenue/expenditure, 2024-25.
  - `health/` — healthy life expectancy vs productivity, UTLA level.
  - `deprivation/` — IMD 2025, **LAD-level summary** (new extraction) plus
    MSA-level LSOA-decile composition.
  - `migration_qualification/` — migrant concentration & % higher
    education, LAD level, 2021.

## What's covered vs explicitly excluded

Per project scope: **UK sub-national indicators only**. Two datasets that
exist elsewhere in the project are deliberately **not** in this bundle
because they have no WECA-specific cut:
- OECD wages vs subnational tax devolution (country-level comparison).
- UK long-term sickness/economic inactivity (UK-wide time series, no
  sub-national breakdown).

Also excluded, as superseded/out of scope (see each subfolder's README
for the full reasoning):
- `msa_waldorf_irr.csv` and two related files — an earlier, exploratory
  rurality index superseded by the validated table that's bundled instead.
- `data/raw/agri/` (CAP agricultural subsidy data) — unrelated to this
  indicator set.
- The two large raw LAD/ITL3-level GVA source files (268MB + 3.4MB) —
  flagged in `data/gva/README.md` with their location, not extracted
  further for this compilation.

## Time coverage

Full available time series was pulled where it exists, not just the
headline years used in the project's published charts — e.g. GVA back to
1998, the new productivity extraction back to 2004. Single-year files
(pay, finance, deprivation, migration) reflect the only year(s) published
at that geography.

## Sharing this with a colleague or another Claude session

The `geographic_lookup/` folder is self-contained and sufficient on its
own for "how do I convert geography X to MSA/WECA level" questions — it
doesn't depend on anything in `data/`. The `data/` folder depends on
`geographic_lookup/` only insofar as most indicator files already carry
their own `msa_code`/`lad_code` columns pre-joined; use the lookup folder
if you need to join something *new* on, or need the County/ITL mapping.
