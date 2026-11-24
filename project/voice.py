import subprocess,numpy as np,os
from edl import *
SR=48000
CH=("highpass=f=85,afftdn=nr=12:nf=-45:tn=1,"
    "equalizer=f=120:t=q:w=1:g=1.5,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.5:g=-2,equalizer=f=5500:t=q:w=1.2:g=-2,"
    "agate=threshold=0.012:ratio=2.2:attack=8:release=220:range=0.2,"
    "deesser=i=0.4:m=0.5:f=0.5,acompressor=threshold=-24dB:ratio=2:attack=15:release=160:makeup=2,alimiter=limit=0.8")
VW={'P':[(3.9,5.96),(13.48,15.78),(21.62,24.82),(29.28,33.48)],
    'R':[(7.26,11.34),(15.46,18.26),(25.30,28.62),(34.52,36.04)]}
CLIP={'P':'72522','R':'72631'}
def load(which):
    os.makedirs("../work",exist_ok=True)
    out=f"../work/voice_{which}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"../material_original/clip_{CLIP[which]}.mp4","-vn","-ac","1","-ar",str(SR),"-af",CH,out],check=True)
    return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",out,"-f","f32le","-ac","1","-"],capture_output=True).stdout,dtype=np.float32).copy()
def rms_db(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
def build():
    m,tot=edit_time_map()
    N=int(tot*SR)+SR
    mix=np.zeros(N,np.float32)
    env={'P':np.zeros(N,np.float32),'R':np.zeros(N,np.float32)}
    info=[]
    for which in 'PR':
        x=load(which)
        for (s,e) in VW[which]:
            # buscar segmento que contiene el habla
            for (te0,te1,a,c) in m:
                src0=a if which=='P' else c
                dur=te1-te0
                if s>=src0-0.2 and e<=src0+dur+0.05:
                    ps=max(s-0.07,src0); pe=min(e+0.10,src0+dur)
                    seg=x[int(ps*SR):int(pe*SR)].copy()
                    # nivelación por toma: RMS del habla -> -22 dBFS
                    g=-22-rms_db(seg[int(0.07*SR):-int(0.1*SR)] if len(seg)>SR//2 else seg)
                    seg*=10**(g/20)
                    f=int(0.04*SR); seg[:f]*=np.linspace(0,1,f); seg[-f:]*=np.linspace(1,0,f)
                    o=int((te0+(ps-src0))*SR)
                    mix[o:o+len(seg)]+=seg
                    env[which][o:o+len(seg)]=1
                    info.append((which,s,e,round(g,1),round(te0+(ps-src0),2),round(te0+(pe-src0),2)))
                    break
            else: raise SystemExit(f"sin segmento {which} {s},{e}")
    return mix,env,info,tot
if __name__=="__main__":
    mix,env,info,tot=build()
    for i in info: print(i)
    import soundfile as sf
