# Deprivation

Indices of Multiple Deprivation, 2025 edition (IoD2025).

| File | Geography | Notes |
|---|---|---|
| `lad_imd_2025_summary.csv` | **LAD** (296, England only) | **New extraction** built for this bundle from `data/raw/imd/File_10_-_IoD2025_Local_Authority_District_Summaries__lower-tier__v2.xlsx`, sheet `IMD`. Columns: `imd_average_rank/score` (+ rank-of columns), `imd_pct_lsoas_most_deprived_decile` (+ rank), `imd_extent`, `imd_local_concentration` (+ ranks). Lower rank numbers = more deprived throughout. Zero missing matches checked against the project's `lad_code` (Barnsley/Sheffield pre-reissue vintage). |
| `msa_imd_ranks.csv` | MSA (21) | LSOA-decile composition per MSA: `pct_decile_1`...`pct_decile_10` (share of each MSA's LSOAs falling in each national IMD decile), plus `imd_avg_rank/median_rank`, `pct_decile_1_2`/`pct_decile_9_10` (most/least deprived quintile shares), `n_lsoas_decile1/2`. |

**WECA**: filter `lad_code` in `{E06000022, E06000023, E06000025}` on the
LAD file, or `msa_name == "West of England"` on the MSA file (no
`msa_abbrev` column there).

## Not bundled

Two larger raw IMD source files exist but weren't extracted into this
bundle — `File_10`'s LAD summary above is the practical, already-clean
extraction target:
- `data/raw/imd/File_7_IoD2025_All_Ranks_Scores_Deciles_Population_Denominators.csv` — full LSOA-level ranks/scores/deciles for all ~33,000 English LSOAs across all 7 IMD domains (Income, Employment, Education, Health, Crime, Barriers, Living, plus IDACI/IDAOPI) — this is the ultimate source `msa_imd_ranks.csv` is built from.
- `data/raw/imd/IMD_2025_data.csv` — a flatter raw dump of the same.

If you need a specific domain (e.g. Income deprivation only) at LAD
level, ask — `File_10` has one sheet per domain, same structure as `IMD`.
