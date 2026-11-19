#!/usr/bin/env python3
# 99c — 피부 질환 사망(SKND, L00-L98) 가설 풀용 추가 열(2026-11-13). 새 수집 없음(99c_extra_canonical_pool_seps.py 복제).
#  공변량 ← EXT_canonical_pool_ALLD_261112(수급률 2021-23 양쪽 규칙 33칸 정정판)
#  종속변수 ← 02_패널/next5c_mort_counts_261113.csv(원표 DT_1B34E13 cC = 피부 및 피하조직의 질환, 일반구 합산·코드 결합, 계 = 기준 SQLite 3,206칸 일치)
#  산출: 02_패널/EXT_canonical_pool_SKND_261113.csv
import os, unicodedata, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); PAN = os.path.join(os.path.dirname(HERE), "02_패널")
def rd(f, cols):
    d = pd.read_csv(os.path.join(PAN, f), encoding="utf-8-sig"); d["fbd_region"] = d.fbd_region.map(NFC); return d[["year", "fbd_region"] + cols]
out = rd("EXT_canonical_pool_ALLD_261112.csv", ["basic_livelihood_rate", "tertiary_educated_share", "genhosp_per100k", "ill_defined_share", "em_specialists_per100k", "ltc_hospitals_per100k_65"])
mc = rd("next5c_mort_counts_261113.csv", ["cC", "total_chk"]).rename(columns={"cC": "sknd_deaths", "total_chk": "all_deaths"})
out = out.merge(mc, on=["year", "fbd_region"], how="left", validate="one_to_one")
r = out.fbd_region.map(out[out.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate.mean())
assert not (out.year.isin([2021, 2022, 2023]) & ((out.basic_livelihood_rate < 0.2 * r) | (out.basic_livelihood_rate > 5 * r))).any(), "수급률 정정 위반"
assert len(out) == 3206 and out.fbd_region.nunique() == 229 and out.notna().all().all(), out.isna().sum()
nat = out.groupby("year").sknd_deaths.sum(); assert nat[2011] == 470 and nat[2024] == 508, nat
out.sort_values(["fbd_region", "year"]).to_csv(os.path.join(PAN, "EXT_canonical_pool_SKND_261113.csv"), index=False, encoding="utf-8-sig")
print("[99c-sknd] 저장", out.shape, "피부 사망 2011/2024 =", int(nat[2011]), int(nat[2024]), "0칸", int((out.sknd_deaths == 0).sum()), "수급률 정정 위반 0·결측 0")
