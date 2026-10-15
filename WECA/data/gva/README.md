# GVA

| File | Geography | Coverage | Notes |
|---|---|---|---|
| `msa_gva_ranks_all21.csv` | MSA (21) | `gva_ph_1998`...`gva_ph_2023` wide time series | GVA per hour by MSA, pop-weighted across each MSA's constituent ITL3 areas (`n_itl3`, `method` columns show how many/which basis). Also carries `gva_index_eng` (England=100) and `rank_gva_ph`. The richest GVA file — start here. |
| `msa_gva_lad_timeseries.csv` | MSA (named `msa_name` despite the filename — not LAD-level) | Long format, `year` 1998+ | `gva_total_m`, i.e. total current-price GVA (£m), not per-head/per-hour. |
| `msa_gva_lad_2018.csv` | MSA (named `msa_name` despite the filename) | Single year, 2018 | Snapshot: `gva_total_m, pop_2018, gva_ph, gva_index, rank`. |
| `msa_gva_index_by_tier.csv` | Devolution tier (Established/Existing/Planned), not MSA | `year` time series | GVA/hour aggregated across all MSAs *within a tier*, England-indexed. Useful for "do Established MSAs out-produce Planned ones" questions. |
| `msa_maturity_gva.csv` | MSA (21) | Same wide `gva_ph_*` series as `msa_gva_ranks_all21.csv` | Adds `inception_year, maturity_years, n_lads` — GVA performance against how long the MSA has existed as a devolved body. |

**WECA**: `msa_abbrev == "WECA"` / `msa_name == "West of England"` in the
first and last files; `msa_name == "West of England"` in the others
(no `msa_abbrev` column there — join via
`../../geographic_lookup/msa_registry.csv` if you need the abbreviation).

## Not bundled

True LAD/ITL3-level GVA (the actual source these MSA aggregates are built
from) lives in two large raw ONS files, not copied into this bundle:
- `data/raw/gva/gva-by-industry-by-local-authority-time-series-v1.csv` (268MB)
- `data/raw/gva/regionalgrossvalueaddedbalancedperheadandincomecomponents.xlsx` (3.4MB)

If you need GVA at LAD level specifically (rather than MSA-aggregated),
ask for an extraction from these — it wasn't pulled for this compilation
as it's a much bigger job than the rest of this bundle.
