"""
build/population.py
-------------------
SOURCE 2 -- and your first AUTOMATED pull: mid-year population estimates per local
authority from the Nomis API, summed to ITL2.

Why population first: it's a COUNT (aggregates by a simple sum), and ITL2 population
is the weight you'll reuse later to aggregate RATE variables correctly.

You provide ONE thing: the Nomis API CSV URL (see the chat for the 6 clicks to get it).
Paste it into NOMIS_URL below, then run from the project root:
    python build/population.py

Needs nothing extra installed -- pandas (already in 'charts') and urllib (built in).
"""

import urllib.request
from datetime import date
from pathlib import Path
import pandas as pd

# --- paste the URL from the Nomis query builder between the quotes -----------
NOMIS_URL = "https://www.nomisweb.co.uk/api/v01/dataset/NM_2002_1.data.csv?geography=1778384897...1778384901,1778384941,1778384950,1778385143...1778385146,1778385159,1778384902...1778384905,1778384942,1778384943,1778384956,1778384957,1778385033...1778385044,1778385124...1778385138,1778384906...1778384910,1778384958,1778385139...1778385142,1778385154...1778385158,1778384911...1778384914,1778384954,1778384955,1778384965...1778384972,1778385045...1778385058,1778385066...1778385072,1778384915...1778384917,1778384944,1778385078...1778385085,1778385100...1778385104,1778385112...1778385117,1778385147...1778385153,1778384925...1778384928,1778384948,1778384949,1778384960...1778384964,1778384986...1778384997,1778385015...1778385020,1778385059...1778385065,1778385086...1778385088,1778385118...1778385123,1778385160...1778385192,1778384929...1778384940,1778384953,1778384981...1778384985,1778385004...1778385014,1778385021...1778385032,1778385073...1778385077,1778385089...1778385099,1778385105...1778385111,1778384918...1778384924,1778384945...1778384947,1778384951,1778384952,1778384973...1778384980,1778384998...1778385003,1778384959,1778385193...1778385257&gender=0&c_age=200&measures=20100"

SPINE     = Path("clean/geography_spine.csv")
CROSSWALK = Path("lib/la_code_crosswalk.csv")   # superseded LA code -> current LA code
RAW_DIR   = Path("raw/population")
OUT       = Path("clean/population_itl2.csv")

# --- 1. download the raw data (immutable + dated) ---------------------------
if not NOMIS_URL.lower().startswith("http"):
    raise SystemExit("Set NOMIS_URL to the CSV URL from the Nomis query builder first.")

RAW_DIR.mkdir(parents=True, exist_ok=True)
raw_path = RAW_DIR / f"nomis_population_raw_{date.today().isoformat()}.csv"
print("Downloading from Nomis ...")
urllib.request.urlretrieve(NOMIS_URL, raw_path)
print(f"Saved raw -> {raw_path}")

# --- 2. load raw + spine ----------------------------------------------------
df = pd.read_csv(raw_path, encoding="utf-8-sig")
df.columns = [c.strip().upper() for c in df.columns]
spine = pd.read_csv(SPINE)

def need(col):
    if col not in df.columns:
        raise SystemExit(f"Expected column '{col}' not found.\nColumns are: {list(df.columns)}")
    return col

GEO  = need("GEOGRAPHY_CODE")
VAL  = need("OBS_VALUE")
YEAR = "DATE_NAME" if "DATE_NAME" in df.columns else need("DATE")

# --- 3. tidy to: la_code | year | value -------------------------------------
df = df[[GEO, YEAR, VAL]].rename(columns={GEO: "la_code", YEAR: "year", VAL: "value"})
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# --- 3b. harmonise superseded LA codes to current codes (BEFORE the join) ---
# Some sources (e.g. Nomis) still use retired LA codes. The crosswalk (built by
# build/build_crosswalk.py from the ONS Code History Database) maps them to the
# current codes used in the spine.
if CROSSWALK.exists():
    xw = pd.read_csv(CROSSWALK, dtype=str)
    remap = dict(zip(xw["old_code"], xw["new_code"]))
    n = df["la_code"].isin(remap).sum()
    df["la_code"] = df["la_code"].replace(remap)
    if n:
        print(f"Crosswalk applied: {n} row(s) recoded to current LA codes")
else:
    print("NOTE: no crosswalk found at lib/la_code_crosswalk.csv -- run build/build_crosswalk.py first.")

# --- 4. join onto the spine, report any LA codes that didn't match ----------
merged = df.merge(spine, on="la_code", how="left")
unmatched = sorted(merged.loc[merged["itl2_code"].isna(), "la_code"].dropna().unique())
if unmatched:
    show = unmatched[:10]
    print(f"NOTE: {len(unmatched)} LA code(s) not in the spine, so dropped: "
          f"{show}{' ...' if len(unmatched) > 10 else ''}")
    print("      Investigate each: if it's a live authority, check build_crosswalk.py output.")
merged = merged.dropna(subset=["itl2_code"])

# --- 5. aggregate: population is a COUNT -> SUM to ITL2 ----------------------
pop = (merged.groupby(["itl2_code", "itl2_name", "year"], as_index=False)["value"]
             .sum()
             .rename(columns={"value": "population"})
             .sort_values(["year", "itl2_code"])
             .reset_index(drop=True))

OUT.parent.mkdir(parents=True, exist_ok=True)
pop.to_csv(OUT, index=False)

# --- 6. summary + sanity checks ---------------------------------------------
years = sorted(pop["year"].astype(str).unique())
print(f"Built ITL2 population: {pop['itl2_code'].nunique()} regions x {len(years)} year(s) = {len(pop)} rows")
latest = years[-1]
total = pop.loc[pop["year"].astype(str) == latest, "population"].sum()
print(f"Total population in {latest}: {total:,.0f}   (all-ages UK ~67-68m)")
print(f"Saved -> {OUT}")