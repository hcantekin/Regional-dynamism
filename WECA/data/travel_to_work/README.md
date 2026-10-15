# Travel to work

ONS Census 2021, method of travel to work (NOMIS dataset `NM_2078_1`).

| File | Geography | Notes |
|---|---|---|
| `lad_travel_to_work_mode_share.csv` | **LAD** (164 x 6 modes = 984 rows) | **New extraction** built for this bundle, pulled live from NOMIS. One row per LAD x mode (`Public transport, Cycling, Walking, Car, Other, Work from home`). `count` is the raw commuter count; `share_of_commuters` excludes work-from-home from the denominator (null for the work-from-home row itself); `share_of_all_employed` includes it (this is the only share defined for work-from-home). Carries full MSA membership columns. |
| `msa_public_transport_vs_rurality.csv` | MSA (21) | `pct_public_transport` (share of commuters) vs `pct_pop_rural`, the table behind the PT-vs-rurality scatter chart. |

**WECA**: filter `lad_code` in `{E06000022, E06000023, E06000025}` on the
LAD file, or `msa_abbrev == "WECA"` on the MSA file.

## Integrity check

The LAD extraction's bucketed mode counts were checked to sum back to
NOMIS's own published "all categories" total for every LAD before saving
(max discrepancy < 1) — see the build note in this bundle's parent repo
(`hannah_c_charts/02_travel_to_work_by_msa/build_chart.py`) for the same
check applied at MSA level.

## Caveat

**2021 Census fieldwork fell during COVID-19 restrictions**, so public
transport and active travel shares are likely depressed relative to a
normal year — treat as indicative, not current behaviour.

## Not bundled

Live pull only — no bundled CSV, so re-running the extraction script
later will get whatever NOMIS currently serves (this is a fixed Census
year, so it shouldn't change, but pulling live avoids a stale copy
drifting from the source).
