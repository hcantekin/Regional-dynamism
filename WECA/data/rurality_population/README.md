# Rurality & population

| File | Geography | Notes |
|---|---|---|
| `msa_rural_population_table.csv` | MSA (21) | `population, population_rural, pct_pop_rural, rurality_score` — % of population living in a rural LSOA (population-weighted, not a simple count of rural LSOAs). This is the validated rurality table used across the project's charts. |
| `msa_rural_urban_scores_all21.csv` | MSA (21) | Same `pct_pop_rural`/`pop_weighted_rurality_score` metric, with `msa_abbrev` and a rank column added. |
| `msa_land_area_km2.csv` | MSA (21) | `area_km2`, extracted from the MSA boundary GeoJSON (`data/raw/boundaries/geojson/strategic_authorities.geojson`) rather than bundling the full ~1.3MB boundary file. |

**WECA**: `msa_name == "West of England"` (no `msa_abbrev` column in
`msa_rural_population_table.csv` or `msa_land_area_km2.csv`; use
`msa_abbrev == "WECA"` in `msa_rural_urban_scores_all21.csv`, or join
against `../../geographic_lookup/msa_registry.csv`).

## Excluded as superseded

`data/processed/msa_waldorf_irr.csv`, `msa_rural_urban.csv` and
`msa_rurality_summary.csv` were an earlier, exploratory alternative
rurality index (an "IRR" composite of population, density, % urban, RUC
score and distance, normalised and combined several ways). They're
**not bundled here** — `msa_rural_population_table.csv` above is the
version that was validated and carried through into the project's
published charts. Ask if you specifically need the exploratory version.

## Not bundled

No population-only time series or small-area (LSOA-level) rurality table
is included — these files are MSA-level summaries only. If you need
LSOA-level rural/urban classification (RUC21) directly, ask for that
extraction separately.
