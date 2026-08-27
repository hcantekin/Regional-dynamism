"""
build/ppd_complete.py
---------------------
Build MEDIAN house price per ITL2 region per year from the single large Price Paid
file (pp-complete.csv, ~5GB, ~30M rows).

Streams the file in chunks so it never loads all 5GB at once, keeps only the slim
(region, year, price) for category-A residential sales, and takes a true median per
region-year at the end.

Geography: postcode -> local authority (ONSPD 'lad25cd') -> crosswalk -> ITL2 spine.
We deliberately DO NOT trust ONSPD's 'itl25cd' column: in the Feb 2026 release it
actually contains local-authority codes, not ITL codes. ITL2 comes from OUR spine.

Inputs:  raw/housing/price_paid/pp-complete.csv  and  raw/onspd/ONSPD*.csv
Output:  clean/house_prices_median_itl2.csv
Run from the project root:  python build/ppd_complete.py
"""

from pathlib import Path
import pandas as pd

BASE      = Path(".")
PP_FILE   = BASE / "raw" / "housing" / "price_paid" / "pp-complete.csv"
ONSPD_DIR = BASE / "raw" / "onspd"
SPINE     = BASE / "clean" / "geography_spine.csv"
CROSSWALK = BASE / "lib" / "la_code_crosswalk.csv"
OUT       = BASE / "clean" / "house_prices_median_itl2.csv"

PP_COLS = ["txn_id","price","date","postcode","property_type","old_new","duration",
           "paon","saon","street","locality","town","district","county",
           "ppd_category","record_status"]
USE = ["price","date","postcode","property_type","ppd_category"]
RES = {"D","S","T","F"}
CHUNK = 500_000

def norm_pc(s):
    return s.astype(str).str.upper().str.replace(" ", "", regex=False)

# --- postcode -> LA -> (crosswalk) -> ITL2, always via OUR spine ------------------
onspd_file = (list(ONSPD_DIR.rglob("ONSPD*.csv")) + list(ONSPD_DIR.rglob("*.csv")))[0]
ocols = {c.lower(): c for c in pd.read_csv(onspd_file, nrows=0).columns}
pc_col  = ocols.get("pcds") or ocols.get("pcd")
lad_col = ocols.get("lad25cd") or ocols.get("oslaua") or ocols.get("laua") or ocols.get("lad")
if not (pc_col and lad_col):
    raise SystemExit(f"Need postcode + LA columns in ONSPD. Found: {list(ocols)}")

o = pd.read_csv(onspd_file, usecols=[pc_col, lad_col], dtype=str)
spine = pd.read_csv(SPINE)
lad2itl = dict(zip(spine.la_code, spine.itl2_code))
remap = {}
if CROSSWALK.exists():
    xw = pd.read_csv(CROSSWALK, dtype=str)
    remap = dict(zip(xw.old_code, xw.new_code))
o["itl2"] = o[lad_col].replace(remap).map(lad2itl)
pc_to_itl = dict(zip(norm_pc(o[pc_col]), o["itl2"]))
print(f"Postcode->ITL2 via '{lad_col}' + spine: {len(pc_to_itl):,} postcodes "
      f"({o['itl2'].notna().sum():,} mapped to an ITL2 region)")

# --- stream the big file, keeping only slim (itl2, year, price) -------------------
slim = []
rows_kept = unmapped = 0
reader = pd.read_csv(PP_FILE, header=None, names=PP_COLS, usecols=USE, dtype=str, chunksize=CHUNK)
for i, chunk in enumerate(reader, 1):
    chunk = chunk[(chunk["ppd_category"] == "A") & (chunk["property_type"].isin(RES))]
    price = pd.to_numeric(chunk["price"], errors="coerce")
    year  = pd.to_datetime(chunk["date"], errors="coerce").dt.year
    itl2  = norm_pc(chunk["postcode"]).map(pc_to_itl)
    unmapped += int((price.notna() & itl2.isna()).sum())
    good = price.notna() & year.notna() & itl2.notna()
    slim.append(pd.DataFrame({
        "itl2":  itl2[good].astype("category"),
        "year":  year[good].astype("int16"),
        "price": price[good].astype("int64"),
    }))
    rows_kept += int(good.sum())
    print(f"  chunk {i}: kept {rows_kept:,} residential cat-A sales", end="\r")

print()
df = pd.concat(slim, ignore_index=True)
del slim

# --- true median + count per region-year -----------------------------------------
panel = (df.groupby([df["itl2"].astype(str), "year"])["price"]
           .agg(median_price="median", n_sales="size").reset_index()
           .rename(columns={"itl2": "itl2_code"}))
itl2_name = dict(zip(spine.itl2_code, spine.itl2_name))
panel["itl2_name"] = panel["itl2_code"].map(itl2_name)
panel = panel[["itl2_code","itl2_name","year","median_price","n_sales"]].sort_values(["year","itl2_code"])
OUT.parent.mkdir(parents=True, exist_ok=True)
panel.to_csv(OUT, index=False)
print(f"Unmapped (price-valid) rows dropped: {unmapped:,}")
print(f"Saved -> {OUT}  ({panel.itl2_code.nunique()} regions x {panel.year.nunique()} years, "
      f"{int(panel.n_sales.sum()):,} sales)")