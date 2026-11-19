#!/usr/bin/env python3
# 99c — 전체 사망(ALLD) 가설 풀용 추가 열(2026-11-12). 새 수집 없음: 이미 검증된 EXT 파일(같은 정의·같은 결합 규칙)을 코드 결합으로 모은다.
#  basic_livelihood_rate·tertiary_educated_share·genhosp_per100k·ill_defined_share  ← EXT_canonical_pool_CANM_261109(수급률 2021-23 양쪽 규칙 33칸 정정판)
#  em_specialists_per100k ← EXT_canonical_pool_STRK_261107 / im_specialists_per100k·unmet_need_rate ← ANEM_261111 / ltc_hospitals_per100k_65 ← ALZ_261107
#  산출: 02_패널/EXT_canonical_pool_ALLD_261112.csv
import os, unicodedata, numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); PAN = os.path.join(os.path.dirname(HERE), "02_패널")
def rd(f, cols):
    d = pd.read_csv(os.path.join(PAN, f), encoding="utf-8-sig"); d["fbd_region"] = d.fbd_region.map(NFC); return d[["year", "fbd_region"] + cols]
out = rd("EXT_canonical_pool_CANM_261109.csv", ["basic_livelihood_rate", "tertiary_educated_share", "genhosp_per100k", "ill_defined_share"])
for f, cols in [("EXT_canonical_pool_STRK_261107.csv", ["em_specialists_per100k"]), ("EXT_canonical_pool_ANEM_261111.csv", ["im_specialists_per100k", "unmet_need_rate"]), ("EXT_canonical_pool_ALZ_261107.csv", ["ltc_hospitals_per100k_65"])]:
    out = out.merge(rd(f, cols), on=["year", "fbd_region"], how="left", validate="one_to_one")
# 수급률 정정판 재확인: 2021-23이 (2020·2024 평균)의 0.2배 미만·5배 초과인 칸 0
r = out.fbd_region.map(out[out.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate.mean())
assert not (out.year.isin([2021, 2022, 2023]) & ((out.basic_livelihood_rate < 0.2 * r) | (out.basic_livelihood_rate > 5 * r))).any()
B = rd("EXT_canonical_pool_ANEM_261111.csv", ["basic_livelihood_rate"]).merge(out[["year", "fbd_region", "basic_livelihood_rate"]], on=["year", "fbd_region"])
assert np.allclose(B.iloc[:, 2], B.iloc[:, 3]), "ANEM·CANM 수급률 정정판 불일치"
assert len(out) == 3206 and out.fbd_region.nunique() == 229 and out.notna().all().all(), out.isna().sum()
out.sort_values(["fbd_region", "year"]).to_csv(os.path.join(PAN, "EXT_canonical_pool_ALLD_261112.csv"), index=False, encoding="utf-8-sig")
print("[99c-alld] 저장", out.shape, "수급률 정정판 일치·결측 0")
