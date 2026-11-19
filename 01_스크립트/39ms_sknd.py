#!/usr/bin/env python3
# 39ms_sknd — 피부 질환 사망(SKND, L00-L98) 성×연령 간접표준화 E(E_sexage)(2026-11-13). 공유 원본 39ms_build_Esex_mort.py 불변, 사인 표에 한 줄 더해 실행.
#  사용: ST_FBDZIP=<창원 교정 인구> [ST_E2_PANEL_SUF=_std3] python3 39ms_sknd.py
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "39ms_build_Esex_mort.py"), encoding="utf-8").read()
a = 'TAG = sys.argv[1]; assert TAG in CAUSES, TAG; NC = CAUSES[TAG]'
assert src.count(a) == 1
src = src.replace(a, 'CAUSES["SKND"] = "피부 및 피하조직의 질환 (L00-L98)"\n' + a)
sys.argv = ["39ms_build_Esex_mort.py", "SKND"]
exec(compile(src, os.path.join(HERE, "39ms_build_Esex_mort.py"), "exec"), {"__file__": os.path.join(HERE, "39ms_build_Esex_mort.py"), "__name__": "__main__"})
