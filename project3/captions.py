import json,re,numpy as np
from PIL import ImageFont
from edl import *
FB="../assets/fonts/Poppins-Bold.ttf"
# (ventana de búsqueda de palabras lo,hi, inicio de voz, fin de voz[, clip]) en tiempos del clip; P siempre del clip POBRE
LINES={'P':[(1.5,6.5,2.10,5.48),(13.0,16.0,13.40,15.54),(22.5,28.6,23.00,28.20),(34.3,39.5,34.95,39.06),(46.0,49.5,46.60,48.96)],
       'R':[(8.0,13.6,8.55,13.10,'74454'),(14.0,22.2,17.08,21.54,'74454'),(27.0,34.2,27.50,33.54,'74345'),(38.5,45.0,39.15,44.22,'74454'),(47.8,54.0,48.40,53.54,'74454')]}
TR={c:f'../work3/tr_{c}.json' for c in ['74222','74345','74454']}
FIX={"Raúl":"RAÚL"}
FIXW={}   # correcciones de la transcripción (se comprobaron contra el audio)
def words(clip):
    ws=[]
    for s in json.load(open(TR[clip])):
        for w,a,b in s['w']:
            t=re.sub(r"[;:¡!¿?]","",w.strip()).upper()
            t=FIXW.get(t,t)
            if t: ws.append((t,a,b))
    return ws
def to_edit(which,t,clip=None):
    m,tot=edit_time_map()
    cand=[]
    for i,(te0,te1,a,c) in enumerate(m):
        s0=a if which=='P' else c
        if which=='R' and RCLIP[i]!=clip: continue
        cand.append((te0,te1,s0))
    for te0,te1,s0 in cand:
        if s0-0.05<=t<=s0+(te1-te0)+0.05: return te0+(t-s0)
    best=min(cand,key=lambda r:min(abs(t-r[2]),abs(t-(r[2]+r[1]-r[0]))))
    te0,te1,s0=best; return te0+min(max(t-s0,0),te1-te0)
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
