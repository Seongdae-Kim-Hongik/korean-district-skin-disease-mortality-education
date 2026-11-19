# american.py — JDDG 규정(American English): 빌더가 원고·표·범례 문자열을 출력 직전에 미국식 철자로 바꾼다(참고문헌 서지는 원문 유지).
import re
WORDS = {"analyse": "analyze", "analysed": "analyzed", "analyses": "analyses", "analysing": "analyzing", "modelled": "modeled", "modelling": "modeling",
         "centre": "center", "centres": "centers", "centred": "centered", "neighbour": "neighbor", "neighbours": "neighbors", "neighbourhood": "neighborhood", "neighbourhoods": "neighborhoods",
         "behaviour": "behavior", "behaviours": "behaviors", "behavioural": "behavioral", "ageing": "aging", "colour": "color", "favour": "favor", "favourable": "favorable",
         "labelled": "labeled", "travelled": "traveled", "grey": "gray", "fibre": "fiber", "programme": "program", "programmes": "programs",
         "haemoglobin": "hemoglobin", "glycaemic": "glycemic", "anaemia": "anemia", "foetal": "fetal", "paediatric": "pediatric", "oedema": "edema", "equalled": "equaled", "neighbouring": "neighboring",
         "acknowledgement": "acknowledgment", "acknowledgements": "acknowledgments", "judgement": "judgment", "generalisability": "generalizability", "per cent": "percent", "tumour": "tumor", "haemorrhage": "hemorrhage"}
KEEP = {"raise", "raised", "raises", "arise", "arises", "otherwise", "exercise", "exercised", "advise", "advised", "comprise", "comprises", "comprised", "precise", "precisely", "concise", "wise", "rise", "rises",
        "surprise", "enterprise", "expertise", "promise", "premise", "noise", "praise", "revise", "revised", "supervise", "supervised", "televise", "devise", "devised", "disguise", "franchise", "merchandise", "compromise", "excise", "incise", "despise", "chastise", "improvise", "improvised", "demise", "poise", "cruise", "bruise", "guise", "paradise", "porpoise", "tortoise", "treatise", "anise", "increase", "decrease", "increased", "decreased", "case", "cases", "base", "based", "phase", "phases", "release", "released", "disease", "diseases", "these", "those", "close", "closed", "dose", "doses", "purpose", "purposes", "use", "used", "uses", "cause", "caused", "causes", "because", "house", "houses", "pause", "loose", "choose", "chose", "whose", "rose", "pose", "posed", "suppose", "supposed", "propose", "proposed", "expose", "exposed", "impose", "imposed", "compose", "composed", "oppose", "opposed", "dispose", "else", "false", "pulse", "sense", "dense", "response", "license", "intense", "immense", "tense", "expense", "defense", "offense", "verse", "inverse", "inversely", "reverse", "reversed", "diverse", "adverse", "converse", "nurse", "nurses", "worse", "course", "source", "sources", "horse", "purse", "lapse", "collapse", "eclipse", "ellipse", "glimpse", "rinse", "cleanse", "tease", "lease", "ease", "please", "cease", "crease", "grease", "geese", "cheese", "otherwise"}
def brit(t):   # 이름은 기존 빌더 호환(brit = 철자 변환기)
    if not t: return t
    def ise(m):
        w = m.group(0); low = w.lower()
        if low in KEEP: return w
        r = re.sub(r"is(e|ed|es|ing|ation|ations|er|ers)$", r"iz\1", w)
        return r
    t = re.sub(r"\b[A-Za-z]{3,}is(?:e|ed|es|ing|ation|ations|er|ers)\b", ise, t)
    t = t.replace("per cent", "percent")
    def word(m):
        w = m.group(0); r = WORDS.get(w.lower())
        if r is None: return w
        return r[0].upper() + r[1:] if w[0].isupper() else r
    return re.sub(r"\b[A-Za-z]+\b", word, t)
if __name__ == "__main__":
    print(brit("Expected counts were standardised and harmonised; ageing behaviour; analysed; modelled; centred; organisation; Generalisability; otherwise raised; revised; summarised; prioritise; penalised; characterised; Spatial+-type; diseases; precise; exercise; advise; comprises; utilisation; randomised"))
