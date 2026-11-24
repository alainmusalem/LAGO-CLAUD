import json,re,numpy as np
from PIL import ImageFont
from edl import *
FB="../assets/fonts/Poppins-Bold.ttf"
LINES={'P':[(2.0,7.0,3.18,6.12),(12.0,17.0,12.7,16.52),(22.0,26.5,22.86,25.98),(31.5,37.0,32.5,36.22),(42.5,45.0,43.24,44.38)],
       'R':[(6.5,13.0,7.4,10.52),(17.5,23.0,18.1,22.14),(27.0,32.6,28.16,32.1),(37.0,43.0,38.1,42.68),(45.0,50.5,46.0,50.0)]}
TR={'P':'../work2/tr_73356.json','R':'../work2/tr_73701.json'}
FIX={"Raúl":"RAÚL"}
FIXW={"COMPO":"COMPRO","000":"MIL",".000":"MIL"}   # correcciones de la transcripción (se comprobaron contra el audio)
def words(which):
    ws=[]
    for s in json.load(open(TR[which])):
        for w,a,b in s['w']:
            t=re.sub(r"[.;:¡!¿?]","",w.strip()).upper()
            t=FIXW.get(t,t)
            if t: ws.append((t,a,b))
    return ws
def to_edit(which,t):
    m,tot=edit_time_map()
    for te0,te1,a,c in m:
        s0=a if which=='P' else c
        if s0-0.05<=t<=s0+(te1-te0)+0.05: return te0+(t-s0)
    # en hueco: acercar al segmento más próximo
    best=min(m,key=lambda r:min(abs(t-(r[2] if which=='P' else r[3])),abs(t-((r[2] if which=='P' else r[3])+r[1]-r[0]))))
    s0=best[2] if which=='P' else best[3]; return best[0]+min(max(t-s0,0),best[1]-best[0])
def chunk(ws,maxw=470,size=70,maxn=3):
    f=ImageFont.truetype(FB,size); n=len(ws)
    INF=1e9; best=[INF]*(n+1); prv=[0]*(n+1); best[0]=0
    for j in range(1,n+1):
        for i in range(max(0,j-maxn),j):
            seg=ws[i:j]; txt=" ".join(x[0] for x in seg)
            if f.getlength(txt)>maxw and j-i>1: continue
            k=j-i; dur=seg[-1][2]-seg[0][1]
            c={1:2.5,2:0.0,3:0.3}[k]+(3.0 if dur<0.45 else 0)+0.1
            if k==1 and len(txt)<=3: c+=3
            if best[i]+c<best[j]: best[j]=best[i]+c; prv[j]=i
    out=[];j=n
    while j>0: i=prv[j]; out.append(ws[i:j]); j=i
    return out[::-1]
def build():
    caps=[]
    for which in 'PR':
        ws=words(which)
        for lo,hi,on,off in LINES[which]:
            lw=[w for w in ws if lo<=w[1]<hi]
            lw=[(t,max(a,on-0.02) if i==0 else a, min(b,off+0.05)) for i,(t,a,b) in enumerate(lw)]
            lw=[(t,a,max(b,a+0.12)) for t,a,b in lw]
            ch=chunk(lw)
            for i,c in enumerate(ch):
                st=c[0][1]; en=c[-1][2]
                if i+1<len(ch):
                    nxt=ch[i+1][0][1]; en=nxt if nxt-en<0.35 else en+0.12
                else: en=en+0.15
                caps.append((which," ".join(x[0] for x in c),to_edit(which,st)/SPEED,to_edit(which,en)/SPEED))
    caps.sort(key=lambda c:c[2])
    return caps
if __name__=="__main__":
    for c in build(): print(c[0],f"{c[2]:.2f}-{c[3]:.2f}",c[1])
