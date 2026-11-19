# cover_jddg_sknd.py — SKND JDDG cover letter. American English, 1쪽, 단독 저자 비인칭, 김성대 명의. 자료 중복 고지 금지(저자 결정), 제외 심사자는 포털 칸에만. IRB 번호 포함.
#  Zenodo는 공개(open) 게시, 커버레터에는 공개 DOI만. --draft면 DOI 자리표시자 허용.
import os, re, sys, datetime, subprocess
from docx import Document
from docx.shared import Pt, Cm
import content_sknd as C
from build_jddg_sknd import TITLE as DTITLE, ZENODO, ADDRESS
from american import brit
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out"); DRAFT = "--draft" in sys.argv
N = C.N; W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_jddg.txt")).read().split()); A0 = C.A0
if not DRAFT: assert ZENODO.startswith("10.5281/zenodo."), "공개 DOI 없음(투고 전 게이트)"
_d = datetime.date.today(); cl = [f"{_d:%B} {_d.day}, {_d.year}", "The Editors", "JDDG: Journal der Deutschen Dermatologischen Gesellschaft", "",
      "Dear Editors,",
      f"Please find enclosed the manuscript entitled \"{DTITLE}\" by Seongdae Kim, submitted as an Original Article for the Health Services Research section of JDDG.",
      f"Deaths assigned to diseases of the skin and subcutaneous tissue occur mostly in very old people and have been discussed as a possible signal of shortfalls in care, yet their geography within countries is rarely described. This secondary analysis of national data covers all {N['cases_total']:,} skin-disease deaths in the {N['n_districts']} districts of the Republic of Korea over 2011–2024. Yearly deaths were slightly higher at the end of the period than at the start, while the age-standardized rate nearly halved from {A0(2011):.2f} to {A0(2024):.2f} per 100,000, and {N['pct80']:.1f}% occurred at 80 years or older. "
      f"After sex and age standardization, district death rates were associated with the share of the population aged 80 years or older and, non-specifically, with lower education, with residual hot spots mainly in Busan and the south-west; the crude association with older-adult single-person households could not be separated from very old age, and single-year district rankings agreed poorly.",
      "These findings are relevant to dermatologists and to those who plan dermatologic and nursing care for frail older people, because they show where skin-disease deaths concentrate, the limits of interpreting that geography, and why single-year district figures should not be used alone to prioritize districts. "
      "The study used only published aggregate statistics; the Institutional Review Board of Hongik University approved it (7002340-202511-HR-012) and its continuing review (7002340-202611-HR-040).",
      "The manuscript has not been published previously, has not been submitted for publication elsewhere, and will not be submitted for publication elsewhere before a decision is reached concerning publication in JDDG.",
      f"The main text contains {int(W['body_words'])} words, with a structured abstract of {int(W['abstract_words'])} words, two tables, three figures and {W['refs']} references. Supporting Information and the completed STROBE checklist are provided as separate files. The analysis code is openly available on Zenodo (https://doi.org/{ZENODO}).",
      "The author used an AI translation tool, Claude (Anthropic), only for translation and English-language editing, checked the accuracy of the terminology, and takes full responsibility for the content.",
      "Thank you for considering this manuscript.", "", "Sincerely,", "",
      "Seongdae Kim, PhD (corresponding author)", ADDRESS, "Phone: +82-2-320-1114. Email: kimsd@hongik.ac.kr"]
d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.0
for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)
gap = False
for t in cl:
    if t == "": gap = True; continue
    p = d.add_paragraph(brit(t))
    if gap: p.paragraph_format.space_before = Pt(10); gap = False
d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Cover Letter"; d.core_properties.comments = ""
fp = os.path.join(OUT, "Cover_Letter_JDDG_SKND.docx"); d.save(fp)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_sknd_cl", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
txt = subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and re.search(r"7002340-?\s*202611-?\s*HR-040", txt) and not re.search(r"(?i)funding|competing|overlap|previously submitted|token|private link", txt), "문체·IRB·금지 항목"
pages = subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0]
assert pages == "1", pages; print("cover pages", pages, "draft" if DRAFT else "")
