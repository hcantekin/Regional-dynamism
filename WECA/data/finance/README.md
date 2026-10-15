# Finance

| File | Geography | Notes |
|---|---|---|
| `msa_finance_2024_25.csv` | MSA (21) | `expenditure, income, grants, local, other, grant_share` (£m) — MSA-level revenue/expenditure for 2024-25, split by funding source (central grants vs locally-raised vs other), plus `grant_share` as a dependency-on-central-funding measure. |

**WECA**: `msa_name == "West of England"` (no `msa_abbrev` column — join
against `../../geographic_lookup/msa_registry.csv` if needed).

## Not bundled

No LAD-level finance breakdown is included — this is an MSA/combined
authority-level budget, not something that decomposes to constituent LADs
(combined authority funding, by definition, sits at the CA level).
