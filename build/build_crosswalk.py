"""
build/build_crosswalk.py
------------------------
Builds a superseded-LA-code -> current-LA-code crosswalk from the ONS Code History
Database (CHD), written to lib/la_code_crosswalk.csv (read by every source script
before joining to the spine).

Resolution strategy (name is the arbiter):
  * RECODE (name unchanged): match a terminated LA code to the LIVE LA code with the
    same entity type + same name. Bulletproof, and it ignores the known stray links
    in the CHD 'Changes' table (which sometimes point an old code at a differently-
    named successor).
  * MERGER / rename (name changes): only for codes the recode step can't resolve, use
    the CHD 'Changes' predecessor->successor links, resolving to the current live code.
    If a code has more than one plausible live successor, it is FLAGGED, not guessed.

Setup: unzip the CHD CSV download anywhere under raw/geography/ (the script finds it).
Run from the project root:  python build/build_crosswalk.py
"""

from pathlib import Path
import pandas as pd

GEO_ROOT = Path("raw/geography")
OUT      = Path("lib/la_code_crosswalk.csv")
LA = ("E06", "E07", "E08", "E09", "W06", "S12", "N09")   # local-authority code types

def read_robust(path, **kw):
    for enc in ("cp1252", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc, dtype=str, **kw)
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"Could not decode {path}")

def upper(df):
    df.columns = [c.strip().upper() for c in df.columns]
    return df

def is_la(code):
    return isinstance(code, str) and code[:3] in LA

# --- locate CHD -------------------------------------------------------------
hits = list(GEO_ROOT.rglob("ChangeHistory.csv")) + list(GEO_ROOT.rglob("changehistory.csv"))
if not hits:
    raise SystemExit(f"No ChangeHistory.csv under {GEO_ROOT}.")
ch_file = sorted(hits)[-1]
CHD_DIR = ch_file.parent
tag = f"CHD {CHD_DIR.name}"
print(f"Using CHD in: {CHD_DIR}")

# --- ChangeHistory: names, and the set of live LA codes ---------------------
ch = upper(read_robust(ch_file))
STATUS = "STATUS" if "STATUS" in ch.columns else None
TERM   = next((c for c in ("TERM_DATE", "TERMDATE") if c in ch.columns), None)
ch["ENTITY"] = ch["GEOGCD"].str[:3]
ch["name_key"] = ch["GEOGNM"].str.strip().str.lower()

if STATUS:
    live_mask = ch["STATUS"].str.strip().str.lower().eq("live")
elif TERM:
    live_mask = ch[TERM].isna() | (ch[TERM].astype(str).str.strip() == "")
else:
    raise SystemExit("No STATUS or TERM_DATE column in ChangeHistory.")

la_ch = ch[ch["ENTITY"].isin(LA)]
live_codes = set(la_ch.loc[live_mask.loc[la_ch.index], "GEOGCD"])
name_key_of = dict(zip(ch["GEOGCD"], ch["name_key"]))
live_by_name = (la_ch[live_mask.loc[la_ch.index]]
                .dropna(subset=["name_key"]).drop_duplicates(["ENTITY", "name_key"])
                .set_index(["ENTITY", "name_key"])["GEOGCD"].to_dict())
terminated_la = sorted(set(la_ch.loc[~live_mask.loc[la_ch.index], "GEOGCD"]))

# --- Changes: predecessor -> [successors] (LA only) -------------------------
changes_succ = {}
chg_hits = list(CHD_DIR.glob("Changes.csv")) + list(CHD_DIR.glob("changes.csv"))
if chg_hits:
    chg = upper(read_robust(chg_hits[0]))
    if {"GEOGCD", "GEOGCD_P"}.issubset(chg.columns):
        for p, s in zip(chg["GEOGCD_P"], chg["GEOGCD"]):
            if is_la(p) and is_la(s) and s != p:
                changes_succ.setdefault(p, [])
                if s not in changes_succ[p]:
                    changes_succ[p].append(s)

# --- resolve any old LA code to its current live code -----------------------
def to_current(code, seen=None):
    seen = seen or set()
    if code in live_codes:
        return code
    if code in seen:
        return None
    seen.add(code)
    # 1) recode: live code, same entity + same name  (ignores stray Changes links)
    nm = name_key_of.get(code)
    if nm:
        cand = live_by_name.get((code[:3], nm))
        if cand and cand != code:
            return cand
    # 2) merger/rename: via Changes successors, resolved to current; unique or nothing
    resolved = set()
    for s in changes_succ.get(code, []):
        r = to_current(s, seen)
        if r:
            resolved.add(r)
    return next(iter(resolved)) if len(resolved) == 1 else None

mappings, ambiguous = {}, []
for old in terminated_la:
    new = to_current(old)
    if new is None:
        if changes_succ.get(old):
            ambiguous.append(old)
    elif new != old:
        mappings[old] = new

xw = pd.DataFrame(
    [{"old_code": o, "new_code": n, "name": ch.loc[ch.GEOGCD == o, "GEOGNM"].iloc[0], "note": tag}
     for o, n in mappings.items()]
).drop_duplicates("old_code")

# --- self-check -------------------------------------------------------------
checks = {"E08000016": "E08000038",   # Barnsley  (recode; must ignore stray Sheffield link)
          "E08000019": "E08000039",   # Sheffield (recode)
          "E07000004": "E06000060"}   # Aylesbury Vale -> Buckinghamshire (merger)
print("\nSelf-check:")
ok = True
for old, new in checks.items():
    got = xw.loc[xw.old_code == old, "new_code"].tolist()
    good = got == [new]
    ok = ok and good
    print(f"  {old} -> {new}: {'OK' if good else 'FAILED (got ' + str(got) + ')'}")

# --- preserve manual entries, write -----------------------------------------
if OUT.exists():
    prev = read_robust(OUT)
    xw = pd.concat([xw, prev[~prev["old_code"].isin(xw["old_code"])]], ignore_index=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
xw.sort_values("old_code").to_csv(OUT, index=False)

print(f"\nCrosswalk written: {len(xw)} mappings -> {OUT}")
if ambiguous:
    print(f"Flagged {len(ambiguous)} code(s) with ambiguous successors (left unmapped, review if they appear): {ambiguous[:15]}")
print("\nSample:")
print(xw.sort_values("old_code").head(10).to_string(index=False))