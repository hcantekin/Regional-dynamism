"""
analysis/chart_setup.py
-----------------------
Shared chart setup for the analysis notebooks (reallocation/, productivity/, rurality/, demographics/).

    import sys; sys.path.append(str(BASE / "analysis"))
    from chart_setup import styles, alt, ECO, TXT, GREY, label_layers

- Enables the Economics Observatory house theme (eco_styles.py, kept as copied from the template)
  with one project tweak: no gridlines on any chart (axis lines and reference rules only).
- label_layers(): simple label placement used by the scatter charts.
"""
import warnings
import altair as alt
import eco_styles

warnings.filterwarnings("ignore", category=DeprecationWarning)          # alt.themes -> alt.theme rename in Altair 5.5
styles = eco_styles.EcoStyles()
styles.register_and_enable_theme()

_theme = styles.custom_theme()
for key in ["axis", "axisXDiscrete", "axisXTemporal", "axisXQuantitative", "axisYQuantitative", "axisYDiscrete"]:
    _theme["config"].setdefault(key, {})["grid"] = False
_theme["config"]["axis"].update({"domain": True, "domainOpacity": 1})
alt.themes.register("cotd_nogrid", lambda: _theme)
alt.themes.enable("cotd_nogrid")

ECO = styles.eco_colours
TXT, GREY = styles.palette["light"]["text"], styles.palette["light"]["deemphasise_color"]


def label_layers(d, xcol, ycol, xs, ys, width, height, text="itl2_name"):
    """One text layer per label: labels in the right 30% go left of the point; labels that would overlap are staggered."""
    (x0, x1), (y0, y1) = xs.domain, ys.domain
    d = d.copy()
    d["px"] = (d[xcol] - x0) / (x1 - x0) * width
    d["py"] = (y1 - d[ycol]) / (y1 - y0) * height
    d["right"] = d.px > 0.7 * width
    d["dy"] = 0
    d = d.sort_values("py").reset_index(drop=True)
    for i in range(1, len(d)):
        a, b = d.loc[i - 1], d.loc[i]
        if abs(b.py - a.py) < 13 and abs(b.px - a.px) < 160:
            d.loc[i - 1, "dy"] -= 7; d.loc[i, "dy"] += 7
    return [alt.Chart(d.iloc[[i]]).mark_text(align="right" if r.right else "left", dx=-8 if r.right else 8, dy=float(r.dy),
                                             fontSize=10, color=TXT)
              .encode(x=alt.X(f"{xcol}:Q", scale=xs), y=alt.Y(f"{ycol}:Q", scale=ys), text=f"{text}:N")
            for i, r in d.iterrows()]


def place_labels(d, xcol, ycol, xs, ys, width, height, size=None, size_col="emp", fs=9, xlog=False,
                 max_labels=5, max_len=20, pad=4, group_col="group", priority_group="London", candidates=None):
    """Sparse greedy labels for scatter charts. Priority: `priority_group` first, then points furthest from the centre.
    Each label goes just right or left of its dot and is skipped if it would touch another label, another dot or the
    frame; names longer than `max_len` are skipped (tooltips still show them). `candidates` (list of itl2_name) restricts
    which dots get labels. Returns rows with align/dx for mark_text.
    `size` is the (linear, area) alt.Scale used for the dots, so dot radii are allowed for; xlog=True for log x scales."""
    import numpy as np
    import pandas as pd
    (x0, x1), (y0, y1) = xs.domain, ys.domain
    tx = (lambda v: np.log(v)) if xlog else (lambda v: v)
    d = d.copy()
    d["px"] = (tx(d[xcol]) - tx(x0)) / (tx(x1) - tx(x0)) * width
    d["py"] = (y1 - d[ycol]) / (y1 - y0) * height
    d["short"] = d.itl2_name.str.replace(" - ", " ", regex=False).str.replace(" and ", " & ", regex=False)
    if size is not None:
        (s0, s1), (a0, a1) = size.domain, size.range
        d["rad"] = np.sqrt((a0 + (d[size_col] - s0) / (s1 - s0) * (a1 - a0)) / np.pi)
    else:
        d["rad"] = 4.0
    z = lambda s: (s - s.mean()) / s.std()
    d["prio"] = (np.where(d[group_col] == priority_group, 10, 0) if group_col in d else 0) + np.hypot(z(d.px), z(d.py))
    pts, boxes, out = d[["px", "py", "rad"]].values, [], []
    cand = d[d.short.str.len() <= max_len] if max_len else d
    if candidates is not None:                                           # label only these rows (all dots still act as obstacles)
        cand = d[d.itl2_name.isin(candidates)]
    for _, r in cand.sort_values("prio", ascending=False).iterrows():
        if max_labels and len(out) >= max_labels:
            break
        w, h, gap = 0.56 * fs * len(r.short), fs + 2, r.rad + 5
        for align, dx in (("left", gap), ("right", -gap)):
            bx0 = r.px + dx if align == "left" else r.px + dx - w
            b = (bx0, r.py - h / 2, bx0 + w, r.py + h / 2)
            inside = b[0] >= 0 and b[2] <= width and b[1] >= 0 and b[3] <= height
            hits_lab = any(not (b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3]) for o in boxes)
            hits_pt = any(b[0] - rr - pad <= px <= b[2] + rr + pad and b[1] - rr - pad <= py <= b[3] + rr + pad
                          for px, py, rr in pts if (px, py) != (r.px, r.py))
            if inside and not hits_lab and not hits_pt:
                boxes.append(b); out.append({**r.to_dict(), "align": align, "dx": float(dx)}); break
    return pd.DataFrame(out)
