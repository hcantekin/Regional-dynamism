# Pay

ONS ASHE (Annual Survey of Hours and Earnings), place of **residence**
basis (Table 8), median gross hourly pay. All quantile-pooled across each
MSA's constituent LADs (not a simple average of LAD medians — see method
note below).

| File | Geography | Years | Notes |
|---|---|---|---|
| `msa_hourly_pay_2025.csv` | MSA (21) | 2025 | `median_hourly, jobs_k, lad_min, lad_max, n_lads, rank`. |
| `msa_hourly_pay_2025only.csv` | MSA (21) | 2025 only | Adds `se, ci_lo, ci_hi` (sampling uncertainty from quantile pooling). |
| `msa_hourly_pay_pooled_2023_25.csv` | MSA (21) | 2023-25 pooled | Same columns as above, pooled across 3 years for a larger effective sample / tighter CI. |
| `msa_lad_hourly_pay_2025.csv` | **LAD** (164) | 2025 | LAD-level `median_hourly` + full MSA membership columns — no percentile breakdown. |
| `msa_lad_hourly_pay_2025only.csv` | **LAD** (164) | 2025 only | Adds the full percentile set (`p10...p75`), `median_cv`, `se`. |
| `msa_lad_hourly_pay_pooled_2023_25.csv` | **LAD** (164) | 2023-25 pooled, `n_years` | Same percentile set, pooled across years. |

**WECA**: `msa_abbrev == "WECA"`, or at LAD level filter `lad_code` in
`{E06000022, E06000023, E06000025}`.

## Method note

Averaging published LAD medians directly is biased (a median isn't a
linear statistic) — checked, it overstates England's true median by
~£0.33. These files instead reconstruct each LAD's pay distribution from
its published percentile points, pool those distributions across an MSA's
constituent LADs, and read the weighted median off the pooled result
(residual bias ~-£0.02 vs the ONS-published England figure). Full
methodology in `../../../hannah_c_charts/04_hourly_pay_distribution_2025/README.md`.
