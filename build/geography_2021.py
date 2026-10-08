"""
build/geography_2021.py
-----------------------
The ITL2 **2021** version of the spine (41 regions), alongside the 2025 spine built by
build/geography.py. Needed because the job-flows data currently uses ITL2 2021 codes;
indicators that are produced for both boundary sets write their 2021 versions to
clean/itl2_2021/ with the same file names as clean/.

Input: ONS Open Geography Portal lookup "Local Authority District (April 2023) to LAU1 to
ITL3 to ITL2 to ITL1 (January 2021) Lookup in the UK" — downloaded once to raw/geography/.

Same rules as the 2025 spine: one row per LA (current codes, via the crosswalk); LAs split
across ITL2 are assigned wholly to the ITL2 where most residents live (SPLIT_RULE).

Run from the project root:  python build/geography_2021.py
"""

import json
import urllib.request
from pathlib import Path
import pandas as pd

RAW = Path("raw/geography/LAD_(April_2023)_to_LAU1_to_ITL3_to_ITL2_to_ITL1_(January_2021)_Lookup_in_the_UK.csv")
URL = ("https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
       "LAD23_LAU121_ITL321_ITL221_ITL121_UK_LU/FeatureServer/0/query?where=1%3D1&outFields=*&f=json")
CROSSWALK = Path("lib/la_code_crosswalk.csv")
SPINE_2025 = Path("clean/geography_spine.csv")
OUT = Path("clean/itl2_2021/geography_spine.csv")

SPLIT_RULE = {
    "S12000021": "TLM9",   # North Ayrshire: mainland (Southern Scotland); Arran & Cumbrae -> TLM6
    "S12000035": "TLM6",   # Argyll and Bute: islands + mainland (Highlands & Islands); Helensburgh & Lomond -> TLM8
}

# --- 1. download the lookup once -------------------------------------------
if not RAW.exists():
    feats = json.loads(urllib.request.urlopen(URL, timeout=120).read())["features"]
    pd.DataFrame([f["attributes"] for f in feats]).to_csv(RAW, index=False)
    print(f"Downloaded lookup -> {RAW}")
lu = pd.read_csv(RAW, dtype=str)

# --- 2. one row per LA, current LA codes ------------------------------------
remap = dict(zip(*[pd.read_csv(CROSSWALK, dtype=str)[c] for c in ("old_code", "new_code")]))
spine = (lu.rename(columns={"LAD23CD": "la_code", "ITL221CD": "itl2_code", "ITL221NM": "itl2_name"})
           [["la_code", "itl2_code", "itl2_name"]].drop_duplicates())
spine["la_code"] = spine.la_code.replace(remap)
spine = spine.drop_duplicates()

split = sorted(spine.loc[spine.la_code.duplicated(keep=False), "la_code"].unique())
unruled = sorted(set(split) - set(SPLIT_RULE))
if unruled:
    raise SystemExit(f"LA(s) split across ITL2 with no rule in SPLIT_RULE: {unruled}")
spine = spine[~spine.la_code.isin(split) | (spine.itl2_code == spine.la_code.map(SPLIT_RULE))]
spine = spine.sort_values(["itl2_code", "la_code"]).reset_index(drop=True)
assert spine.la_code.is_unique

# --- 3. checks: same LAs as the 2025 spine ----------------------------------
s25 = pd.read_csv(SPINE_2025)
diff = set(spine.la_code) ^ set(s25.la_code)
assert not diff, f"LA sets differ from the 2025 spine: {sorted(diff)}"

OUT.parent.mkdir(parents=True, exist_ok=True)
spine.to_csv(OUT, index=False)
print(f"Split LA(s) assigned by rule: { {la: SPLIT_RULE[la] for la in split} }")
print(f"2021 spine built: {spine.la_code.nunique()} local authorities -> {spine.itl2_code.nunique()} ITL2 (2021) regions")
print(f"Saved to: {OUT}")
