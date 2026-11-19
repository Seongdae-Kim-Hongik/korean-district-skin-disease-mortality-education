# -*- coding: utf-8 -*-
# figs_sknd.py — SKND figures. Color; panel letters = one fig.text constant PANEL_LABEL_PT (same size and weight in every panel), lowercase '(a)' at top left.
#  방위표 3배(동해 중간), 그림 안 설명문 없음, 결합은 시군구 코드로만. TIFF: 지도 600 dpi, 선화 1200 dpi.
#  Fig 1 (A) 성별 연간 사망 (B) 성별 연령표준화율 (C) 연령군별 사망 분포 · Fig 2 지도 (A) 14년 SMR (B) 평활 잔차 RR (C) 핫·콜드스팟 · Fig 3 4변수 모형별 RR
import os, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Polygon, Rectangle
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from numbers_sknd import load, SHP, DESC, TE, ALN, GH, P80
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figs"); OUTF = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
MM = 1 / 25.4; W = 170 * MM; DPI = 600; LW = 0.3
PANEL_LABEL_PT = 54   # 15 런북 11/10·37호: 48–64 pt, fig.text 상수 하나
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "legend.fontsize": 8, "legend.title_fontsize": 8.5, "axes.linewidth": 0.6, "pdf.fonttype": 42})
NFC = lambda s: unicodedata.normalize("NFC", str(s)).strip()
N = load()
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["region"] = G.region.map(NFC); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido")
assert G.region.is_unique and len(G) == 229
XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
def label(fig, ax, ch, dx=-0.02, dy=0.01):   # 축 왼쪽 위 바깥, 그림 좌표
    bb = ax.get_position(); fig.text(max(bb.x0 + dx, 0.012), bb.y1 + dy, f"({ch.lower()})", fontsize=PANEL_LABEL_PT, fontweight="bold", va="bottom", ha="left")
def mapax(ax):
    SIDO.boundary.plot(ax=ax, color="#303030", linewidth=0.5); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0
    bx, by, bh = x0 + 0.55 * W_, y0 + 0.03 * H_, 0.012 * H_
    ax.add_patch(Rectangle((bx, by), 50000, bh, facecolor="black", edgecolor="black", lw=0.5)); ax.add_patch(Rectangle((bx + 50000, by), 50000, bh, facecolor="white", edgecolor="black", lw=0.5))
    for k, t in ((0, "0"), (50000, "50"), (100000, "100")): ax.text(bx + k, by + bh + 0.01 * H_, t, ha="center", va="bottom", fontsize=6.5)
    ax.text(bx + 100000 + 0.015 * W_, by + bh / 2, "km", ha="left", va="center", fontsize=6.5)
    nx, ny, nw, nh = x0 + 0.93 * W_, y0 + 0.40 * H_, 0.06 * W_, 0.20 * H_
    ax.add_patch(Polygon([[nx - nw / 2, ny], [nx, ny + nh], [nx + nw / 2, ny], [nx, ny + 0.25 * nh]], closed=True, facecolor="black", edgecolor="black", lw=0.4))
    ax.text(nx, ny + nh + 0.012 * H_, "N", ha="center", va="bottom", fontsize=22, fontweight="bold")
def save(fig, k, dpi=DPI):
    p = os.path.join(FIG, f"JDDG_Fig{k}.png"); fig.savefig(p, dpi=dpi, facecolor="white"); plt.close(fig)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(dpi, dpi)); im.save(os.path.join(OUTF, f"Figure{k}.tif"), dpi=(dpi, dpi), compression="tiff_lzw"); return im.size

# Fig 1 전국 추이·연령
D = pd.read_csv(os.path.join(DESC, "S47D_national.csv")); A = pd.read_csv(os.path.join(DESC, "S47D_agesex.csv")); yrs = list(range(2011, 2025))
fig = plt.figure(figsize=(W, 4.2)); axs = [fig.add_axes([0.08 + i * 0.325, 0.25, 0.25, 0.47]) for i in range(3)]
SX = (("남자", "Men", "#2166AC", "s"), ("여자", "Women", "#B2182B", "^"))
a = axs[0]; bot = np.zeros(len(yrs))
for s, lab, c, _ in SX:
    v = D[D.sex == s].set_index("year").deaths.reindex(yrs).values; a.bar(yrs, v, bottom=bot, color=c, width=0.75, label=lab); bot += v
assert bot.max() < 700; a.set_ylim(0, 700); a.set_ylabel("Deaths, no."); a.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=7.5)
a = axs[1]
for s, lab, c, mk in (("계", "Both sexes", "#000000", "o"),) + SX:
    a.plot(yrs, D[D.sex == s].set_index("year").asr_2020.reindex(yrs), color=c, marker=mk, ms=2.8, lw=1.0, label=lab)
assert D.asr_2020.max() < 2.0; a.set_ylim(0, 2.0); a.set_ylabel("Age-standardized rate per 100,000"); a.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=7.5)
a = axs[2]; lo = lambda b: int(str(b).split("-")[0].replace("+", ""))
AG = [("<65", 0, 64, "#FDB863"), ("65–74", 65, 74, "#E08214"), ("75–84", 75, 84, "#8073AC"), ("≥ 85", 85, 200, "#2D004B")]
x = np.arange(2); wd = 0.6; bot = np.zeros(2)
for lab, a0, a1, c in AG:
    v = np.array([A[(A.sex == s) & A.band.map(lo).between(a0, a1)].사망자수.sum() / A[A.sex == s].사망자수.sum() * 100 for s, *_ in SX]); a.bar(x, v, bottom=bot, color=c, width=wd, label=lab); bot += v
assert np.allclose(bot, 100); a.set_xticks(x); a.set_xticklabels(["Men", "Women"]); a.set_ylim(0, 100); a.set_ylabel("Share of deaths, 2011–2024 (%)")
a.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=7.5, handlelength=1.0, columnspacing=0.8)
for a in axs[:2]: a.set_xticks([2011, 2015, 2019, 2024])
for a in axs: a.spines[["top", "right"]].set_visible(False); a.tick_params(labelsize=8)
for a, ch in zip(axs, "ABC"): label(fig, a, ch, dx=-0.075, dy=0.02)
s1 = save(fig, 1, dpi=1200)

# Fig 2 지도
P = pd.read_csv(os.path.join(os.path.dirname(DESC), "panel_SKND_std3.csv")); P["sigungu_cd"] = None
S6 = N["s6"].copy(); S6["cd"] = S6.sigungu_cd.astype(str); assert S6.cd.nunique() == 229 and set(S6.cd) == set(G.cd)
d = S6.set_index("cd"); R2C = dict(zip(G.region, G.cd))
sm = P.groupby("fbd_region").agg(c=("cases", "sum"), e=("E", "sum")); sm.index = sm.index.map(NFC).map(R2C); assert sm.index.notna().all() and sm.index.nunique() == 229
d["SMR"] = (sm.c / sm.e).reindex(d.index)
BR = [0, 0.67, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 99]; LB = ["< 0.67", "0.67–0.79", "0.80–0.89", "0.90–0.99", "1.00–1.09", "1.10–1.24", "1.25–1.49", "≥ 1.50"]
PAL = ["#053061", "#2166AC", "#67A9CF", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
for c in ("SMR", "RR"): assert d[c].min() >= BR[0] and d[c].max() < BR[-1]
fig = plt.figure(figsize=(W, 4.6)); pos = [[0.00, 0.20, 0.33, 0.70], [0.335, 0.20, 0.33, 0.70], [0.67, 0.20, 0.33, 0.70]]
for (col, ch), p in zip((("SMR", "A"), ("RR", "B")), pos[:2]):
    ax = fig.add_axes(p); gg = G.copy(); gg["v"] = gg.cd.map(d[col]); assert gg.v.notna().all()
    gg.plot(ax=ax, column="v", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#b5b5b5", linewidth=0.2); mapax(ax); label(fig, ax, ch, dx=0.0, dy=-0.005)
fig.legend(handles=[Patch(facecolor=c, edgecolor="#777777", linewidth=LW, label=l) for c, l in zip(PAL, LB)], title="Ratio ((a) observed/expected; (b) residual spatial)", loc="upper center", bbox_to_anchor=(0.335, 0.20), ncol=4, frameon=False, columnspacing=0.9, handlelength=1.2, fontsize=7)
ax = fig.add_axes(pos[2]); gg = G.copy(); gg["k"] = gg.cd.map(d["class"]); assert gg.k.notna().all()
CK = {"hotspot": "#B2182B", "coldspot": "#2166AC", "neutral": "#EFEFEF"}; gg.plot(ax=ax, color=gg.k.map(CK), edgecolor="#b5b5b5", linewidth=0.2); mapax(ax); label(fig, ax, "C", dx=0.0, dy=-0.005)
fig.legend(handles=[Patch(facecolor=CK[k], edgecolor="#777777", linewidth=LW, label=l) for k, l in (("hotspot", f"Hot spot ({N['n_hot']})"), ("coldspot", f"Cold spot ({N['n_cold']})"), ("neutral", "Neither"))],
           loc="upper center", bbox_to_anchor=(0.835, 0.20), ncol=1, frameon=False, fontsize=7.5, handlelength=1.2)
s2 = save(fig, 2)

# Fig 3 포레스트(4변수 × 모형)
LAB = {TE: "Tertiary-educated\nadults", P80: "Population aged\n≥ 80 years", ALN: "Older-adult single-\nperson households", GH: "General\nhospitals"}
ORD = [TE, P80, ALN, GH]
SEN = lambda s: (lambda v: N["sens"][s][v][:3] if v in N["sens"][s] else None)
MOD = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"]), "o", "#000000"),
       ("Knorr-Held type III", lambda v: N["s43"][("KH_typeIII", v)][:3], "D", "#F4A582"),
       ("Knorr-Held type IV", lambda v: N["s43"][("KH_typeIV", v)][:3], "D", "#B2182B"),
       ("Spatial+-type", lambda v: N["s41"][("D1_spatial_plus", v)][:3], "v", "#8073AC"),
       ("Share aged ≥ 80 years omitted", SEN("s2"), "s", "#2D004B"),
       ("Independent district effect", lambda v: N["s43"][("iid_only", v)][:3], "s", "#E08214"),
       ("Transport-injury deaths as outcome", lambda v: N["nco"][("TRANS", v)][:3], "^", "#2166AC")]
VALS = [t for v in ORD for _, f, _, _ in MOD if (t := f(v)) is not None]; lo_all = min(t[1] for t in VALS); hi_all = max(t[2] for t in VALS)
fig, ax = plt.subplots(figsize=(W, 4.8)); fig.subplots_adjust(left=0.21, right=0.98, top=0.97, bottom=0.29)
off = np.linspace(-0.38, 0.38, len(MOD))
for i, v in enumerate(ORD):
    for (lab, f, mk, fc), o in zip(MOD, off):
        t = f(v)
        if t is None: continue
        e, lo_, hi_ = t; ax.plot([lo_, hi_], [i + o] * 2, color=fc, lw=0.9); ax.plot(e, i + o, marker=mk, mfc=fc, mec=fc, ms=3.8, ls="none")
ax.axvline(1, color="#808080", lw=0.6); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v] for v in ORD]); ax.invert_yaxis()
ax.set_xscale("log"); xt = [0.7, 0.8, 0.9, 1.0, 1.15, 1.35]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
ax.set_xlabel("Rate ratio per 1 standard deviation (95% credible interval, log scale)"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Line2D([0], [0], color=fc, marker=m, mfc=fc, mec=fc, lw=0.9, ms=3.8, label=l) for l, _, m, fc in MOD], loc="upper center", bbox_to_anchor=(0.42, -0.14), ncol=3, frameon=False, fontsize=7.5)
s3 = save(fig, 3, dpi=DPI)   # 1200 dpi(4,600만 화소)는 ScholarOne 변환 실패(400×174 인식) → 600 dpi
for k, s, dp in zip((1, 2, 3), (s1, s2, s3), (1200, DPI, DPI)): print(f"Fig{k}: {s[0]}x{s[1]} px = {s[0]/dp*25.4:.0f} x {s[1]/dp*25.4:.0f} mm")
