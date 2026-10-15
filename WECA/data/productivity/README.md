# Productivity

| File | Geography | Coverage | Notes |
|---|---|---|---|
| `lad_productivity_index_2004_2023.csv` | **LAD** (362 rows — all England/Scotland/Wales/NI, plus `UKX`=UK total) | Wide, `Index_2004`...`Index_2023` | **New extraction** built for this bundle from `data/raw/productivity/ons_lad_productivity_2025edition.xls`, sheet `A1` ("Current Price (smoothed) GVA per hour worked indices"). UK=100. This is the only true LAD-level, multi-year productivity series in the bundle — everything else here is MSA/snapshot level. |
| `lad_productivity_vs_workplace_pay_2023.csv` | LAD (164 English LADs, MSA set only) | 2023 | LAD-level `productivity` (index) vs `median_hourly` workplace pay, plus a fitted `predicted_wage`/`residual` (pay vs what productivity alone would predict). Already carries full MSA membership columns. |
| `msa_productivity_2023.csv` | MSA (21) | 2023 | `productivity_index` by MSA with `lad_min/lad_max/n_lads` — the spread of its constituent LADs. |
| `msa_productivity_level_vs_range.csv` | MSA (21) | 2023 | Same idea, `median_productivity` + `range` (max-min) instead of index/min/max. |

**WECA**: filter `lad_productivity_index_2004_2023.csv` on `LAD_Code` in
`{E06000022, E06000023, E06000025}` (BANES, Bristol, South Gloucestershire
— see `../../geographic_lookup/lad_to_msa_county_itl.csv`). The other
three files already carry `msa_name`/`msa_abbrev == "WECA"` directly.

## Method note

`Index_2004`...`Index_2023` are ONS's own smoothed (5-year weighted
moving average) current-price GVA-per-hour indices, UK=100 — not raw
GVA/hour in £. Smoothing means a given year's figure also reflects
neighbouring years; don't read a single year in isolation as "that year's"
productivity shock.
