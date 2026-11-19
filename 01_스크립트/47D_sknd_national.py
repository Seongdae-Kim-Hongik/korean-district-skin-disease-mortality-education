#!/usr/bin/env python3
# 47D — SKND 전국 기술(2026-11-13): 성×5세 사망자수·사망률(DT_1B34E01) → 직접표준화율(2020 전국 인구 표준, 18구간 85+), 연령·성 구성.
#  산출: 04_분석/SKND/results_desc/S47D_national.csv, S47D_agesex.csv
import os, pandas as pd, numpy as np
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); O=f"{R}/04_분석/SKND/results_desc"
N=pd.read_csv(f"{R}/00_원천/D_사망_인구_암/DT_1B34E01_national_long.csv",encoding="utf-8-sig")
B=['0세','1 - 4세']+[f"{a} - {a+4}세" for a in range(5,85,5)]+['85 - 89세','90세이상']
s=N[N.cause.str.contains('L00-L98')&N.age.isin(B)&N.year.between(2011,2024)]
d=s.pivot_table(index=['year','sex','age'],columns='item',values='value',aggfunc='sum').reset_index()
d['pop']=np.where(d['사망률']>0,d['사망자수']/d['사망률']*1e5,np.nan)
# 사망 0인 칸의 인구: 같은 연도·성·연령 다른 사인 행에서 얻음
P=N[N.age.isin(B)&N.year.between(2011,2024)].pivot_table(index=['year','sex','age','cause'],columns='item',values='value',aggfunc='sum').reset_index()
P=P[(P['사망률']>0)&(P['사망자수']>=20)]; P['pop']=P['사망자수']/P['사망률']*1e5; pp=P.groupby(['year','sex','age'])['pop'].median()
d['pop']=d.set_index(['year','sex','age']).index.map(pp)
def band(a): return '0-4' if a in ('0세','1 - 4세') else ('85+' if a in ('85 - 89세','90세이상') else a.replace(' - ','-').replace('세',''))
d['band']=d.age.map(band); g=d.groupby(['year','sex','band'])[['사망자수','pop']].sum().reset_index()
std=g[(g.year==2020)&(g.sex=='계')].set_index('band')['pop']; w=std/std.sum()
rows=[]
for (y,sx),h in g.groupby(['year','sex']):
    h=h.set_index('band'); r=(h['사망자수']/h['pop']*1e5); rows.append(dict(year=y,sex=sx,deaths=int(h['사망자수'].sum()),crude=round(h['사망자수'].sum()/h['pop'].sum()*1e5,3),asr_2020=round(float((r*w).sum()),3),share85=round(h.loc['85+','사망자수']/h['사망자수'].sum(),3)))
T=pd.DataFrame(rows); T.to_csv(f"{O}/S47D_national.csv",index=False); print(T[T.sex=='계'].to_string(index=False)); print(T[T.sex!='계'].pivot(index='year',columns='sex',values='asr_2020'))
g.to_csv(f"{O}/S47D_agesex.csv",index=False)
a=g[g.sex!='계'].groupby(['sex','band'])['사망자수'].sum().unstack(0); print((a/a.values.sum()).loc[['70-74','75-79','80-84','85+']].round(3))
