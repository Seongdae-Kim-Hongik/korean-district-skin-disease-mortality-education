# esm_sknd.py — SKND Supporting Information (single file: Appendix S1, Tables S1-S4, Appendix S2 STROBE) and a separate STROBE checklist file.
#  수치는 결과 CSV에서만. 영국식 철자(TX가 brit 적용), 표 제목 쌍점 금지, 사후 검토는 post hoc 표기, 보충 번호 = 본문 첫 인용 순서(S1 공변량 → S2 우도 → S3 사양 → S4 핫스팟).
import os, re, json, subprocess, pandas as pd
import content_sknd as C
from build_jddg_sknd import LABEL, GROUPS, TX, TITLE as DTITLE, foot_row
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out"); B = os.path.dirname(MSD); RS = os.path.join(B, "results_std3")
N = C.N
st = lambda t: f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
J = TX(cite="bracket")
def TF(title, header, rows, foot="", fs=8):
    J.page_break(); J.table_fit(title, header, rows, "", fs_max=fs, title_bold=True)
    if foot: foot_row(J, foot, 8, 12)
J.para("<b>Supporting Information</b>"); J.para(f"Supporting information for the manuscript entitled \"{DTITLE}\"")
J.para("Contents. Appendix S1 (supplementary methods and additional results); Table S1 (district characteristics); Table S2 (likelihood comparison); Table S3 (alternative specifications); Table S4 (residual hot spots and cold spots); Appendix S2 (STROBE checklist).")
_MT = pd.read_csv(os.path.join(B, "panel_META_SKND_std3.csv"), encoding="utf-8-sig").set_index("variable")
_imp = lambda v: int(_MT.loc[v, "n_imputed_interp"] + _MT.loc[v, "n_imputed_sgg_mean"] + _MT.loc[v, "n_imputed_year_mean"])
assert int(_MT.loc["older_single_household_share", "obs_year_min"]) == 2015
gate = open(os.path.join(B, "data_gate_SKND_std3_261113.txt"), encoding="utf-8").read(); nwarn = int(re.search(r"경고 (\d+)건", gate).group(1))
_vif = _MT.vif_final.dropna().sort_values(ascending=False); assert _vif.index[0] == "older_single_household_share" and _vif.iloc[1] < 10
AC = pd.read_csv(os.path.join(RS, "S50_access_sensitivity.csv")).set_index("cov"); OC = AC.loc["outside_care_share"]
PPC = pd.read_csv(os.path.join(RS, "S42_ppc.csv")).iloc[0].to_dict()
J.page_break(); J.head("Appendix S1. Supplementary methods and additional results", 2)
SM = [("Outcome.", f"Annual deaths with an underlying cause in ICD-10 Chapter XII (L00–L98) by district of residence came from the 50-item district cause-of-death table of Statistics Korea, summed over the urban wards of cities with general wards and joined by administrative code; the 14-year total was {N['cases_total']:,}. "
       f"National deaths by cause, sex and 5-year age group came from the 104-item national table, whose 14-year total was {N['national_total']:,} (one death fewer than the district table, a difference between the published tables). Districts were harmonised to the 229 units of 2024. The district table does not separate pressure ulcer (L89), cellulitis (L03) or other skin conditions."),
      ("Expected deaths.", "National deaths by sex and age (0–4 to 80–84 years and 85 years or older) were divided by national populations to give annual sex- and age-specific rates, which were applied to district populations by sex and 5-year age group from resident registration. The 2023 age-specific populations of Changwon, which repeated the 2022 values in the source file, were replaced with the official 2023 values (total 1,009,038) before expected deaths and population-based covariates were computed. Alternative expected deaths used age only (18 groups) or ten broad age groups (sensitivity analyses)."),
      ("Covariates.", f"Walking and moderate-or-higher physical activity were age-standardised district rates from the Korea Community Health Survey, and chewing discomfort among adults aged 65 years or older came from the same survey; moderate physical activity was missing for one survey year and was interpolated within districts. "
       f"Suspected diabetes was the share of national general health-screening participants classified as suspected diabetes. Public sports facilities came from the national public sports facility register. General hospitals, long-term care hospitals, tertiary education and basic livelihood recipients came from a harmonised public district panel; recipient shares that collapsed in 2021–2023 for districts of cities with general wards were corrected with city totals. "
       f"The older-adult single-person household share (one-person households aged 65 years or older over all households) was published from 2015; missing district-years were filled with district means (912) or, where a district had no observed value, with yearly means (14), {_imp('older_single_household_share')} district-years in all, and the uncertainty from filling was not propagated into the models."),
      ("Panel checks before modelling.", f"An automated gate run on the analytic panel before any model was fitted reported {nwarn} flags: standardised columns whose yearly means were near 0 (a ratio artefact), real increases over time in the share aged 80 years or older and in sports facilities, the sex ratio above 100 by definition, the post-2020 indicator (constant by design) and districts with no general hospital or long-term care hospital in any year (true zeros); no flag concerned keys, missing outcome counts or population denominators. "
       f"Final variance inflation factors were below 10 except for the older-adult single-person household share ({_vif.iloc[0]:.1f}), which was retained as a pre-specified characteristic and examined post hoc."),
      ("Models.", "Software: R 4.6.0 with R-INLA (one thread) and Python 3.9 for data preparation and figures. Fixed effects had normal priors with mean 0 and precision 4 (intercept precision 0.001). The Besag–York–Mollié 2 district effect used penalised-complexity priors (P(σ > 0.5) = 0.01; P(φ < 0.5) = 2/3) on a 593-edge district adjacency graph with Jeju Island as a separate component; the random-walk and independent year effects used penalised-complexity priors (P(σ > 0.5) = 0.01). Covariate subsets for the multiverse were drawn with a fixed seed. Kendall's W used 2000 permutations of district ranks within years.")]
for h, t in SM: J.para(f"<b>{h}</b> {t}")
J.para("<b>Additional results.</b> " + f"Posterior predictive 95% intervals covered {100*PPC['coverage95']:.1f}% of district-years. The post-2020 indicator was not associated with skin-disease deaths after adjustment ({st(N['covid_main'])}), and none of its interactions with the characteristics was credible. "
       f"The share of outpatient care used outside the district of residence, added in a sensitivity analysis, was not associated ({st((OC.IRR, OC.lo, OC.hi))}), and the tertiary-educated share remained credible. "
       f"The ratio of the 90th to the 10th percentile of smoothed annual district SMRs was {N['gap'][2011]['ratio']:.2f} in 2011 and {N['gap'][2024]['ratio']:.2f} in 2024. "
       f"Kendall's W was {N['kendall']['2011-2019']:.2f} over 2011–2019 and {N['kendall']['2020-2024']:.2f} over 2020–2024. In emerging hot spot analysis, {N['ehsa'].get('Sporadic hot', 0)} districts were sporadic hot spots, {N['ehsa'].get('New hot', 0)} a new hot spot, {N['ehsa'].get('Sporadic cold', 0)} sporadic cold spots and {N['ehsa'].get('Consecutive cold', 0)} a consecutive cold spot; none was persistent.")
# ── Table S1 ──
DIR = {C.ALN: "+", C.LTC: "+", C.CHEW: "+", C.DM: "+", C.BLS: "+", C.TE: "−", C.GH: "−", C.WALK: "−", C.MPA: "−", C.FAC: "−"}
SRCN = {C.ALN: "KOSIS local indicators", C.LTC: "District panel", C.CHEW: "Community Health Survey", C.DM: "National health screening", C.BLS: "District panel", C.TE: "Census (district panel)", C.GH: "District panel",
        C.WALK: "Community Health Survey", C.MPA: "Community Health Survey", C.FAC: "Sports facility register",
        "urban_population_share": "KOSIS local indicators", "physicians_per_1000": "KOSIS local indicators", "sex_ratio": "KOSIS local indicators", "fiscal_independence": "KOSIS local indicators", "pop80_share": "Resident registration"}
UNIT = {C.ALN: "% of households", C.LTC: "per 100,000 aged ≥ 65", C.CHEW: "% aged ≥ 65", C.DM: "% of participants", C.BLS: "%", C.TE: "% of adults", C.GH: "per 100,000", C.WALK: "%", C.MPA: "%", C.FAC: "per 100,000",
        "urban_population_share": "%", "physicians_per_1000": "per 1,000", "sex_ratio": "ratio", "fiscal_independence": "%", "pop80_share": "%"}
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        m = _MT.loc[v]; rows.append([f"  {LABEL[v].split(' (')[0]}", UNIT[v], SRCN[v], f"{int(m.obs_year_min)}–{int(m.obs_year_max)}", ("Forced" if m.role == "forced" else DIR[v]), f"{_imp(v)}"])
TF("Table S1 Source, unit, observed years, expected direction and filled cells for each district characteristic, 229 districts, Republic of Korea, 2011–2024", ["Characteristic", "Unit", "Source", "Years", "Direction", "Filled cells"], rows,
   "KOSIS, Korean Statistical Information Service; ratio, men per 100 women; forced, in every model. Expected directions were set before any covariate model was fitted. Filled cells of 3,206 district-years: interpolation within districts, district means or yearly means. "
   "Basic livelihood recipient shares that collapsed in 2021–2023 in the wards of cities with general wards were corrected with city totals before analysis; these corrections are not counted as filled cells. Negative control exposures (separate model): hit-and-run collisions, a traffic-culture index and fires per 10,000 residents.")
# ── Table S2 우도 ──
LN = [("poisson", "Poisson"), ("nbinomial", "Negative binomial"), ("zeroinflatedpoisson1", "Zero-inflated Poisson"), ("zeroinflatednbinomial1", "Zero-inflated negative binomial"), ("poisson+obs_iid", "Poisson with observation-level effect")]
rows = [[lab, f"{L['WAIC']:.1f}", f"{L['DIC']:.1f}", f"{L['neg_logscore']:.1f}", "–" if pd.isna(L["zero_prob"]) else f"{L['zero_prob']:.4f}", "–" if pd.isna(L["size"]) else f"{L['size']:.1f}", "–" if pd.isna(L["expected_zeros"]) else f"{L['expected_zeros']:.0f}"] for k, lab in LN for L in [N["lik"][k]]]
TF("Table S2 Likelihood comparison for skin-disease deaths with forced controls and the same random effects, 3,206 district-years, Republic of Korea, 2011–2024", ["Likelihood", "WAIC", "DIC", "−Σ log CPO", "Zero probability", "Size", "Expected zeros"], rows,
   f"WAIC, widely applicable information criterion; DIC, deviance information criterion; CPO, conditional predictive ordinate; size, negative binomial size parameter; –, not applicable. Observed district-years with no death: {N['zeros']}. "
   "Expected zeros are the sum of posterior-mean probabilities of a zero count. The principal model used the negative binomial likelihood, chosen before covariates were added by the pre-specified comparison with Poisson; the Poisson model with an observation-level effect gave the same conclusions (Table S3).", fs=8)
# ── Table S3 사양 ──
NAMES = [("principal", "Principal model"), ("KH_typeI", "Knorr-Held type I"), ("KH_typeII", "Knorr-Held type II"), ("KH_typeIII", "Knorr-Held type III"), ("KH_typeIV", "Knorr-Held type IV"),
         ("icar_besag", "ICAR district effect"), ("iid_only", "IID district effect"), ("no_spatial", "No district effect"), ("knn3", "3 nearest neighbours"), ("knn4", "4 nearest neighbours"), ("knn5", "5 nearest neighbours"),
         ("pc_phi_flat", "Flat prior on mixing"), ("pc_relaxA", "Relaxed priors A"), ("pc_relaxB", "Relaxed priors B"),
         ("B3_smooth_forced", "Smoothed forced controls"), ("C1_poisson_lognormal", "Poisson, observation effect"), ("C2_rw2_year", "RW2 year effect"), ("C3_ar1_year", "AR1 year effect"), ("C4_sido_year_iid", "Province-by-year effect"), ("D1_spatial_plus", "Spatial+-type"),
         ("E0_nolag_from2012", "No lag, from 2012"), ("E1_lag1", "Lag 1 year"), ("E0_nolag_from2013", "No lag, from 2013"), ("E2_lag2", "Lag 2 years"), ("F3_extreme_R7", "Extreme values refilled"), ("G1_kchs_ma3", "Survey 3-year averages"), ("H4_odd_years", "Odd years only"), ("H4_even_years", "Even years only"),
         ("sa", "Age-only expected deaths"), ("s8", "Ten age groups in E"), ("s2", "Share aged 80+ omitted"), ("s577", "Queen graph, 577 edges"),
         ("bw_twoway", "Between and within components"), ("H1_nco_TRANS", "Transport-injury deaths (comparison)"), ("H1_nco_GCA", "Gastric cancer patients (comparison)")]
SS = {**N["s43"], **N["s41"]}; WA = {**N["s43_waic"], **N["s41_waic"]}
for v in ("s577", "s2", "s8", "sa"): SS.update({(v, c): t for c, t in N["sens"][v].items()}); WA[v] = float(pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_fit.csv")).WAIC.iloc[0])
WA["principal"] = N["waic_main"]; SS.update({("principal", c): (r["IRR"], r["lo"], r["hi"], r["cred"]) for c, r in N["main"].items()})
SS[("bw_twoway", C.TE)] = N["bw"][C.TE + "__within"]
def cell(a, v): t = SS.get((a, v)); return "–" if t is None else st(t)
HN = {C.TE: "Tertiary-educated adults", C.P80: "Population aged ≥ 80 years", C.ALN: "Older-adult single-person households", C.GH: "General hospitals"}
rows = [[lab, f"{WA[a]:.0f}" if a in WA and not a.startswith("H1_") else "–"] + [cell(a, v) for v in (C.TE, C.P80, C.ALN, C.GH)] for a, lab in NAMES]
TF("Table S3 Rate ratios per 1 standard deviation across alternative specifications and comparison outcomes, 229 districts, Republic of Korea, 2011–2024", ["Specification", "WAIC"] + [HN[v] for v in (C.TE, C.P80, C.ALN, C.GH)], rows,
   "Values are rate ratios (95% credible intervals) per 1 standard deviation; –, not estimated or omitted from the model. For the between and within row, the tertiary-educated value is the within-district component (between-district component "
   f"{st(N['bw'][C.TE + '__between'])}). For the Spatial+-type model, rate ratios are per 1 standard deviation of the residualised covariate. Comparison outcomes were fitted with the same covariates and model. WAIC: widely applicable information criterion (not comparable across outcomes or numbers of years); ICAR: intrinsic conditional autoregressive; IID: independent and identically distributed; RW2: second-order random walk; AR1: first-order autoregressive; E: expected deaths. "
   f"Omitting each province: tertiary-educated share credible in {N['leaveout'][('province', C.TE)][1]} of {N['leaveout'][('province', C.TE)][0]}; omitting each year: {N['leaveout'][('year', C.TE)][1]} of {N['leaveout'][('year', C.TE)][0]}. Post hoc rows for the reversed associations used existing fits only.", fs=7)
# ── Table S4 핫·콜드 ──
EN = {"서울시": "Seoul", "부산시": "Busan", "대구시": "Daegu", "인천시": "Incheon", "광주시": "Gwangju", "대전시": "Daejeon", "울산시": "Ulsan", "세종시": "Sejong", "경기도": "Gyeonggi-do", "강원도": "Gangwon-do", "충청북도": "Chungcheongbuk-do",
      "충청남도": "Chungcheongnam-do", "전라북도": "Jeollabuk-do", "전라남도": "Jeollanam-do", "경상북도": "Gyeongsangbuk-do", "경상남도": "Gyeongsangnam-do", "제주도": "Jeju"}
ROM = json.load(open(os.path.join(HERE, "district_romanization.json"), encoding="utf-8"))   # 공식 영문 시군구명(행정안전부 표기), 핫·콜드 69곳
S6 = N["s6"].copy(); S6["sido"] = S6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]; S6["sgg"] = [r[len(s):] for r, s in zip(S6.fbd_region, S6.sido)]
rom = lambda region: ROM[region]
rows = []
for cls, lab in (("hotspot", "Hot spots"), ("coldspot", "Cold spots")):
    q = S6[S6["class"] == cls].sort_values(["sido", "RR"], ascending=[True, cls != "hotspot"]); rows.append(["__H__", f"{lab} ({len(q)})"])
    for r in q.itertuples(): rows.append([f"  {EN[r.sido]}", rom(r.fbd_region), f"{r.RR:.2f} ({r.lo:.2f}–{r.hi:.2f})", f"{r.P_gt1:.3f}", f"{r.SIR_obs:.2f}"])
TF("Table S4 Residual hot spots and cold spots of skin-disease deaths, 229 districts, Republic of Korea, 2011–2024", ["Province", "District", "Residual spatial RR (95% CrI)", "P(RR > 1)", "Observed SMR"], rows,
   "RR, rate ratio from the district effect of the principal model; CrI, credible interval; SMR, standardised mortality ratio over 14 years. Hot spots: posterior probability of RR > 1 above 0.95; cold spots: below 0.05. Because this one-sided criterion differs from exclusion of 1 by the two-sided 95% CrI, some intervals include 1. Exploratory; not adjusted for multiple comparisons.", fs=7)
assert not any(isinstance(r[1], str) and re.search(r"[가-힣]", r[1]) for r in rows if r[0] != "__H__"), "untranslated district name"
# ── STROBE ──
MH = [x[0] for x in C.METHODS]; RH = [x[0] for x in C.RESULTS]
# JDDG: each STROBE item must cite the manuscript content explicitly (quoted text), not page/paragraph only.
from docx import Document as _Doc
def _ptext(p):   # paragraph text without superscript citation numbers
    return "".join(r.text for r in p.runs if not (r.font.superscript or (r._r.rPr is not None and r._r.rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}vertAlign') is not None)))
_PT = [re.sub(r"\s+", " ", _ptext(p)).strip() for p in _Doc(os.path.join(OUT, "Manuscript_JDDG_SKND.docx")).paragraphs]
def Q(anchor, n=34):
    par = next((t for t in _PT if anchor in t), None); assert par, ("STROBE anchor missing", anchor)
    i = par.find(anchor); st = par.rfind(". ", 0, i); st = 0 if st < 0 else st + 2
    if ": " in par[:i] and par[:i].rfind(": ") > st and par.startswith(("Background and objectives", "Patients and methods", "Results", "Conclusions")): st = par.rfind(": ", 0, i) + 2
    en = par.find(". ", i); en = len(par) if en < 0 else en + 1
    w = par[st:en].split(); return "\u201c" + (" ".join(w[:n]) + (" \u2026" if len(w) > n else "")) + "\u201d"
MM = "Material and methods"
CK = [("Title and abstract", "1", "Title page; Abstract, " + Q("Ecological study of all")), ("Background/rationale", "2", "Introduction, " + Q("Within-country geography of deaths")), ("Objectives", "3", "Introduction, final paragraph, " + Q("This study described the district geography")),
      ("Study design", "4", f"{MM}, {MH[0]}, " + Q("This ecological study covered all")), ("Setting", "5", f"{MM}, {MH[0]}, " + Q("Annual deaths by underlying cause")), ("Participants", "6", f"{MM}, {MH[0]}, " + Q("Districts were joined across sources")),
      ("Variables", "7", f"{MM}, {MH[1]}; {MH[2]}; Table S1, " + Q("Ten characteristics were fixed before")), ("Data sources/measurement", "8", f"{MM}, {MH[1]}; Appendix S1, " + Q("Expected deaths were obtained by indirect")),
      ("Bias", "9", f"{MM}, {MH[2]}; Table S3, " + Q("Three negative control exposures")), ("Study size", "10", f"{MM}, {MH[0]}, all {C.N['n_districts']} districts and {C.N['n_rows']:,} district-years"), ("Quantitative variables", "11", f"{MM}, {MH[2]}, " + Q("All characteristics were standardized to mean 0")),
      ("Statistical methods", "12", f"{MM}, {MH[3]}; Appendix S1; Table S2, " + Q("The principal model was negative binomial")), ("Participants (flow)", "13", "Not applicable (aggregate district data; no exclusions)"),
      ("Descriptive data", "14", f"Results, {RH[0]}; Table 1, " + Q("skin-disease deaths over 2011")), ("Outcome data", "15", f"Results, {RH[0]}; Table 1; Figure 1, " + Q("The age-standardized rate fell from")),
      ("Main results", "16", f"Results, {RH[2]}; Table 2; Figures 2 and 3, " + Q("Death rates were higher with a larger share")), ("Other analyses", "17", f"Results, {RH[2]}; Tables S2–S4, " + Q("The tertiary-educated share was credible in")),
      ("Key results", "18", "Discussion, first paragraph, " + Q("After standardization for sex and age, district rates")), ("Limitations", "19", "Discussion, Limitations, " + Q("This was an ecological study, and district")), ("Interpretation", "20", "Discussion, " + Q("Its association with transport-injury deaths shows")), ("Generalizability", "21", "Discussion, Conclusions, " + Q("Because district rankings changed between years")),
      ("Other information (funding, code)", "22", "Funding; Data availability, " + Q("The analysis code that generates"))]
J.page_break()
J.table_fit("Appendix S2 STROBE checklist for this ecological study", ["Item", "No.", "Where reported, with the manuscript text"], [[a, b, c] for a, b, c in CK], "", fs_max=8, title_bold=True)
foot_row(J, "STROBE: Strengthening the Reporting of Observational Studies in Epidemiology.", 8, 12)
ps = os.path.join(OUT, "Supporting_Information_JDDG_SKND.docx"); J.doc_title = "Supporting Information"; J.save(ps)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_sknd_esm", "--convert-to", "pdf", "--outdir", OUT, ps], check=True, capture_output=True)
print("saved", os.path.basename(ps))
K = TX(cite="bracket"); K.para("<b>STROBE checklist</b>"); K.para(f"Manuscript \"{DTITLE}\"")
K.table_fit("STROBE checklist for this ecological study", ["Item", "No.", "Where reported, with the manuscript text"], [[a, b, c] for a, b, c in CK], "", fs_max=9, title_bold=True)
foot_row(K, "Section names refer to the main manuscript and the Supporting Information.", 8, 12)
pk = os.path.join(OUT, "STROBE_Checklist_JDDG_SKND.docx"); K.doc_title = "STROBE checklist"; K.save(pk)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_sknd_esm", "--convert-to", "pdf", "--outdir", OUT, pk], check=True, capture_output=True)
print("saved", os.path.basename(pk))
