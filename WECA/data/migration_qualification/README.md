# Migration & qualification

| File | Geography | Notes |
|---|---|---|
| `migration_qualification_lad_2021.csv` | **LAD** | `migration_concentration` (an index of migrant concentration, 2021), `pct_higher_ed` (% with higher education qualifications), `country` (England/Wales/Scotland/NI — this file has UK-wide coverage, not just the 164 MSA-set LADs). |

**WECA**: filter `lad_code` in `{E06000022, E06000023, E06000025}`.

## Not bundled

No MSA-level aggregate of this file exists elsewhere in the project — if
you need it rolled up to MSA, join on `lad_code` via
`../../geographic_lookup/lad_to_msa_county_itl.csv` and aggregate
yourself (decide a population or jobs weighting — none is pre-computed
here).
