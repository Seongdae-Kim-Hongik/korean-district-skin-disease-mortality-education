# build_jddg_sknd.py — SKND manuscript for JDDG (Journal der Deutschen Dermatologischen Gesellschaft), Original Article, Health Services Research section.
#  JDDG author guidelines (last update May 2026): American English; page 1 = title, author, institute, short title <=85 characters, corresponding author with postal address, phone, fax and email;
#   page 2 = structured abstract <=200 words (Background and objectives / Patients and methods / Results / Conclusions); body <=3,000 words, <=50 references; sections Introduction, Material and methods (ethics inside), Results, Discussion, Conflict of interest;
#   references numbered in order of citation, superscript, MEDLINE abbreviations in italics, up to 4 authors all named, more than 4 = 3 + et al; pages numbered bottom right; "Figure"/"Table" not abbreviated; declaration of AI translation tools.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from jkms_engine import JKMS
from american import brit
import content_sknd as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_sknd.json"), encoding="utf-8"))
DRAFT = os.path.join(MS, "draft", "01_manuscript.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
AI_STATEMENT = ("An AI translation tool was used. Claude (Anthropic; Claude Opus 5.5) translated the author's Korean draft into English and corrected English grammar and wording without changing content; it was not used to design the study, analyze data, interpret results or generate references. "
                "The author checked the accuracy of the terminology used and of all content and takes full responsibility for the content of this publication.")
AI_HEAD = "Declaration of use of AI"
PHONE = "+82-2-320-1114"
KEYWORDS = ["skin diseases", "mortality", "age-standardized death rate", "spatio-temporal analysis", "small-area analysis", "districts", "Republic of Korea", "aged, 80 and over", "educational status", "living alone", "pressure ulcer", "Bayesian spatial model"]
FUNDING = "None."
COI = "The author declares no conflicts of interest."
ETHICS = "The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent because only published aggregate statistics were used."
CONSENT = "Not applicable (aggregate statistics only; no patient-level data or images)."
ACK = "None."
def data_statement(): return (f"All source data are publicly available aggregate statistics from Statistics Korea, the Ministry of the Interior and Safety, the Korea Community Health Survey and the other national sources cited in the Material and methods. "
                             f"The analysis code that generates every number, table and figure is openly available on Zenodo (https://doi.org/{ZENODO}). The processed district-year data are available from the author on reasonable request.")

def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def all_keys():
    src = open(os.path.join(HERE, "content_sknd.py"), encoding="utf-8").read() + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys()

MON = ["January","February","March","April","May","June","July","August","September","October","November","December"]
def usdate(t):
    d, m, y = t.split(); return f"{m} {int(d)}, {y}"
def ref(k):   # JDDG: Author AA, Author BB. Title. <i>MEDLINE abbreviation</i>. Year;vol(issue):pages. 4 authors or fewer all, more than 4 = 3 + et al. DOI appended.
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. Available from: {r['url']}. {r['year']} (Last accessed {usdate(r['accessed'])})."
    au = r["authors"]; a = ", ".join(au) if len(au) <= 4 else ", ".join(au[:3]) + ", et al"
    t = r["title"].rstrip("."); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a}. {t} <i>{r['journal']}</i>. {r['year']}"
    if r.get("vol"): s += f";{r['vol']}" + (f"({r['issue']})" if r.get("issue") else "")
    if r.get("pages"): s += f":{r['pages']}"
    s += "."
    if r.get("doi"): s += f" doi:{r['doi']}"
    return s

class TX(JKMS):
    raw = False
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw:
            text = brit(text); text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

TAB1_COV = [("pop80_share", "Population aged ≥ 80 years, %"), ("older_single_household_share", "Older-adult single-person households, %"), ("ltc_hospitals_per_100k_65", "Long-term care hospitals per 100,000 aged ≥ 65 years"),
            ("chewing_discomfort_rate_65plus", "Chewing discomfort, aged ≥ 65 years, %"), ("screening_suspected_diabetes_share", "Suspected diabetes at screening, %"), ("basic_livelihood_rate", "Basic livelihood recipients, %"),
            ("tertiary_educated_share", "Tertiary-educated adults, %"), ("ext__genhosp_per100k", "General hospitals per 100,000"), ("walking_practice_rate", "Walking, %"), ("moderate_pa_rate", "Moderate-or-higher physical activity, %"),
            ("public_sports_facilities_per_100k", "Public sports facilities per 100,000")]
WC = ["W1_2011-15", "W2_2016-19", "W3_2020-24", "ALL"]; WH = ["2011–2015", "2016–2019", "2020–2024", "2011–2024"]
def table1():
    T = N["T1"]; A = N["asr"]
    def mean_asr(a, b): return sum(A[(y, "계")] for y in range(a, b + 1)) / (b - a + 1)
    rows = [["__H__", "Deaths"], ["  District-years, no."] + [f"{T[c]['n']:,}" for c in WC], ["  Skin-disease deaths (L00–L98), no."] + [f"{T[c]['cases']:,}" for c in WC],
            ["  District-years with no death, no."] + [f"{T[c]['zeros']:,}" for c in WC],
            ["  Age-standardised rate per 100,000*"] + [f"{mean_asr(a, b):.2f}" for a, b in ((2011, 2015), (2016, 2019), (2020, 2024), (2011, 2024))],
            ["  District SMR, median (P10–P90)†"] + [f"{T[c]['med']:.2f} ({T[c]['p10']:.2f}–{T[c]['p90']:.2f})" for c in WC], ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1_COV:
        mx = max(abs(T[c]['cov'][v][0]) for c in WC); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:.{dp}f} ({T[c]['cov'][v][1]:.{dp}f})" for c in WC])
    foot = ("P10–P90, 10th–90th percentile; SD, standard deviation; SMR, standardized mortality ratio. *Mean of annual national rates, 2020 resident population as standard. †Observed over sex- and age-standardised expected deaths summed over the period. "
            "Characteristics are district-year means; the five forced controls are in Table S1.")
    return (f"Table 1 Skin-disease deaths and district characteristics, {N['n_districts']} districts, Republic of Korea, 2011–2024", ["Characteristic"] + WH, rows, foot)

GROUPS = [("Care and frailty", [C.ALN, C.LTC, C.CHEW, C.DM]), ("Social conditions and access", [C.BLS, C.TE, C.GH]), ("Physical activity", [C.WALK, C.MPA, C.FAC]),
          ("Forced controls", ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"])]
LABEL = {C.ALN: "Older-adult single-person households (+)", C.LTC: "Long-term care hospitals (+)", C.CHEW: "Chewing discomfort, aged ≥ 65 years (+)", C.DM: "Suspected diabetes at screening (+)",
         C.BLS: "Basic livelihood recipients (+)", C.TE: "Tertiary-educated adults (−)", C.GH: "General hospitals (−)", C.WALK: "Walking (−)", C.MPA: "Moderate-or-higher physical activity (−)", C.FAC: "Public sports facilities (−)",
         "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians per 1,000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged ≥ 80 years"}
def f3(t): return f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
def table2():
    rows = []; assert sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"] and set(LABEL) == set(N["main"])
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k = N["s43"][(C.BEST_KH, v)]; s2 = N["sens"]["s2"].get(v); tr = N["nco"][("TRANS", v)]
            rows.append([f"  {LABEL[v]}", f3((m["IRR"], m["lo"], m["hi"])), f"{100*mv['cred_frac']:.0f}" if mv else "Forced", f3(k), f3(s2) if s2 else "Omitted", f3(tr)])
    foot = (f"CrI, credible interval; RR, rate ratio per 1 standard deviation; expected direction in parentheses. Principal model: negative binomial with a Besag–York–Mollié 2 district effect and random-walk and independent year effects, all characteristics and five forced controls (n = {N['n_rows']:,} district-years). "
            "*Share of the 200 covariate-subset models containing the characteristic in which the CrI excluded 1. †Knorr-Held type III space-time interaction added, the best-fitting interaction model. "
            "‡Same model without the share aged ≥ 80 years. §Transport-injury deaths as a comparison outcome with the same model.")
    return (f"Table 2 District characteristics and skin-disease deaths, {N['n_districts']} districts, Republic of Korea, 2011–2024",
            ["Characteristic", "Principal RR (95% CrI)", "Subsets credible, %*", "Type III RR (95% CrI)†", "Without share aged ≥ 80 years‡", "Transport-injury deaths§"], rows, foot)

FIGCAP = {
 1: ("Skin-disease deaths in the Republic of Korea, 2011–2024. (a) Deaths by year and sex. (b) National age-standardised death rates (2020 population) by sex. (c) Age distribution of deaths by sex, 2011–2024.",
     "Three panels. Stacked bars show 428 to 620 deaths a year, about two-thirds in women. Lines show the overall age-standardised rate falling from about 1.6 to 0.8 per 100,000, with similar declines in men and women. Stacked bars show that half of deaths in women and a quarter in men occurred at 85 years or older."),
 2: ("District geography of skin-disease deaths, 229 districts, Republic of Korea, 2011–2024. (a) Standardised mortality ratio (observed over sex- and age-standardised expected deaths, 14 years pooled). (b) Residual spatial rate ratio from the principal model. (c) Residual hot spots and cold spots (posterior probability of a rate ratio above 1 > 0.95 or < 0.05). Thick lines are province boundaries.",
     "Three maps of South Korea. Higher ratios and hot spots lie mainly in the south and south-west, including Busan, Gwangju and south-western Jeollanam-do, with scattered districts in Gangwon-do and Chungcheong; lower ratios and cold spots lie mainly in Seoul and Gyeonggi-do in the north-west."),
 3: ("Rate ratios per 1 standard deviation with 95% credible intervals for four characteristics across models, 229 districts, Republic of Korea, 2011–2024: principal model, Knorr-Held type III and type IV space-time models, Spatial+-type model, model without the share aged 80 years or older, independent district effect, and transport-injury deaths as a comparison outcome. The horizontal axis is on a log scale.",
     "Forest plot. Tertiary-educated adults lie below 1 in every model. Population aged 80 years or older lies above 1 in most models. Older-adult single-person households lie below 1 with spatial models but cross 1 when the share aged 80 years or older is omitted or the district effect is independent. General hospitals lie near 1."),
}
SUPPINFO = ("Additional supporting information may be found in the online version of the article. Appendix S1 Supplementary methods and additional results. Table S1 Source, unit, observed years and expected direction of each district characteristic. "
            "Table S2 Likelihood comparison. Table S3 Rate ratios across alternative specifications. Table S4 Residual hot spots and cold spots. Appendix S2 STROBE checklist.")
def foot_row(J, text, sz=9, ls=13):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3], 8); J.counting = c

def bullets(J, D, head):
    J.para(f"<b>{head}</b>", before=6)
    for s in re.split(r"(?<=\.)\s+(?=[A-Z])", D[head][0]): J.para(f"• {s}")

def build(bw=0, aw=0):
    D = read_draft(); J = TX(cite="sup")
    J.para(f"<b>{TITLE}</b>")
    J.para("<b>Article category:</b> Original Article. <b>Section:</b> Health Services Research", before=6)
    J.para(f"<b>Short title:</b> {C.RUNNING}", before=6)
    J.para("Seongdae Kim", before=6); J.para(f"ORCID: https://orcid.org/{ORCID}"); J.para(AFFIL)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, {ADDRESS}. Phone: {PHONE}. Fax: not available. Email: kimsd@hongik.ac.kr", before=6)
    J.para(f"<b>Word count:</b> {bw} (main text, excluding abstract and references); abstract {aw}. <b>Tables:</b> 2. <b>Figures:</b> 3. <b>References:</b> {len(KEYS)}.", before=6)
    J.para(f"<b>Conflict of interest:</b> {COI}", before=6); J.para(f"<b>Funding sources:</b> {FUNDING}")
    J.para(f"<b>Data availability:</b> {data_statement()}"); J.para(f"<b>Ethics statement:</b> {ETHICS}")
    J.para(f"<b>Keywords:</b> {'; '.join(KEYWORDS)}", before=6)
    J.page_break(); J.head("Abstract", 1)
    for p in D["Abstract"]:
        m = re.match(r"^(Background and objectives|Patients and methods|Results|Conclusions):\s*(.*)$", p, re.S); J.para(f"<b>{m.group(1)}:</b> {m.group(2)}")
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    J.head("Material and methods", 1)
    for x in C.METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Results", 1)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    J.head("Conflict of interest", 1); J.para(COI)
    J.head("Acknowledgments", 1); J.para(ACK)
    J.head(AI_HEAD, 1); J.para(AI_STATEMENT)
    J.head("Funding", 1); J.para(FUNDING)
    J.head("Data availability", 1); J.para(data_statement())
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s = f"{i}. " + ref(k); rl.append(s); J.para(s)
    J.raw = False
    J.head("Supporting Information", 1); J.para(SUPPINFO)
    J.page_break(); J.head("Figure legends", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Figure {k}</b> {FIGCAP[k][0]}"); J.para(f"Alt text: {FIGCAP[k][1]}", after=6)
    J.page_break(); put_table(J, table1())
    J.new_page("landscape"); put_table(J, table2(), fs=8)
    return J, rl, D

def docx_bw(path):   # 본문 단어 수: Introduction ~ Discussion 끝(Acknowledgments 직전)
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    i = t.find("\nIntroduction\n"); j = re.search(r"\nConflict of interest\n", t).start(); assert 0 < i < j; return len(t[i:j].split())
def fix_orphans(path, heads, max_iter=8):
    from docx import Document
    fixed = set()
    for _ in range(max_iter):
        pdf = path.replace(".docx", ".pdf")
        subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_sknd_jddg", "--convert-to", "pdf", "--outdir", os.path.dirname(path), path], check=True, capture_output=True)
        pages = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout.split("\f"); orphan = None
        for pg in pages:
            ls = [re.sub(r"^\d+\s+", "", l.strip()) for l in pg.split("\n") if l.strip()]; ls = [l for l in ls if not re.fullmatch(r"\d+", l)]
            if ls and ls[-1] in heads:
                k = len(ls) - 1
                while k > 0 and ls[k - 1] in heads: k -= 1
                orphan = ls[k]; break
        if orphan is None: return
        if orphan in fixed: print("orphan persists, stop:", orphan); return
        fixed.add(orphan); d = Document(path)
        for p in d.paragraphs:
            if p.text.strip() == orphan:
                np_ = OxmlElement("w:p"); r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br); np_.append(r); p._p.addprevious(np_); break
        d.save(path); print("orphan fixed:", orphan)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_JDDG_SKND.docx"); D = read_draft()
    AB = [re.sub(r"^(Background and objectives|Patients and methods|Results|Conclusions):\s*", "", x) for x in D["Abstract"]]; aw = sum(len(x.split()) for x in AB)
    J, rl, D = build(); J.doc_title = "Manuscript"; J.save(p); bw = docx_bw(p)
    J, rl, D = build(bw, aw); J.doc_title = "Manuscript"; J.save(p); assert docx_bw(p) == bw
    heads = {"Abstract", "Introduction", "Material and methods", "Results", "Discussion", "References", "Figure legends", "Acknowledgments", "Acknowledgements", AI_HEAD, "Funding", "Conflict of interest", "Data availability", "Supporting Information"} | {x[0] for x in C.METHODS + C.RESULTS}
    fix_orphans(p, heads)
    open(os.path.join(OUT, "wordcount_jddg.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=3\nrunning_head_chars={len(C.RUNNING)}\n")
    open(os.path.join(OUT, "reference_list.txt"), "w").write("\n".join(rl) + "\n")
    print(f"body {bw} | abstract {aw} | refs {len(KEYS)}")
    assert bw <= 3000 and aw <= 200 and len(KEYS) <= 50 and len(C.RUNNING) <= 85
