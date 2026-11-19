# content_sknd.py — SKND Original Article Material and methods and Results text for JDDG (numbers come only from numbers_sknd).
#  JDDG author guidelines (May 2026): American English, structured abstract <=200 words (Background and objectives / Patients and methods / Results / Conclusions), body <=3,000 words, <=50 references, Figure/Table not abbreviated.
#  Sole author: no first person. No interpretation in Results. No colon in titles. Opposite-direction associations labelled post hoc; principal model unchanged.
from numbers_sknd import load, ROB, REV, PA, HYP, FORCED, P80, ALN, LTC, CHEW, DM, BLS, TE, GH, WALK, MPA, FAC
N = load()
def tci(t): return f"RR {t[0]:.3f}, 95% CrI {t[1]:.3f}–{t[2]:.3f}"
def ci(v): r = N["main"][v]; return tci((r["IRR"], r["lo"], r["hi"]))
M = N["main"]; T1 = N["T1"]
S43 = lambda a, v: N["s43"][(a, v)]
S41 = lambda a, v: N["s41"][(a, v)]
BW = lambda k: N["bw"][k]
NCO = lambda o, v: N["nco"][(o, v)]
SEN = lambda s, v: N["sens"][s][v]
KH = ("KH_typeI", "KH_typeII", "KH_typeIII", "KH_typeIV"); BEST_KH = min(KH, key=lambda a: N["s43_waic"][a]); assert BEST_KH == "KH_typeIII"
EN = {"서울시": "Seoul", "경기도": "Gyeonggi-do", "충청남도": "Chungcheongnam-do", "충청북도": "Chungcheongbuk-do", "부산시": "Busan", "전라남도": "Jeollanam-do", "광주시": "Gwangju",
      "경상남도": "Gyeongsangnam-do", "강원도": "Gangwon-do"}
def sidos(d):
    l = [f"{EN[k]} ({v})" for k, v in d.items()]; return ", ".join(l[:-1]) + " and " + l[-1]
TITLE = "Skin-disease mortality across Korean districts followed very old age and lower education, not living alone"
RUNNING = "Skin-disease mortality, very old age and education in Korean districts"
KEYWORDS = "skin diseases; pressure ulcer; cellulitis; mortality; aged, 80 and over; small-area analysis; Republic of Korea"
assert ":" not in TITLE and len(RUNNING) <= 85
SUP = {"methods": "Appendix S1", "covariates": "Table S1", "lik": "Table S2", "specs": "Table S3", "hot": "Table S4", "strobe": "Appendix S2"}   # 첫 인용 순서
sup = lambda k: SUP[k]
ALT = len(N["alt"]); RET = N["ret"]
A0 = lambda y: N["asr"][(y, "계")]
LIK = N["lik"]; NB = LIK["nbinomial"]; ZINB = LIK["zeroinflatednbinomial1"]; ZIP = LIK["zeroinflatedpoisson1"]; PO = LIK["poisson"]; POI = LIK["poisson+obs_iid"]
MV = lambda v: N["mv"][v]["cred_frac"]
LO = N["leaveout"]

METHODS = [
("Study design and data",
 f"This ecological study covered all {N['n_districts']} districts (urban wards, cities and counties) of the Republic of Korea, harmonised to 2024 boundaries, over 2011–2024 ({N['n_rows']:,} district-years), and is reported according to the STROBE statement [@vonelm2007strengthening] ({sup('strobe')}). "
 f"Annual deaths by underlying cause, sex and district of residence, and national deaths by cause, sex and 5-year age group, came from the national cause-of-death statistics, which cover all registered deaths [@web:kostat2026cause]; resident populations by sex and age came from resident registration [@web:mois2026population] ({sup('methods')}). "
 "Districts were joined across sources by administrative code only. Only published aggregate statistics were used, and no individual could be identified. The Institutional Review Board of Hongik University approved the study on 4 November 2025 (7002340-202511-HR-012) and its continuing review on 3 November 2026 (7002340-202611-HR-040) and waived informed consent. The study followed the principles of the Declaration of Helsinki."),
("Outcome and expected deaths",
 "The outcome was deaths with an underlying cause in the published item 'diseases of the skin and subcutaneous tissue' of the International Classification of Diseases, 10th revision (ICD-10 L00–L98), the only skin item available at district level; it includes pressure ulcer (L89), cellulitis (L03), bullous disorders and other conditions, which are not published separately. "
 "Expected deaths were obtained by indirect standardisation, applying national death rates for this chapter by year, sex and 18 age groups (5-year groups to 85 years or older) to each district population [@inskip1983methods]; the observed-to-expected ratio is the standardised mortality ratio (SMR). "
 "National age-standardised rates used the 2020 resident population as the standard."),
("District characteristics",
 f"Ten characteristics were fixed before any model was fitted, each with an expected direction ({sup('covariates')}). "
 "Care and frailty were represented by the share of all households consisting of one person aged 65 years or older (older-adult single-person households), the share of adults aged 65 years or older reporting chewing discomfort, long-term care hospitals per 100,000 residents aged 65 years or older, and the share of health-screening participants with suspected diabetes (all expected to raise deaths) [@jaul2018overview; @woo2026association; @carey2018risk]. "
 "Social conditions and access were represented by the share of basic livelihood security recipients (expected to raise deaths) and by the tertiary-educated share and general hospitals per 100,000 residents (expected to lower them) [@kim2019prevalence]. "
 "Because immobility underlies pressure ulcers [@coleman2013patient], age-standardised walking and moderate-or-higher physical activity from the Community Health Survey [@kang2015korea] and public sports facilities per 100,000 residents were included (all expected to lower deaths). "
 "Five controls were forced into every model: urban population share, physicians per 1,000 residents, sex ratio, fiscal autonomy and the population share aged 80 years or older. "
 "Three negative control exposures with no plausible effect on skin-disease deaths (hit-and-run collisions, a traffic-culture index and fires) were fitted in a separate model [@lipsitch2010negative]. All characteristics were standardised to mean 0 and standard deviation (SD) 1."),
("Statistical analysis",
 f"Before the ten hypothesis characteristics were added, five likelihoods (Poisson, negative binomial, zero-inflated Poisson, zero-inflated negative binomial and Poisson with an observation-level random effect) were compared with the same random effects ({sup('lik')}). "
 f"The principal model was negative binomial, chosen by a rule fixed before any covariate model was fitted: a lower widely applicable information criterion (WAIC) than Poisson for the forced-control model ({N['waic_nb']:,.1f} versus {N['waic_pois']:,.1f}) [@gelman2014understanding], with an offset of log expected deaths, a Besag–York–Mollié 2 district effect with penalised-complexity priors [@besag1991bayesian; @riebler2016intuitive; @simpson2017penalising] and random-walk and independent year effects, fitted by integrated nested Laplace approximation in R 4.6.0 [@rue2009approximate; @web:rcore2026]. The Poisson model with an observation-level effect had a lower WAIC than the negative binomial model and was refitted with all characteristics as an alternative specification. "
 "Rate ratios (RRs) per 1 SD are reported with 95% credible intervals (CrIs), and an association was called credible when its interval excluded 1; P values were not used. "
 "Residual hot spots and cold spots were districts whose posterior probability of a residual spatial RR above 1 exceeded 0.95 or fell below 0.05 (exploratory, not adjusted for multiple comparisons). "
 "Persistence of district rankings was measured by Kendall's W over the 14 annual SMRs and by Spearman correlations of SMRs between 2011–2015, 2016–2019 and 2020–2024; spatial autocorrelation by Moran's I [@moran1950notes].",
 f"Robustness was assessed in {N['mv_total']} models with random covariate subsets (robust when credible in at least 75% of the models containing the characteristic with at least 95% sign agreement) [@steegen2016increasing]; four Knorr-Held space-time interactions [@knorrheld2000bayesian]; refits in the three periods; between-district and within-district components entered together [@bell2015explaining]; {RET[TE][1]} alternative fits of likelihood, temporal structure, lags, spatial confounding [@dupont2022spatial] and covariate measurement; omission of each province and each year; and expected deaths from age alone or from ten age groups, a different adjacency graph and omission of the share aged 80 years or older ({sup('specs')}). "
 "Transport-injury deaths, which share area-level socioeconomic and age-structure determinants but not skin-specific pathways, and patients treated for gastric cancer, a marker of general medical care use, were fitted with the same model as comparison outcomes. For robust associations, E-values were computed [@vanderweele2017sensitivity]. "
 "Associations in the direction opposite to that expected were examined post hoc with these existing fits only, without changing the principal model. "
 "An AI translation tool, Claude (Anthropic; Claude Opus 5.5), was used only to translate the author's Korean draft into English and to edit English wording (see Declaration of use of AI)."),
]

RESULTS = [
("Deaths by year, sex and age",
 f"There were {N['cases_total']:,} skin-disease deaths over 2011–2024, between {N['per_year'][0]} and {N['per_year'][1]} a year ({N['n_y'][2011]} in 2011, a peak of {N['peak_n']} in {N['peak_year']} and {N['n_y'][2024]} in 2024; Table 1). "
 f"In the national age table, {N['pct65']:.1f}% of deaths occurred at 65 years or older, {N['pct80']:.1f}% at 80 years or older and {N['pct85']:.1f}% at 85 years or older, and {N['pct_women']:.1f}% were in women (Figure 1). "
 f"The age-standardised rate fell from {A0(2011):.2f} to {A0(2024):.2f} per 100,000 ({100*(A0(2024)/A0(2011)-1):.0f}%). "
 f"Of the {N['n_rows']:,} district-years, {N['zeros']} ({100*N['zeros']/N['n_rows']:.0f}%) had no death; the negative binomial model expected {NB['expected_zeros']:.0f}, and zero-inflated likelihoods estimated zero probabilities of {ZIP['zero_prob']:.3f} (Poisson) and {ZINB['zero_prob']:.3f} (negative binomial) without improving the WAIC ({ZINB['WAIC']:,.1f} versus {NB['WAIC']:,.1f}; {sup('lik')})."),
("Geography",
 f"The 14-year district SMR had a median of {T1['ALL']['med']:.2f} (10th–90th percentile {T1['ALL']['p10']:.2f}–{T1['ALL']['p90']:.2f}), and Moran's I of the pooled log SMR was {N['moran_pooled']:.2f}. "
 f"The spatially structured component accounted for {100*N['vp_spatial']:.0f}% of the variance of the linear predictor (mixing parameter φ {N['phi'][0]:.2f}, 95% CrI {N['phi'][1]:.2f}–{N['phi'][2]:.2f}). "
 f"There were {N['n_hot']} residual hot spots, in {sidos(N['hot_by_sido'])}, and {N['n_cold']} cold spots, in {sidos(N['cold_by_sido'])} (Figure 2; {sup('hot')}); {N['hot_by_sido']['부산시']} of the {N['n_busan']} districts of Busan were hot spots. "
 f"Annual Moran's I ranged from {N['moran_year'][0]:.2f} to {N['moran_year'][1]:.2f}. Rankings changed between years: Kendall's W was {N['kendall']['2011-2024']:.2f} over 2011–2024, and Spearman correlations of SMRs between periods were {N['rho_win'][0]:.2f}–{N['rho_win'][1]:.2f}. "
 f"Across districts, the 14-year SMR was correlated with the older-adult single-person household share (ρ {N['rho_raw']['aln']:.2f}), the share aged 80 years or older (ρ {N['rho_raw']['p80']:.2f}) and the tertiary-educated share (ρ {N['rho_raw']['te']:.2f}); the first two were correlated with each other (ρ {N['rho_aln_p80']:.2f})."),
("District characteristics",
 f"Adding the ten characteristics did not lower the WAIC ({N['waic_forced']:,.1f} for forced controls alone and {N['waic_main']:,.1f} with all characteristics; Tables S2 and S3). "
 f"Death rates were higher with a larger share aged 80 years or older ({ci(P80)}; 1 SD = {T1['ALL']['cov'][P80][1]:.1f} percentage points) and lower with a higher tertiary-educated share ({ci(TE)}; 1 SD = {T1['ALL']['cov'][TE][1]:.1f} percentage points). The share aged 80 years or older was credible in {ALT - 1} of {ALT} alternative specifications (not with odd years only, {tci(S41('H4_odd_years', P80))}) and in the type III model ({tci(S43('KH_typeIII', P80))}), but not in the type IV model ({tci(S43('KH_typeIV', P80))}) or without a district effect ({tci(S43('no_spatial', P80))}). "
 f"Against the expected directions, deaths were lower with a higher older-adult single-person household share ({ci(ALN)}) and higher with more general hospitals ({ci(GH)}). "
 f"Walking ({ci(WALK)}), moderate-or-higher physical activity ({ci(MPA)}), sports facilities ({ci(FAC)}), long-term care hospitals, chewing discomfort, suspected diabetes and livelihood recipients had intervals including 1, as did the three negative control exposures. Residual Moran's I was {N['moran_resid']:.2f}.",
 f"The tertiary-educated share was credible in {100*MV(TE):.0f}% of the covariate-subset models containing it, in all four Knorr-Held models (type III, the best-fitting, {tci(S43(BEST_KH, TE))}), in {ALT - 1} of {ALT} alternative specifications (not with even years only, {tci(S41('H4_even_years', TE))}), in {LO[('province', TE)][1]} of {LO[('province', TE)][0]} province omissions (not when Seoul was omitted) and in all {LO[('year', TE)][0]} year omissions, {RET[TE][0]} of {RET[TE][1]} fits in all (Figure 3; {sup('specs')}); "
 f"the within-district component was credible ({tci(BW(TE + '__within'))}) and the between-district component was not ({tci(BW(TE + '__between'))}). Its E-value was {N['evalue'][TE]['E_point']:.2f} (CrI limit {N['evalue'][TE]['E_limit']:.2f}). "
 f"The tertiary-educated share was also inversely associated with transport-injury deaths ({tci(NCO('TRANS', TE))}) and gastric cancer patients ({tci(NCO('GCA', TE))}), and the share aged 80 years or older with transport-injury deaths ({tci(NCO('TRANS', P80))}). "
 f"In the three periods, the number of credible characteristics was {N['win_ncred'][0]}, {N['win_ncred'][1]} and {N['win_ncred'][2]}; {N['n_inter_cred']} of the {N['n_inter']} characteristic-by-period interactions and none of the interactions with the post-2020 period were credible.",
 f"In post hoc checks, the inverse older-adult single-person household association was credible in {100*MV(ALN):.0f}% of subset models and in most spatial specifications (type IV, {tci(S43('KH_typeIV', ALN))}), but not when the share aged 80 years or older was omitted ({tci(SEN('s2', ALN))}), when the district effect was independent ({tci(S43('iid_only', ALN))}) or when no district effect was fitted ({tci(S43('no_spatial', ALN))}). "
 f"The general-hospital association was credible in {100*MV(GH):.0f}% of subset models; it remained credible with 1-year and 2-year lags and was not credible in the Spatial+-type model ({tci(S41('D1_spatial_plus', GH))}), the type IV model ({tci(S43('KH_typeIV', GH))}), with extreme values refilled or without the share aged 80 years or older."),
]

# 문장 주장 대조(결과표와 어긋나면 빌드 중단)
H = [v for v in M if M[v]["role"] == "hypothesis"]
assert {v for v in H if M[v]["cred"]} == {TE, ALN, GH} and M[TE]["IRR"] < 1 and M[ALN]["IRR"] < 1 and M[GH]["IRR"] > 1 and M[P80]["cred"] and M[P80]["IRR"] > 1
assert not any(M[v]["cred"] for v in PA + [LTC, CHEW, DM, BLS])
assert N["waic_main"] > N["waic_forced"]
assert all(S43(a, TE)[3] for a in KH) and BW(TE + "__within")[3] and not BW(TE + "__between")[3] and NCO("TRANS", TE)[3] and NCO("TRANS", TE)[0] < 1
assert all(SEN(s, TE)[3] for s in ("s577", "s2", "s8", "sa"))
assert not SEN("s2", ALN)[3] and not S43("iid_only", ALN)[3] and not S43("no_spatial", ALN)[3]
assert S41("E1_lag1", GH)[3] and S41("E2_lag2", GH)[3] and S43("KH_typeIV", ALN)[3] and not S41("D1_spatial_plus", GH)[3] and not S43("KH_typeIV", GH)[3] and not S41("F3_extreme_R7", GH)[3] and not SEN("s2", GH)[3]
assert POI["WAIC"] < NB["WAIC"] and ZINB["WAIC"] > NB["WAIC"] and ZINB["zero_prob"] < 0.01
assert list(N["hot_by_sido"])[0] == "부산시" and list(N["cold_by_sido"])[:2] == ["서울시", "경기도"]
assert A0(2024) < A0(2011) and N["n_y"][2024] > N["n_y"][2011]

if __name__ == "__main__":
    import re
    for x in METHODS + RESULTS: print("##", x[0], "\n", "\n\n".join(x[1:]), "\n")
    print("words M", sum(len(re.sub(r"\[@[^\]]+\]", "", t).split()) for x in METHODS for t in x[1:]), "R", sum(len(re.sub(r"\[@[^\]]+\]", "", t).split()) for x in RESULTS for t in x[1:]))
assert sum(S41(a, TE)[3] for a in N["alt"]) == ALT - 1 and not S41("H4_even_years", TE)[3]
assert sum(S41(a, P80)[3] for a in N["alt"]) == ALT - 1 and not S41("H4_odd_years", P80)[3]
