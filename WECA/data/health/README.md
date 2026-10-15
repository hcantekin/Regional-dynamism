# Health

| File | Geography | Notes |
|---|---|---|
| `england_utla_productivity_vs_hle.csv` | **UTLA/CTYUA** (upper-tier — County/Unitary Authority, not LAD) | `productivity` (index, same basis as `../productivity/lad_productivity_index_2004_2023.csv` but at upper-tier geography) vs `hle_male, hle_female, hle` (healthy life expectancy at birth, years). Carries both `CTYUA24CD/CTYUA24NM` and the source's own `Area code/Area name` (identical in practice — kept both as they came from the original build). |

**WECA**: BANES, Bristol, and South Gloucestershire are each their own
unitary authority, so unlike most other files here there's no single
"WECA" aggregate row — filter `CTYUA24CD` in `{E06000022, E06000023,
E06000025}` directly (these happen to be the same codes as the LAD codes,
since all three are unitary authorities with no lower tier).

## Note on geography level

This is the one file in the bundle at **UTLA level rather than LAD**
(healthy life expectancy is published by ONS at upper-tier only). For
WECA specifically this makes no difference — its three constituent
authorities are unitary (LAD = UTLA) — but don't assume that holds for
other MSAs with genuine two-tier structure underneath them.
