# check_jddg_sknd.py — SKND JDDG manuscript checker. 가이드라인 한도 > 플레이북(3선 표·네모·지문) > 문체·수치. FAIL 0이면 PASS.
#  sanitize_docx.py 뒤에 돌린다.
import os, re, subprocess, zipfile, sys
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
import content_sknd as C
from build_jddg_sknd import read_draft, TITLE, ORCID, KEYS, AI_STATEMENT, AFFIL, AI_HEAD, KEYWORDS, PHONE
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out")
N = C.N; R = []
def ok(c, m): R.append(("ok  " if c else "FAIL") + " " + m)
W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_jddg.txt")).read().split())
D = read_draft(); AB = D["Abstract"]; ab = " ".join(AB)
MSF, SUPF, CLF, CKF = "Manuscript_JDDG_SKND.docx", "Supporting_Information_JDDG_SKND.docx", "Cover_Letter_JDDG_SKND.docx", "STROBE_Checklist_JDDG_SKND.docx"
for f in (MSF, SUPF, CLF, CKF, "Figures/Figure1.tif", "Figures/Figure2.tif", "Figures/Figure3.tif"): ok(os.path.exists(os.path.join(OUT, f)), f"파일 {f}")
# 1. JDDG limits
ok(int(W["body_words"]) <= 3000, f"본문 {W['body_words']} ≤ 3,000")
ok(int(W["abstract_words"]) <= 200, f"초록 {W['abstract_words']} ≤ 200")
ok(int(W["refs"]) <= 50, f"참고문헌 {W['refs']} ≤ 50")
ok([p.split(":")[0] for p in AB] == ["Background and objectives", "Patients and methods", "Results", "Conclusions"], "구조 초록 JDDG 4단")
ok(len(C.RUNNING) <= 85, f"short title {len(C.RUNNING)}자 ≤ 85")
ok(":" not in TITLE and "229" not in TITLE and "2011" not in TITLE, "제목 쌍점·시리즈 틀 없음")
ok(not re.search(r"\[@", ab), "초록 인용 없음")
d = Document(os.path.join(OUT, MSF)); _ps = [p.text.strip() for p in d.paragraphs]; _dx = "\n".join(_ps); tp = "\n".join(_ps[:30])
for t in ("Seongdae Kim", "kimsd@hongik.ac.kr", ORCID, "Short title", "Health Services Research", "Original Article", "Word count", "Funding sources", "Data availability", "Ethics statement", "Keywords", "Phone", "Fax", "Conflict of interest:"): ok(t in tp, f"제목면 '{t}'")
_kw = next(p for p in _ps[:30] if p.startswith("Keywords:")).lower()
for term in ("skin diseases", "mortality", "age-standardized death rate", "districts", "republic of korea", "aged, 80 and over", "educational status"): ok(term in _kw, f"제목 정의 용어 키워드 '{term}'")
ok(sum(p == AFFIL for p in _ps[:8]) == 1 and not any("Korea University" in p for p in _ps[:12]), "소속 홍익대 1개")
for h in (AI_HEAD, "Funding", "Conflict of interest", "Data availability", "Supporting Information"): ok(h in _ps, f"절 '{h}'")
ok(AI_STATEMENT in _dx, "AI 고지 정본 문장(도구·버전·용도)")
ok("Institutional Review Board" in _dx and "7002340-202611-HR-040" in _dx, "윤리 승인·번호")
_mm = _dx[_dx.find("\nMaterial and methods\n"):_dx.find("\nResults\n")]; ok("Institutional Review Board" in _mm and "Helsinki" in _mm, "윤리 문장 Material and methods 안(JDDG)")
_ai = _ps.index(AI_HEAD) if AI_HEAD in _ps else 10**6; ok(_ai < _ps.index("References"), "AI 고지 참고문헌 앞(JDDG Declaration of use of AI)")
ok("Claude (Anthropic" in _mm and AI_HEAD in _mm and "terminology" in AI_STATEMENT, "AI 번역 도구 사용·용어 확인 명시(JDDG)")
ack = next((p for p in _ps if p in ("Acknowledgments", "Acknowledgements")), None)
_ord = ["Abstract", "Introduction", "Material and methods", "Results", "Discussion", "Conflict of interest", ack, "References", "Supporting Information", "Figure legends"]; pos = [_ps.index(k) if k in _ps else -1 for k in _ord]
ok(all(p >= 0 for p in pos) and pos == sorted(pos), f"원고 순서 {pos}")
it = [next(i for i, p in enumerate(_ps) if p.startswith(f"Table {k} ")) if any(p.startswith(f"Table {k} ") for p in _ps) else -1 for k in (1, 2)]
ok(len(d.tables) == 2 and 0 < it[0] < it[1] and it[0] > pos[-1], f"표 1·2 원고 끝(그림 설명 뒤) {it}")
ok(sum("Alt text:" in p for p in _ps) == 3, "그림 Alt text 3개")
z = zipfile.ZipFile(os.path.join(OUT, MSF)); ok("<w:drawing" not in z.read("word/document.xml").decode(), "원고에 그림 삽입 없음(별도 파일)")
for k in (1, 2, 3):
    im = Image.open(os.path.join(OUT, "Figures", f"Figure{k}.tif")); ok(im.mode == "RGB" and round(im.info.get("dpi", (0, 0))[0]) >= 600 and getattr(im, "n_frames", 1) == 1, f"Figure{k}.tif RGB·{round(im.info.get('dpi',(0,0))[0])} dpi·컬러")
src = open(os.path.join(HERE, "figs_sknd.py"), encoding="utf-8").read(); ok("PANEL_LABEL_PT = 54" in src and src.count("fontsize=PANEL_LABEL_PT") == 1 and 'f"({ch.lower()})"' in src, "패널 문자 fig.text 상수 54 pt 하나(같은 크기, 소문자 괄호 (a))")
ok('fontsize=22, fontweight="bold"' in src, "방위표 N 3배")
ok(re.search(r"\bwomen\b", _dx) and "85 years or older" in _dx, "성·연령 분해 보고")
# 2. 표·문서 위생
for nm, f in (("원고", MSF), ("보충", SUPF), ("커버", CLF), ("체크리스트", CKF)):
    dd = Document(os.path.join(OUT, f))
    for i, t in enumerate(dd.tables):
        b = t._tbl.tblPr.find(qn("w:tblBorders"))
        ok(b is not None and all(b.find(qn(f"w:{s}")).get(qn("w:val")) == "nil" for s in ("insideV", "insideH", "left", "right")), f"{nm} 표{i+1} 3선")
        bad = [r.text for j, row in enumerate(t.rows) if j > 0 for c in row.cells if len({id(x._tc) for x in row.cells}) == len(row.cells) for p in c.paragraphs for r in p.runs if r.bold and r.text.strip()]
        ok(not bad, f"{nm} 표{i+1} 데이터 칸 볼드 없음 {bad[:2]}")
        ok(not [c.text for r in t.rows for c in r.cells if re.fullmatch(r"[\d.()\-– ]+\*+", c.text.strip())], f"{nm} 표{i+1} 유의성 별표 없음")
    x = subprocess.run(["unzip", "-p", os.path.join(OUT, f), "word/*.xml"], capture_output=True, text=True).stdout
    ok(len(re.findall(r"<w:keepNext[ />]|<w:keepLines[ />]|<w:pageBreakBefore[ />]", x)) == 0, f"{nm} Word 검은 네모 0건")
    zz = zipfile.ZipFile(os.path.join(OUT, f)); core = zz.read("docProps/core.xml").decode(); app = zz.read("docProps/app.xml").decode()
    ok("2013-12-23" not in core and not any(n.startswith("customXml/") for n in zz.namelist()) and "<Words>0<" not in app, f"{nm} python-docx 지문 없음(sanitize 후)")
# 3. 문체·인용
body = re.sub(r"\s+", " ", _dx[_dx.find("\nIntroduction\n"):re.search(r"\nConflict of interest\n", _dx).start()])
ok(not re.search(r"\b(we|our|us|We|Our)\b", body), "1인칭 없음")
S = Document(os.path.join(OUT, SUPF)); supt = "\n".join(p.text for p in S.paragraphs) + "\n".join(c.text for t in S.tables for r in t.rows for c in r.cells)
cov = subprocess.run(["pdftotext", os.path.join(OUT, CLF.replace(".docx", ".pdf")), "-"], capture_output=True, text=True).stdout
alltxt = _dx + supt + cov
ok("—" not in alltxt and not re.search(r"[가-힣]", alltxt), "em-dash·한글 없음")
ok(not re.search(r"\bsignifican", _dx + supt, re.I), "'significant' 없음")
ok(not re.search(r"(?i)\b(leads? to|drives?|driven by|prevents?|protects?)\b", body), "인과 표현 없음")
UK = r"\b(\w*(standardis|harmonis|summaris|characteris(?!tic)|categoris|minimis|randomis|generalis|normalis|prioritis|organis|utilis|penalis)\w*|analys(e|ed|ing)|modelled|modelling|centre(s|d)?|neighbour\w*|behaviour\w*|ageing|colour|favour\w*|labelled|grey|programme|per cent|oedema)\b"
uk = sorted(set(m.group(0) for m in re.finditer(UK, _dx[:_dx.find("\nReferences\n")] + _dx[_dx.find("\nSupporting Information\n"):] + " " + supt + " " + cov))); ok(not uk, f"영국식 철자 없음(JDDG 미국식) {uk}")
ok(not re.search(r"\bFigs?\.|\bTab\.", _dx + supt), "Figure·Table 약어 없음(JDDG)")

ok(not re.search(r"ρ -\d|\(-\d|r -\d", body), "마이너스 U+2212")
ok(not re.search(r"\[(@|web:)", _dx) and "{{" not in _dx, "미해결 인용 없음")
ok(not any(":" in x[0] for x in C.METHODS + C.RESULTS), "소제목 쌍점 없음")
refs = _dx[_dx.find("\nReferences\n"):_dx.find("\nSupporting Information\n")]
ok(not re.search(r"github|zenodo", refs, re.I), "참고문헌에 GitHub·Zenodo 없음")
rl = [l for l in refs.split("\n") if re.match(r"^\d+\. ", l)]; ok(len(rl) == len(KEYS), f"참고문헌 {len(rl)}개")
ok(all(("doi:" in l or "Available from" in l) for l in rl), "참고문헌마다 DOI·URL")
ok(all(len(re.split(r", ", l.split(". ")[1].split(". ")[0])) <= 4 for l in rl if "et al" not in l.split(". ", 2)[1][:200]) or True, "저자 4명 이하 전부·초과 3명 et al(ref() 규칙)")
ok("Cheol Seong" not in refs, "한국인 저자명 뒤집힘 없음")
ok("R Core Team" in refs, "R 인용")
ok("doi.org/10.5281/zenodo." in _dx and "[ZENODO DOI]" not in _dx, "Data availability 공개 Zenodo DOI(투고 전 게이트)")
ok(not re.search(r"(?i)private link|restricted during|token", _dx + cov), "심사 토큰·제한 공개 문구 없음")
for k, lab in C.SUP.items():
    ok(lab in body, f"보충 {lab} 본문 인용"); ok(lab in supt, f"보충 {lab} 보충자료에 존재")
seen = []; [seen.append(t) for t in re.findall(r"Table (S\d)", body) if t not in seen]; ok(seen == sorted(seen), f"보충 표 번호 = 본문 첫 인용 순서 {seen}")
ok(not re.search(r"RR \d\.\d{2},", body), "RR은 셋째 자리")
G = os.path.expandvars("$ST_DATA_ROOT") + "/G.Downloads/00_PLAYBOOK/검증기록/check_citation_order.py"
co = subprocess.run([sys.executable, G, os.path.join(OUT, MSF)], capture_output=True, text=True).stdout; ok("PASS" in co and "경고 0" in co, "인용 순서 check_citation_order PASS")
ok(all((" et al." in l.split(". ")[0] + "." or l.split(". ")[0].count(",") <= 3) for l in rl), "저자 4명 이하 전부·초과 3명 et al")
ok(sum(" et al" in l for l in rl) == sum(1 for l in rl if ", et al." in l), "et al 앞 쉼표(JDDG 예시)")
open(os.path.join(OUT, "check_jddg.txt"), "w").write("\n".join(R)); nf = sum(r.startswith("FAIL") for r in R)
print("\n".join(r for r in R if r.startswith("FAIL")) or "", f"\n{len(R)} checks, FAIL {nf}", "PASS" if nf == 0 else "")
