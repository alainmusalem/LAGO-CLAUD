import numpy as np
from PIL import ImageFont
from edl import *
import captions as C0
SIZE=56; MAXW=470
F=ImageFont.truetype(C0.FB,SIZE)
def wrap(words):
    """devuelve líneas (1 o 2) balanceadas o None si no caben en 2 líneas"""
    txt=" ".join(words)
    if F.getlength(txt)<=MAXW: return [txt]
    best=None
    for k in range(1,len(words)):
        a=" ".join(words[:k]); b=" ".join(words[k:])
        w=max(F.getlength(a),F.getlength(b))
        if w<=MAXW and (best is None or w<best[0]): best=(w,[a,b])
    return best[1] if best else None
def chunk(ws,maxn=6):
    n=len(ws); INF=1e9; best=[INF]*(n+1); prv=[0]*(n+1); best[0]=0
    for j in range(1,n+1):
        for i in range(max(0,j-maxn),j):
            seg=ws[i:j]; ln=wrap([x[0] for x in seg])
            if ln is None: continue
            k=j-i; dur=seg[-1][2]-seg[0][1]
            c=1.5+{1:2.0,2:0.8,3:0.2,4:0.0,5:0.0,6:0.2}[k]+(2.5 if dur<0.5 else (0.8 if dur<0.7 else 0))
            if len(ln)==2 and min(len(ln[0]),len(ln[1]))<6: c+=1.0
            if best[i]+c<best[j]: best[j]=best[i]+c; prv[j]=i
    out=[];j=n
    while j>0: i=prv[j]; out.append(ws[i:j]); j=i
    return out[::-1]
def build():
    caps=[]
    for which in 'PR':
        for ln in C0.LINES[which]:
            lo,hi,on,off=ln[:4]; clip=ln[4] if which=='R' else PCLIP
            ws=C0.words(clip)
            lw=[w for w in ws if lo<=w[1]<hi]
            lw=[(t,max(a,on-0.02) if i==0 else a, min(b,off+0.05)) for i,(t,a,b) in enumerate(lw)]
            lw=[(t,a,max(b,a+0.12)) for t,a,b in lw]
            ch=chunk(lw)
            for i,c in enumerate(ch):
                st=c[0][1]; en=c[-1][2]
                if i+1<len(ch):
                    nxt=ch[i+1][0][1]; en=nxt if nxt-en<0.35 else en+0.12
                else: en=en+0.15
                toks=[x[0] for x in c]; toks[-1]=toks[-1].rstrip('.')
                caps.append((which,wrap(toks),C0.to_edit(which,st,clip)/SPEED,C0.to_edit(which,en,clip)/SPEED))
    caps.sort(key=lambda c:c[2]); return caps
def word_time(which,word,approx,clip=None):
    clip=clip or (PCLIP if which=='P' else '74454')
    ws=[w for w in C0.words(clip) if w[0].rstrip('.,')==word and abs(w[1]-approx)<1.0]
    w=ws[0]; return C0.to_edit(which,w[1],clip)/SPEED
if __name__=="__main__":
    for c in build(): print(c[0],f"{c[2]:.2f}-{c[3]:.2f}"," / ".join(c[1]))
