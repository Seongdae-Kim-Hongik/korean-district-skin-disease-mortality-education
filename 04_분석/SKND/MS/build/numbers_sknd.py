# numbers_sknd.py — SKND(L00-L98 피부 및 피하조직 질환 사망) 원고의 모든 수치를 결과 CSV에서 읽는다(2026-11-13, numbers_illd.py 구조 이식). 손입력 금지, assert로 정합 확인.
import os, glob, numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3"); DESC = os.path.join(B, "results_desc")
ROOT = os.path.dirname(os.path.dirname(B)); PAN = os.path.join(ROOT, "02_패널")
SHP = os.environ.get("ST_SHP", os.path.expandvars("$ST_DATA_ROOT") + "/기타/R_Studio/FBD_DATA_ZIP/final.shp")
WIN = [("W1_2011-15", 2011, 2015), ("W2_2016-19", 2016, 2019), ("W3_2020-24", 2020, 2024)]
rd = lambda f, d=RS, **k: pd.read_csv(os.path.join(d, f), encoding="utf-8-sig", **k)
ALN, LTC, CHEW, DM, BLS, TE, GH, WALK, MPA, FAC = ("older_single_household_share", "ltc_hospitals_per_100k_65", "chewing_discomfort_rate_65plus", "screening_suspected_diabetes_share",
    "basic_livelihood_rate", "tertiary_educated_share", "ext__genhosp_per100k", "walking_practice_rate", "moderate_pa_rate", "public_sports_facilities_per_100k")
HYP = [ALN, LTC, CHEW, DM, BLS, TE, GH, WALK, MPA, FAC]
ROB = [TE]; REV = [ALN, GH]; PA = [WALK, MPA, FAC]
FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
P80 = "pop80_share"

def load():
    N = {}
    P = pd.read_csv(os.path.join(B, "panel_SKND_std3.csv")); N["n_rows"], N["n_districts"] = len(P), P.fbd_region.nunique(); assert (N["n_rows"], N["n_districts"]) == (3206, 229)
    N["cases_total"] = int(P.cases.sum()); assert N["cases_total"] == 7333
    N["zeros"] = int((P.cases == 0).sum()); assert N["zeros"] == 675
    yc = P.groupby("year").cases.sum().astype(int); N["n_y"] = yc.to_dict(); assert N["n_y"][2011] == 470 and N["n_y"][2024] == 508
    N["peak_year"] = int(yc.idxmax()); N["peak_n"] = int(yc.max())
    N["per_year"] = (int(yc.min()), int(yc.max()))
    # 전국 기술(성·연령, 직접표준화)
    D = rd("S47D_national.csv", DESC); N["asr"] = {(r.year, r.sex): r.asr_2020 for r in D.itertuples()}; N["crude"] = {(r.year, r.sex): r.crude for r in D.itertuples()}
    N["share85"] = {(r.year, r.sex): r.share85 for r in D.itertuples()}
    N["deaths_sex"] = D[D.sex != "계"].groupby("sex").deaths.sum().to_dict(); N["national_total"] = int(D[D.sex == "계"].deaths.sum()); assert sum(N["deaths_sex"].values()) == N["national_total"] and abs(N["national_total"] - N["cases_total"]) <= 1   # 전국 성·연령표(DT_1B34E01) 7,332 대 시군구표 7,333: 1명 차(공표표 간 차이)
    A = rd("S47D_agesex.csv", DESC); A = A[A.sex == "계"]
    def band_lo(b): return int(str(b).split("-")[0].replace("+", ""))
    A["lo"] = A.band.map(band_lo); tot = A.사망자수.sum(); assert int(round(tot)) == N["national_total"]
    N["pct65"] = 100 * A[A.lo >= 65].사망자수.sum() / tot; N["pct80"] = 100 * A[A.lo >= 80].사망자수.sum() / tot; N["pct85"] = 100 * A[A.lo >= 85].사망자수.sum() / tot
    N["pct_women"] = 100 * N["deaths_sex"]["여자"] / N["national_total"]
    T1 = {}
    for wn, a, b in WIN + [("ALL", 2011, 2024)]:
        q = P[P.year.between(a, b)]; smr = q.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
        T1[wn] = dict(n=len(q), cases=int(q.cases.sum()), zeros=int((q.cases == 0).sum()), p10=smr.quantile(.1), med=smr.median(), p90=smr.quantile(.9),
                      cov={v: (q[f"{v}_raw"].mean(), q[f"{v}_raw"].std()) for v in HYP + FORCED})
    N["T1"] = T1
    # 우도
    L = rd("S47K_likelihood.csv").set_index("likelihood"); N["lik"] = L.to_dict("index")
    lk = rd("S1_likelihood.csv"); lk = lk[lk.set == "REF_forced_only"].set_index("family").WAIC; N["waic_pois"], N["waic_nb"] = lk["poisson"], lk["nbinomial"]; assert N["waic_nb"] < N["waic_pois"]
    hb = open(os.path.join(B, "HM_best_SKND_std3.txt")).read(); N["waic_forced"] = float(hb.split("ref_forced_only_WAIC=")[1].split()[0]); N["waic_main"] = float(hb.split("S1_narrative_full(")[1].split(",")[0])
    N["rule_best"] = hb.split("rule_best_set=")[1].split()[0]; N["waic_rule_best"] = float(hb.split(N["rule_best"] + "(")[1].split(",")[0])
    # 공간
    s6m = rd("S6_moran_year.csv"); N["moran_year"] = (s6m.moran_I.min(), s6m.moran_I.max()); N["moran_year_max_y"] = int(s6m.loc[s6m.moran_I.idxmax(), "year"])
    r8 = rd("S8_residual_moran.csv").set_index("quantity"); N["moran_pooled"] = r8.loc["observed_logSIR_pooled", "moran_I"]
    N["moran_resid"], N["moran_resid_p"] = r8.loc["pearson_residual_area_mean", "moran_I"], r8.loc["pearson_residual_area_mean", "p_perm"]
    h = rd("S3_main_hyper.csv"); ph = h[h.hyperpar.str.startswith("Phi")].iloc[0]; N["phi"] = (ph["mean"], ph["X0.025quant"], ph["X0.975quant"])
    sz = h[h.hyperpar.str.startswith("size")].iloc[0]; N["nb_size"] = (sz["mean"], sz["X0.025quant"], sz["X0.975quant"])
    s6 = rd("S6_spatial_RR.csv"); N["s6"] = s6; N["rr_min"], N["rr_max"] = s6.RR.min(), s6.RR.max()
    N["n_hot"], N["n_cold"] = int((s6["class"] == "hotspot").sum()), int((s6["class"] == "coldspot").sum()); assert (N["n_hot"], N["n_cold"]) == (35, 34)
    sido = s6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]
    N["hot_by_sido"] = s6[s6["class"] == "hotspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["cold_by_sido"] = s6[s6["class"] == "coldspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["n_busan"] = int(sido.eq("부산시").sum())
    pe = rd("S12_persistence.csv").set_index("set"); N["kendall"] = pe.kendall_W.to_dict()
    N["ehsa"] = rd("S11_ehsa_summary.csv").set_index("category").n.to_dict()
    vp = rd("S42_variance_partition.csv").set_index("component"); N["vp_spatial"] = vp.loc["spatial_structured", "share_of_linear_predictor_var"]
    # 원자료 겹침(시군구 14년 SIR 대 공변량 평균, Spearman)
    d = P.groupby("fbd_region").agg(c=("cases", "sum"), e=("E", "sum"), aln=(f"{ALN}_raw", "mean"), p80=(f"{P80}_raw", "mean"), te=(f"{TE}_raw", "mean")).reset_index(); d["sir"] = d.c / d.e
    N["rho_raw"] = {k: float(spearmanr(d.sir, d[k])[0]) for k in ("aln", "p80", "te")}; N["rho_aln_p80"] = float(spearmanr(d.aln, d.p80)[0])
    w = P.groupby(["fbd_region", "window"]).agg(c=("cases", "sum"), e=("E", "sum")).reset_index(); w["sir"] = w.c / w.e
    pw = w.pivot(index="fbd_region", columns="window", values="sir").corr(method="spearman"); N["rho_win"] = (pw.values[np.triu_indices(3, 1)].min(), pw.values[np.triu_indices(3, 1)].max())
    sp = d.assign(sido=d.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]).groupby("sido")[["c", "e"]].sum(); N["sido_sir"] = (sp.c / sp.e).to_dict()
    # 주모형·다중우주
    m3 = rd("S3_main_IRR.csv").set_index("cov"); N["main"] = m3[["IRR", "lo", "hi", "cred", "role"]].to_dict("index")
    N["n_hyp"] = int((m3.role == "hypothesis").sum()); assert N["n_hyp"] == 10 and set(m3.index[m3.role == "hypothesis"]) == set(HYP)
    N["cred_hyp"] = sorted(v for v in HYP if N["main"][v]["cred"]); assert set(N["cred_hyp"]) == {ALN, TE, GH}
    s7 = rd("S7_multiverse_summary.csv").set_index("cov"); N["mv"] = s7[["n_specs", "cred_frac", "sign_agree", "robust"]].to_dict("index"); assert set(s7.index[s7.robust]) == set(ROB)
    N["mv_total"] = int(s7.n_specs_total.iloc[0])
    nc = rd("S3_negcontrol.csv").set_index("cov"); N["negctl"] = {v: (r.IRR, r.lo, r.hi, bool(r.cred)) for v, r in nc.iterrows()}; assert not any(t[3] for t in N["negctl"].values())
    wi = rd("S4_window_IRR.csv"); N["win"] = {(r.cov, r.window): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in wi.itertuples()}
    N["win_ncred"] = [sum(1 for v in HYP if N["win"].get((v, w), (0, 0, 0, False))[3]) for w, _, _ in WIN]
    ia = rd("S4_interaction.csv"); N["n_inter"], N["n_inter_cred"] = len(ia), int(ia.cred.astype(bool).sum()) if "cred" in ia else None
    S43 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S43_part_*.csv"))]); N["s43"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S43.itertuples()}
    N["s43_waic"] = S43.groupby("analysis").WAIC.first().to_dict()
    T9 = rd("S9_typeI_IRR.csv"); N["s43"].update({("KH_typeI", r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in T9.itertuples()}); N["s43_waic"]["KH_typeI"] = float(T9.WAIC.iloc[0])
    S41 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S41_part_*.csv"))]); N["s41"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S41.itertuples()}
    N["s41_waic"] = S41.groupby("analysis").WAIC.first().to_dict()
    ALT = sorted({a for a in S41.analysis.unique() if not a.startswith(("F1_", "F2_", "G2_", "H1_", "bw_"))}); N["alt"] = ALT
    ret = rd("S41_retention_by_cov.csv").set_index("cov"); N["ret"] = {v: (int(ret.loc[v, "kept"]), int(ret.loc[v, "n_specs"])) for v in ret.index}
    N["bw"] = {r.cov: (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S41[S41.analysis == "bw_twoway"].itertuples()}
    N["nco"] = {(r.analysis.replace("H1_nco_", ""), r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S41[S41.analysis.str.startswith("H1_nco_")].itertuples()}
    lo = rd("S41_leaveout_ranges.csv"); N["leaveout"] = {(r.set, r.cov): (r.n, r.n_cred_same_sign) for r in lo.itertuples() if not str(r.cov).startswith("__")}
    N["evalue"] = rd("S41_evalues.csv").set_index("cov").to_dict("index")
    N["sens"] = {}
    for v in ("s577", "s2", "s8", "sa"):
        m = pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_IRR.csv")).set_index("cov"); N["sens"][v] = {c: (m.loc[c, "IRR"], m.loc[c, "lo"], m.loc[c, "hi"], bool(m.loc[c, "cred"])) for c in m.index}
    assert not N["sens"]["s2"][ALN][3] and N["sens"]["s2"][TE][3]   # 80+ 빼면 독거 역방향 소실, 교육 유지
    cv = rd("S5_covid.csv"); N["covid_main"] = tuple(cv[cv.term == "post_main"][["IRR", "lo", "hi", "cred"]].iloc[0])
    N["covid_inter_cred"] = int(cv[cv.term == "var_x_post"].cred.astype(bool).sum())
    eb = rd("S12c_yearly_EB_SIR.csv"); g = eb.groupby("year").ebSIR; gap = pd.DataFrame({"p10": g.quantile(.1), "p90": g.quantile(.9)}); gap["ratio"] = gap.p90 / gap.p10; N["gap"] = gap.to_dict("index")
    return N

if __name__ == "__main__":
    N = load()
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in N.items() if not isinstance(v, (dict, list, pd.DataFrame, tuple))})
    for k in ("phi", "nb_size", "moran_year", "covid_main", "rho_win", "per_year"): print(k, N[k])
    print("hot", N["hot_by_sido"]); print("cold", N["cold_by_sido"]); print("ret", N["ret"], len(N["alt"])); print("rho", N["rho_raw"], N["rho_aln_p80"])
    print("kendall", N["kendall"]); print("asr", {k: v for k, v in N["asr"].items() if k[1] == "계" and k[0] in (2011, 2024)}); print("evalue", N["evalue"]); print("inter", N["n_inter"], N["n_inter_cred"])
    print("sido_sir", {k: round(v, 2) for k, v in N["sido_sir"].items()}); print("gap", {y: round(N["gap"][y]["ratio"], 2) for y in (2011, 2024)})
