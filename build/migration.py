"""
build/migration.py
------------------
Internal migration (England & Wales) -> net migration per ITL2 region.

Source: ONS "Internal migration in England and Wales" tables. Uses the T1a tables
(2023 LA boundaries): one row per LA with Inflow / Outflow / Net. Reads every
IM{year}-T1a sheet across ALL workbooks in raw/migration/, so the 2012-2021
back-series file and the individual 2022-2025 tables files are all picked up.

Aggregation: inflow and outflow are COUNTS -> SUM to ITL2; net = inflow - outflow.
(Within-region moves cancel in net, so summing LA net to ITL2 is correct.)

Coverage: England & Wales only. Scottish / NI ITL2 regions will be absent (reported).

Run from the project root:  python build/migration.py
"""

import re
from pathlib import Path
import pandas as pd

MIG_DIR   = Path("raw/migration")
SPINE     = Path("clean/geography_spine.csv")
CROSSWALK = Path("lib/la_code_crosswalk.csv")
OUT       = Path("clean/migration_itl2.csv")
LA_PREFIX = ("E06", "E07", "E08", "E09", "W06", "S12", "N09")

def find_header(raw):
    for i in range(min(12, len(raw))):
        row = [str(x).strip().lower() if x is not None else "" for x in raw.iloc[i].tolist()]
        if any("la code" in c for c in row) and any(c == "inflow" for c in row):
            return i
    return None

# --- 1. extract every IM{year}-T1a sheet from every workbook ----------------
books = sorted(MIG_DIR.glob("*.xlsx"))
if not books:
    raise SystemExit(f"No .xlsx files in {MIG_DIR}. Download the ONS internal migration tables there.")

frames = []
for book in books:
    xl = pd.ExcelFile(book)
    got = 0
    for sh in xl.sheet_names:
        m = re.fullmatch(r"IM(\d{4})-T1a", sh)
        if not m:
            continue
        got += 1
        year = int(m.group(1))
        raw = xl.parse(sh, header=None)
        hdr = find_header(raw)
        if hdr is None:
            print(f"  ! {book.name}[{sh}]: no header row found, skipped")
            continue
        df = xl.parse(sh, skiprows=hdr)
        df.columns = [str(c).strip() for c in df.columns]
        la = [c for c in df.columns if c.lower().replace(" ", "") == "lacode"][0]
        ic = [c for c in df.columns if c.lower() == "inflow"][0]
        oc = [c for c in df.columns if c.lower() == "outflow"][0]
        sub = (df[[la, ic, oc]]
               .rename(columns={la: "la_code", ic: "inflow", oc: "outflow"})
               .dropna(subset=["la_code"]))
        sub["la_code"] = sub["la_code"].astype(str).str.strip()
        sub = sub[sub.la_code.str[:3].isin(LA_PREFIX)].copy()
        for c in ("inflow", "outflow"):
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        sub["year"] = year
        frames.append(sub)
    if got == 0:
        print(f"  (no IM{{year}}-T1a sheet in {book.name}; its sheets: {xl.sheet_names[:8]}{' ...' if len(xl.sheet_names) > 8 else ''})")

if not frames:
    raise SystemExit("No IM{year}-T1a sheets found. Check the downloaded files' sheet names.")

mig = pd.concat(frames, ignore_index=True).drop_duplicates(["la_code", "year"])
years = sorted(mig.year.unique())
print(f"Extracted {len(mig)} LA-year rows | years {years[0]}-{years[-1]} ({len(years)}) | {mig.la_code.nunique()} LAs")

# --- 2. harmonise old LA codes to current --------------------------------
if CROSSWALK.exists():
    xw = pd.read_csv(CROSSWALK, dtype=str)
    remap = dict(zip(xw.old_code, xw.new_code))
    n = mig.la_code.isin(remap).sum()
    mig["la_code"] = mig["la_code"].replace(remap)
    if n:
        print(f"Crosswalk applied: {n} row(s) recoded to current LA codes")

# --- 3. join spine ----------------------------------------------------------
spine = pd.read_csv(SPINE)
merged = mig.merge(spine, on="la_code", how="left")
unmatched = sorted(merged.loc[merged.itl2_code.isna(), "la_code"].dropna().unique())
if unmatched:
    print(f"NOTE: {len(unmatched)} LA code(s) not in spine (dropped): "
          f"{unmatched[:10]}{' ...' if len(unmatched) > 10 else ''}")
merged = merged.dropna(subset=["itl2_code"])

# --- 4. aggregate to ITL2: sum flows, net = in - out ------------------------
agg = merged.groupby(["itl2_code", "itl2_name", "year"], as_index=False)[["inflow", "outflow"]].sum()
agg["net_migration"] = agg["inflow"] - agg["outflow"]
agg = agg.sort_values(["year", "itl2_code"]).reset_index(drop=True)

OUT.parent.mkdir(parents=True, exist_ok=True)
agg.to_csv(OUT, index=False)

# --- 5. coverage report (E&W only) ------------------------------------------
regions = spine[["itl2_code", "itl2_name"]].drop_duplicates()
covered = set(agg.itl2_code.unique())
missing = regions[~regions.itl2_code.isin(covered)]
print(f"\nBuilt ITL2 net migration: {len(covered)} of {len(regions)} regions x {len(years)} years")
if len(missing):
    print(f"Regions with NO data (expected -- source is England & Wales only): {len(missing)}")
    print("  " + ", ".join(missing.itl2_name.tolist()))
print(f"Saved -> {OUT}")