# 47K — SKND 우도 비교 보조(2026-11-13). 강제통제 5 + BYM2(593) + RW1 + 연도 iid, offset = E_sexage(std3 패널 E).
#  Poisson · NB · ZIP(type 1) · ZINB(type 1) · Poisson+관측 iid(로그정규) 5종: WAIC·DIC·−Σlog CPO, 사후 평균으로 기대 0칸 수(관측 675 대조).
#  사용(01_스크립트/에서): Rscript 47K_sknd_likelihood.R   산출: 04_분석/SKND/results_std3/S47K_likelihood.csv
suppressPackageStartupMessages({library(INLA);library(jsonlite)})
inla.setOption(num.threads="1:1")
D<-file.path("..","04_분석","SKND");OUT<-file.path(D,"results_std3");dir.create(OUT,showWarnings=FALSE)
S<-fromJSON(file.path(D,"config_SKND_std3.json"))
DD<-read.csv(file.path(D,"panel_SKND_std3.csv"),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE)
g<-inla.read.graph(file.path(D,"graph_593.graph"))
suppressPackageStartupMessages(library(sf))
SHP<-Sys.getenv("ST_SHP",file.path(normalizePath(file.path(dirname(sub("--file=","",grep("--file=",commandArgs(),value=TRUE))),"..")),"data","boundary","final.shp"))
G<-st_read(SHP,quiet=TRUE);G$region<-enc2utf8(G$region);DD$fbd_region<-enc2utf8(DD$fbd_region);stopifnot(g$n==nrow(G),all(DD$fbd_region%in%G$region))
DD$area<-match(DD$fbd_region,G$region)   # 81과 같은 노드 순서(final.shp)
DD$time<-DD$year-min(DD$year)+1;DD$yiid<-DD$time;DD$obs<-seq_len(nrow(DD))
pc<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)),phi=list(prior="pc",param=c(0.5,2/3)));pcp<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)))
base<-paste("cases ~ 1 +",paste(sprintf("`%s`",S$forced),collapse="+"),
  "+ f(area,model='bym2',graph=g,scale.model=TRUE,constr=TRUE,hyper=pc) + f(time,model='rw1',scale.model=TRUE,hyper=pcp) + f(yiid,model='iid',hyper=pcp)")
fit<-function(fam,extra=""){f<-as.formula(paste(base,extra));t0<-Sys.time()
  m<-inla(f,family=fam,data=DD,E=DD$E,control.fixed=list(mean=0,prec=4,mean.intercept=0,prec.intercept=0.001),
    control.compute=list(waic=TRUE,dic=TRUE,cpo=TRUE,config=FALSE),control.predictor=list(compute=TRUE,link=1),
    control.inla=list(control.vb=list(emergency=50)))
  mu<-m$summary.fitted.values$mean*DD$E;hp<-m$summary.hyperpar
  p0<-switch(fam,poisson=exp(-mu),
    nbinomial={k<-hp[grep("size",rownames(hp)),"mean"];(k/(k+mu))^k},
    zeroinflatedpoisson1={p<-hp[grep("zero-probability",rownames(hp)),"mean"];p+(1-p)*exp(-mu/(1-p))},
    zeroinflatednbinomial1={k<-hp[grep("size",rownames(hp)),"mean"];p<-hp[grep("zero-probability",rownames(hp)),"mean"];m1<-mu/(1-p);p+(1-p)*(k/(k+m1))^k})
  cpo<-m$cpo$cpo;nf<-sum(m$cpo$failure>0,na.rm=TRUE)
  data.frame(likelihood=paste0(fam,ifelse(extra=="","","+obs_iid")),WAIC=round(m$waic$waic,1),DIC=round(m$dic$dic,1),neg_logscore=round(-sum(log(cpo),na.rm=TRUE),1),cpo_fail=nf,
    zero_prob=ifelse(grepl("zeroinflated",fam),round(hp[grep("zero-probability",rownames(hp)),"mean"],4),NA),
    size=ifelse(grepl("nbinomial",fam),round(hp[grep("size",rownames(hp)),"mean"],2),NA),
    expected_zeros=round(sum(p0),1),observed_zeros=sum(DD$cases==0),minutes=round(as.numeric(difftime(Sys.time(),t0,units="mins")),2))}
R<-rbind(fit("poisson"),fit("nbinomial"),fit("zeroinflatedpoisson1"),fit("zeroinflatednbinomial1"),fit("poisson","+ f(obs,model='iid',hyper=pcp)"))
R$expected_zeros[R$likelihood=="poisson+obs_iid"]<-NA
write.csv(R,file.path(OUT,"S47K_likelihood.csv"),row.names=FALSE);print(R)
