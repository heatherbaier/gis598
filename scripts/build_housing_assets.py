"""Builds everything the "basics of supervised learning" chapter needs from data/california_housing.csv:

    explorers/line-fit.html            interactive: fit a line by hand, squared vs absolute error
    explorers/threshold-explorer.html  interactive: classifier decision threshold
    explorers/knn-validation.html      interactive: nearest neighbors, training vs validation error
    figures/*.png, figures/*.svg       the two static figures, in light and dark versions
    _variables.yml                     numbers quoted in the chapter text, as {{< var housing.name >}}

Run it from this folder after changing the data, the split, or a template:

    python build_housing_assets.py

It needs numpy, pandas, scikit-learn, and matplotlib. All results use the split the chapter shares
(60 percent training, 20 percent validation, 20 percent test, random_state=42).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, QuantileRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor, NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOLLARS = 100_000          # the target is stored in hundreds of thousands of dollars

# ---------------------------------------------------------------- data and shared split
d = pd.read_csv(ROOT / "data" / "california_housing.csv")
X, y = d.drop(columns="MedHouseVal"), d["MedHouseVal"]
X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_rest, y_rest, test_size=0.25, random_state=42)
LL = ["Latitude", "Longitude"]


def mae(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred) * DOLLARS


# ---------------------------------------------------------------- baselines
mean_mae = mae(y_val, np.full(len(y_val), y_train.mean()))
loc_model = KNeighborsRegressor(n_neighbors=10).fit(X_train[LL], y_train)
loc_mae = mae(y_val, loc_model.predict(X_val[LL]))

# ---------------------------------------------------------------- k-nearest neighbors, latitude and longitude only
KS = [1, 2, 3, 5, 8, 12, 20, 35, 60, 100, 200, 500, 1000, len(X_train)]
train_err, val_err = [], []
for k in KS:
    m = KNeighborsRegressor(n_neighbors=k).fit(X_train[LL], y_train)
    train_err.append(round(mae(y_train, m.predict(X_train[LL]))))
    val_err.append(round(mae(y_val, m.predict(X_val[LL]))))
best_i = int(np.argmin(val_err))

# prediction surface on a grid, kept to cells close to a real block group
STEP = 0.1
lon0, lat0 = np.floor(d.Longitude.min() * 10) / 10, np.floor(d.Latitude.min() * 10) / 10
nx = int(np.ceil((d.Longitude.max() - lon0) / STEP)) + 1
ny = int(np.ceil((d.Latitude.max() - lat0) / STEP)) + 1
gx, gy = np.meshgrid(lon0 + STEP * (np.arange(nx) + 0.5), lat0 + STEP * (np.arange(ny) + 0.5))
grid_pts = np.c_[gy.ravel(), gx.ravel()]
near = NearestNeighbors(n_neighbors=1).fit(d[LL].values).kneighbors(grid_pts)[0].ravel()
cells = np.where(near <= 0.25)[0]
pred = []
for k in KS:
    m = KNeighborsRegressor(n_neighbors=k).fit(X_train[LL].values, y_train)
    pred.append([int(round(v * 100)) for v in m.predict(grid_pts[cells])])   # thousands of dollars
knn_data = {"ks": KS, "train": train_err, "val": val_err,
            "grid": {"lon0": float(lon0), "lat0": float(lat0), "step": STEP, "nx": nx, "ny": ny,
                     "cells": [int(c) for c in cells], "pred": pred}}

# ---------------------------------------------------------------- line fit: income against home value
rng = np.random.RandomState(42)
pick = rng.choice(len(X_train), 400, replace=False)
xs = X_train["MedInc"].values[pick] * 10               # thousands of dollars of income
ys = y_train.values[pick] * DOLLARS                    # dollars
slope_ls, icpt_ls = np.polyfit(xs, ys, 1)
lad = QuantileRegressor(quantile=0.5, alpha=0, solver="highs").fit(xs.reshape(-1, 1), ys)
line_data = {"x": [round(float(v), 1) for v in xs], "y": [int(round(v)) for v in ys],
             "capped": [int(v >= 500000) for v in ys],
             "ls": {"a": float(icpt_ls), "b": float(slope_ls)},
             "lad": {"a": float(lad.intercept_), "b": float(lad.coef_[0])}}

# ---------------------------------------------------------------- classifier: below the statewide median
median = float(y.median())
lab_train, lab_val = (y_train < median).astype(int), (y_val < median).astype(int)
clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_train, lab_train)
p_below = clf.predict_proba(X_val)[:, 1]
thr_data = {"lon": [int(round(v * 100)) for v in X_val["Longitude"]],
            "lat": [int(round(v * 100)) for v in X_val["Latitude"]],
            "p": [int(round(v * 1000)) for v in p_below], "y": [int(v) for v in lab_val],
            "median": int(round(median * DOLLARS, -2))}

# ---------------------------------------------------------------- numbers for the chapter text
n_capped = int((y >= 5).sum())
thousand = lambda v: f"${int(round(v, -3)):,}"
variables = {
    "n_rows": f"{len(d):,}",
    "n_capped": f"{n_capped:,}",
    "mean_mae": thousand(mean_mae),
    "loc_mae": thousand(loc_mae),
    "k1_train_mae": thousand(train_err[0]),
    "k1_val_mae": thousand(val_err[0]),
    "best_k": str(KS[best_i]),
    "best_val_mae": thousand(val_err[best_i]),
}
(ROOT / "_variables.yml").write_text(
    "# Written by scripts/build_housing_assets.py. Use in a chapter as {{< var housing.mean_mae >}}.\n"
    "housing:\n" + "".join(f'  {k}: "{v}"\n' for k, v in variables.items()))


# ---------------------------------------------------------------- fill the widget templates
def build_widget(template, out, data):
    html = (HERE / "templates" / template).read_text()
    html = html.replace("/*__BASE_CSS__*/", (HERE / "templates" / "_base.css").read_text())
    html = html.replace("/*__BRIDGE__*/", (HERE / "templates" / "_bridge.js").read_text())
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    (ROOT / "explorers" / out).write_text(html)


build_widget("line-fit.html", "line-fit.html", line_data)
build_widget("threshold.html", "threshold-explorer.html", thr_data)
build_widget("knn-validation.html", "knn-validation.html", knn_data)

# ---------------------------------------------------------------- static figures
THEMES = {
    "light": dict(text="#1f1f26", muted="#5a5a62", rule="#cfcfca", dots="#c4c4be", feat="#eeedfe", targ="#faeeda",
                  accent="#534ab7", bar_a="#9a9aa4", bar_b="#534ab7", ring="#fcfcfa"),
    "dark": dict(text="#e4e4ea", muted="#9a9aa4", rule="#3a3a44", dots="#4a4a56", feat="#25234f", targ="#3b2a0b",
                 accent="#9a93f0", bar_a="#6a6a74", bar_b="#9a93f0", ring="#16161a"),
}
FIGDIR = ROOT / "figures"
plt.rcParams["font.family"] = "DejaVu Sans"


def excerpt_figure(theme):
    c = THEMES[theme]
    # six real block groups, each the closest one to a spot across the state
    spots = [(37.77, -122.42), (34.02, -118.49), (36.74, -119.79), (34.90, -117.02), (32.72, -117.16), (40.58, -122.39)]
    rows = []
    for lat, lon in spots:
        rows.append(int(((d.Latitude - lat) ** 2 + (d.Longitude - lon) ** 2).idxmin()))
    cols = ["MedInc", "HouseAge", "AveRooms", "AveBedrms", "Population", "AveOccup", "Latitude", "Longitude", "MedHouseVal"]
    fmt = {"MedInc": "{:.2f}", "HouseAge": "{:.0f}", "AveRooms": "{:.2f}", "AveBedrms": "{:.2f}", "Population": "{:,.0f}",
           "AveOccup": "{:.2f}", "Latitude": "{:.2f}", "Longitude": "{:.2f}", "MedHouseVal": "{:.2f}"}
    widths = [0.085, 0.1, 0.11, 0.115, 0.12, 0.12, 0.11, 0.1, 0.105, 0.15]
    xs_ = np.concatenate([[0], np.cumsum(widths)])
    xs_ = xs_ / xs_[-1]

    fig = plt.figure(figsize=(10, 4.0), dpi=200)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0.0, 0.02, 0.675, 0.86]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    nrow = len(rows) + 1
    rh = 1 / (nrow + 1.1)
    top = 1 - 1.1 * rh
    # column bands
    ax.add_patch(plt.Rectangle((xs_[1], 0), xs_[9] - xs_[1], top, color=c["feat"], lw=0))
    ax.add_patch(plt.Rectangle((xs_[9], 0), xs_[10] - xs_[9], top, color=c["targ"], lw=0))
    heads = ["Row"] + cols
    for j, h in enumerate(heads):
        ax.text((xs_[j] + xs_[j + 1]) / 2, top - rh / 2, h, ha="center", va="center", fontsize=7.4, fontweight="bold", color=c["text"])
    ax.plot([0, 1], [top - rh, top - rh], color=c["rule"], lw=0.8)
    for i, r in enumerate(rows):
        yy = top - rh * (i + 1.5)
        ax.text((xs_[0] + xs_[1]) / 2, yy, str(r), ha="center", va="center", fontsize=8.4, color=c["muted"])
        for j, col in enumerate(cols):
            ax.text((xs_[j + 1] + xs_[j + 2]) / 2, yy, fmt[col].format(d.loc[r, col]), ha="center", va="center", fontsize=8.6, color=c["text"])
    # brackets above the groups of columns
    by = top + 0.035
    for a, b, label in [(xs_[1], xs_[9], "features (the inputs)"), (xs_[9], xs_[10], "target")]:
        ax.plot([a + 0.006, a + 0.006, b - 0.006, b - 0.006], [by - 0.02, by, by, by - 0.02], color=c["accent"], lw=1.1, clip_on=False)
        ax.text((a + b) / 2, by + 0.025, label, ha="center", va="bottom", fontsize=8.8, color=c["accent"], fontweight="bold")

    mp = fig.add_axes([0.70, 0.02, 0.29, 0.86])
    mp.scatter(d.Longitude, d.Latitude, s=1.2, color=c["dots"], lw=0, rasterized=True)
    mp.set_aspect(1 / np.cos(np.radians(37.3))); mp.axis("off")
    offs = {rows[0]: (12, 5), rows[1]: (-14, -8), rows[2]: (12, 4), rows[3]: (12, 2), rows[4]: (12, -8), rows[5]: (12, 3)}
    for r in rows:
        mp.scatter(d.Longitude[r], d.Latitude[r], s=34, color=c["accent"], edgecolor=c["ring"], lw=1.2, zorder=3)
        dx, dy = offs[r]
        mp.annotate(str(r), (d.Longitude[r], d.Latitude[r]), xytext=(dx, dy), textcoords="offset points", fontsize=8.2,
                    color=c["text"], fontweight="bold", ha="left" if dx > 0 else "right", va="center", zorder=4)
    fig.text(0.845, 0.935, "Where these block groups are", ha="center", va="center", fontsize=8.8, color=c["muted"])
    fig.savefig(FIGDIR / f"housing-excerpt-{theme}.png", transparent=True)
    plt.close(fig)
    return rows


# models shown on the baseline chart; add more (name, error in dollars) to extend it
BARS = [("Statewide average\n(mean baseline)", mean_mae), ("Nearest block groups, location only\n(k = 10)", loc_mae)]


def baseline_figure(theme):
    c = THEMES[theme]
    fig, ax = plt.subplots(figsize=(8, 0.95 + 0.75 * len(BARS)), dpi=100)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    labels = [b[0] for b in BARS][::-1]; vals = [b[1] for b in BARS][::-1]
    colors = [c["bar_b"] if i == len(vals) - 1 - 0 and False else c["bar_a"] for i in range(len(vals))]
    colors = [c["bar_b"] if n.startswith("Nearest") else c["bar_a"] for n in labels]
    ax.barh(range(len(vals)), vals, color=colors, height=0.55)
    for i, v in enumerate(vals):
        ax.text(v + 1500, i, f"${v:,.0f}", va="center", ha="left", fontsize=11, fontweight="bold", color=c["text"])
    ax.set_yticks(range(len(vals))); ax.set_yticklabels(labels, fontsize=10.5, color=c["text"])
    ax.set_xlim(0, max(vals) * 1.22)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.tick_params(axis="x", colors=c["muted"], labelsize=9.5); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Average error on the validation block groups (dollars)", fontsize=10, color=c["muted"])
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(c["rule"])
    ax.grid(axis="x", color=c["rule"], lw=0.7, alpha=0.7); ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(FIGDIR / f"baselines-{theme}.svg", transparent=True)
    plt.close(fig)


for t in THEMES:
    excerpt_rows = excerpt_figure(t)
    baseline_figure(t)

print("train / validation / test:", len(X_train), len(X_val), len(X_test))
print("mean baseline MAE: $%.0f   location kNN (k=10) MAE: $%.0f" % (mean_mae, loc_mae))
print("k, train, val:", list(zip(KS, train_err, val_err)))
print("best k by validation error:", KS[best_i])
print("capped block groups:", n_capped, "  grid cells kept:", len(cells))
print("line fits, least squares:", line_data["ls"], " least absolute:", line_data["lad"])
print("figure rows:", excerpt_rows)
