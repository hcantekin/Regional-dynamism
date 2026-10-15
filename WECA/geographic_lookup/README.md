# Geographic lookup — converting any UK geography to MSA / WECA level

Everything needed to take a figure at Output Area, LSOA, MSOA, local
authority, postcode, county or ITL level and roll it up to one of the 21
Mayoral Strategic Authorities (MSAs) — including WECA (West of England,
msa_abbrev `WECA`) — or down the other way, to find out which small areas
sit inside WECA.

No code required to use this — these are plain lookup tables, join them in
Excel/Power Query/pandas/R on the shared code columns described below.

## The chain

```
OA (Output Area, 2021)
  -> LSOA (2021)
    -> MSOA (2021)
      -> LAD (local authority district, Dec 2022 codes)
        -> MSA (21 Mayoral Strategic Authorities — project-specific)
        -> CTYUA (county / unitary authority, Dec 2024 codes)
        -> ITL3 -> ITL2 -> ITL1 (Jan 2025 codes)
```

LAD is the hinge point: every other geography in this project joins to
everything else *through* the LAD code. If you only have a postcode, use
`postcode_district_msa_lookup.csv` to jump straight to LAD/MSA without
going through OA/LSOA/MSOA at all.

## Files

- **`oa_lsoa_msoa_lad_lookup.csv`** (188,880 rows) — ONS's own OA to LSOA
  to MSOA to LAD (December 2021) lookup for England and Wales, unmodified.
  Columns: `OA21CD, LSOA21CD, LSOA21NM, LSOA21NMW, MSOA21CD, MSOA21NM,
  MSOA21NMW, LAD22CD, LAD22NM, LAD22NMW, ObjectId`. Use this to roll
  postcode/address-level or small-area data (e.g. deprivation, Census
  variables) up to LAD.

- **`lad_to_msa_county_itl.csv`** (164 rows, one per English local
  authority) — the master LAD-level table, this project's MSA crosswalk
  joined with ONS's county/unitary and ITL lookups. Columns:
  `msa_code, msa_abbrev, msa_name, tier, devolution_type, dpp_status,
  cauth_code, lad_code_original, lad_name, lad_code, CTYUA24CD, CTYUA24NM,
  ITL325CD, ITL325NM, ITL225CD, ITL225NM, ITL125CD, ITL125NM`.
  This is the file most indicator data in `WECA/data/` joins against on
  `lad_code`. **WECA is 3 rows**: Bath & North East Somerset, Bristol,
  City of, and South Gloucestershire.

- **`msa_registry.csv`** (21 rows, one per MSA) — the base MSA reference
  table: `msa_code, msa_abbrev, msa_name, tier, devolution_type,
  dpp_status, cauth_code, n_lads`. WECA's row: `msa_abbrev = WECA`,
  `msa_name = West of England`, `tier = Established`, `n_lads = 3`.

- **`postcode_district_msa_lookup.csv`** (2,323 rows) — postcode district
  (e.g. `BS1`, `BA1`) to LAD to MSA, for when the only geography you have
  is a postcode. **Caveat**: 1,040 of 2,323 rows have a blank `LAD25NM`/
  `msa_name` — these are postcode districts in areas outside the 164
  English LADs covered by this project's MSA set (e.g. London boroughs,
  which have their own GLA governance and aren't assigned to an MSA here).
  A blank doesn't mean the postcode doesn't exist; it means it falls
  outside this project's MSA coverage.

## Code-vintage notes (read this before joining on `lad_code`)

LAD boundaries and codes get reissued periodically, and not every ONS
lookup updates on the same schedule. This project's crosswalk
(`lad_code` / `lad_code_original`) deliberately uses the **pre-reissue**
Barnsley/Sheffield codes (`E08000016`/`E08000019`), matching the vintage
used by the OA-level lookup above. The county (Dec 2024) and ITL
(Jan 2025) lookups merged into `lad_to_msa_county_itl.csv` also use this
same vintage — checked when this file was built: **0 missing matches**
against either lookup, so a direct join on `lad_code` is safe to use
as-is. If you bring in a newer ONS file (e.g. 2025+ reissues) and get
unexpected non-matches, check for a code reissue first before assuming a
data error — this exact vintage mismatch has caused real bugs earlier in
this project.

Separately: Cumbria was reorganised into Westmorland and Furness /
Cumberland in 2023, and North Yorkshire/Somerset also went through
unitary reorganisations — none of these affect WECA's 3 constituent
authorities, but if you're extending this lookup to other MSAs, check
which vintage of LAD codes any new source table uses before joining.

## Typical joins

- **"What LAD is in WECA?"** → filter `lad_to_msa_county_itl.csv` on
  `msa_abbrev == "WECA"`, read off `lad_code`/`lad_name`.
- **"What MSA is this LSOA in?"** → join `oa_lsoa_msoa_lad_lookup.csv` on
  `LSOA21CD` to get `LAD22CD`, then join `lad_to_msa_county_itl.csv` on
  `lad_code == LAD22CD`.
- **"What MSA is this postcode district in?"** → look up directly in
  `postcode_district_msa_lookup.csv`.
- **"What ITL2/county is this MSA's GVA data reported against?"** →
  `lad_to_msa_county_itl.csv` already carries `ITL225NM`/`CTYUA24NM`
  alongside `msa_name`, no extra join needed.
