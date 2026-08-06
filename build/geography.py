"""
build/geography.py
-------------------
STEP 1 of the pipeline: build the canonical LA -> ITL2 concordance (the "spine").
Every other variable in the panel joins onto this, so it comes first.

Boundary vintage: ITL2 2025 (chosen for alignment with Combined/Mayoral authorities
and comparability with current ONS outputs). One frozen vintage, many data years.

Input file (already downloaded):
    raw/geography/LAD_(April_2025)_to_LAU1_to_ITL3_to_ITL2_to_ITL1_(January_2025)_Lookup_in_the_UK.csv

Run from the project root:
    python build/geography.py
"""

import re
import pandas as pd
from pathlib import Path

RAW = Path("raw/geography/LAD_(April_2025)_to_LAU1_to_ITL3_to_ITL2_to_ITL1_(January_2025)_Lookup_in_the_UK.csv")
OUT = Path("clean/geography_spine.csv")

# --- 1. load the raw lookup -------------------------------------------------
# utf-8-sig strips the invisible "BOM" character ONS files sometimes put at the
# very start, which would otherwise corrupt the first column name.
df = pd.read_csv(RAW, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

print("Columns found in the file:")
for c in df.columns:
    print("   ", c)
print()

# --- 2. find the right columns automatically --------------------------------
# ONS names columns like LAD25CD (LA code) and ITL225CD / ITL225NM (ITL2 code/name).
# This matches them whatever the two-digit year is, so it keeps working next revision.
def find_col(level, suffix):
    for c in df.columns:
        if re.fullmatch(rf"{level}\d*{suffix}", c, flags=re.IGNORECASE):
            return c
    return None

LA_CODE   = find_col("LAD",  "CD")
ITL2_CODE = find_col("ITL2", "CD")
ITL2_NAME = find_col("ITL2", "NM")

# If auto-detection can't find one, stop clearly instead of failing cryptically.
# (Look at the printed column list above and set these three by hand if needed.)
# LA_CODE   = "LAD25CD"
# ITL2_CODE = "ITL225CD"
# ITL2_NAME = "ITL225NM"
missing = [name for name, val in
           [("LA code", LA_CODE), ("ITL2 code", ITL2_CODE), ("ITL2 name", ITL2_NAME)] if val is None]
if missing:
    raise SystemExit(
        f"Could not auto-detect these column(s): {', '.join(missing)}.\n"
        f"Look at the column list printed above, then set LA_CODE / ITL2_CODE / "
        f"ITL2_NAME by hand near the top of the script."
    )

print(f"Using columns -> LA: {LA_CODE} | ITL2 code: {ITL2_CODE} | ITL2 name: {ITL2_NAME}\n")

# --- 3. build the spine -----------------------------------------------------
spine = (
    df[[LA_CODE, ITL2_CODE, ITL2_NAME]]
    .drop_duplicates()
    .rename(columns={LA_CODE: "la_code", ITL2_CODE: "itl2_code", ITL2_NAME: "itl2_name"})
    .sort_values(["itl2_code", "la_code"])
    .reset_index(drop=True)
)

OUT.parent.mkdir(parents=True, exist_ok=True)
spine.to_csv(OUT, index=False)

# --- 4. your win: a quick summary ------------------------------------------
print(f"Spine built: {spine['la_code'].nunique()} local authorities "
      f"-> {spine['itl2_code'].nunique()} ITL2 regions")
print(f"Saved to: {OUT}")