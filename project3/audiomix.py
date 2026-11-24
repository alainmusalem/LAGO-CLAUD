import numpy as np,subprocess,soundfile as sf
from scipy import signal
from edl import *
import voice
SR=48000
rng=np.random.default_rng(7)
def tone(f,dur,amp=1,harm=(1,),att=0.01,dec=None):
    t=np.arange(int(dur*SR))/SR
    y=sum((1/(h**1.3))*np.sin(2*np.pi*f*h*t) for h in harm)
    e=np.minimum(1,t/att)*(np.exp(-t/dec) if dec else 1)
    return (y*e*amp).astype(np.float32)
def add(buf,x,at):
    i=int(at*SR); n=min(len(x),len(buf)-i)
    if n>0 and i>=0: buf[i:i+n]+=x[:n]
def midi(n): return 440*2**((n-69)/12)
def music(dur,bpm=92):
    buf=np.zeros(int(dur*SR)+SR,np.float32); beat=60/bpm; bar=4*beat
    chords=[(57,60,64,69),(53,57,60,65),(48,55,60,64),(55,59,62,67)]  # Am F C G
    nb=int(dur/bar)+2
    for b in range(nb):
        ch=chords[b%4]; t0=b*bar
        for k,n in enumerate(ch):                       # pad
            for det in (-0.12,0.12):
                x=tone(midi(n-12)*2**(det/12),bar+0.6,0.10,(1,2,3),att=0.5,dec=None)
                x*=np.minimum(1,(len(x)-np.arange(len(x)))/(0.5*SR)).astype(np.float32)
                add(buf,x,t0)
        for s in range(8):                              # pluck arpeggio
            n=ch[[0,2,1,3,2,3,1,2][s]]+12
            add(buf,tone(midi(n),0.5,0.16,(1,2),att=0.004,dec=0.14),t0+s*beat/2)
        for q in (0,2):                                 # kick suave
            k=np.arange(int(0.3*SR))/SR
            add(buf,(np.sin(2*np.pi*(48+60*np.exp(-k*28))*k)*np.exp(-k*11)*0.30).astype(np.float32),t0+q*beat)
        for q in range(8):                              # hat
            h=rng.standard_normal(int(0.04*SR)).astype(np.float32)
            h=signal.sosfilt(signal.butter(2,7000,'hp',fs=SR,output='sos'),h)*np.exp(-np.arange(len(h))/SR/0.012)*0.05
            add(buf,h.astype(np.float32),t0+q*beat/2+beat/4*(q%2))
    return buf[:int(dur*SR)]
def riser(dur=1.45):
    n=int(dur*SR); t=np.arange(n)/SR
    noise=rng.standard_normal(n).astype(np.float32); out=np.zeros(n,np.float32)
    for i in range(0,n,960):
        fc=300*(12000/300)**(i/n); sos=signal.butter(2,[fc,min(fc*2.2,20000)],'bp',fs=SR,output='sos')
        out[i:i+960]=signal.sosfilt(sos,noise[max(0,i-960):i+960])[-len(out[i:i+960]):] if i>0 else signal.sosfilt(sos,noise[:960])
    env=(t/dur)**2.2
    sweep=np.sin(2*np.pi*np.cumsum(180*(8**(t/dur)))/SR)
    y=(out*3.0*env+sweep*0.25*env)*0.6
    y[-int(0.03*SR):]*=np.linspace(1,0,int(0.03*SR))
    return y.astype(np.float32)
def hit():
    k=np.arange(int(0.5*SR))/SR
    th=np.sin(2*np.pi*(45+90*np.exp(-k*22))*k)*np.exp(-k*9)
    nz=signal.sosfilt(signal.butter(2,[300,5000],'bp',fs=SR,output='sos'),rng.standard_normal(len(k)))*np.exp(-k*14)*0.35
    return ((th*0.9+nz)*0.7).astype(np.float32)
def pop():
    k=np.arange(int(0.12*SR))/SR
    return (np.sin(2*np.pi*(700+500*np.exp(-k*40))*k)*np.exp(-k*30)*0.9).astype(np.float32)
def click():
    k=np.arange(int(0.08*SR))/SR
    return ((np.sin(2*np.pi*1500*k)*np.exp(-k*90)*0.7)+rng.standard_normal(len(k))*np.exp(-k*300)*0.3).astype(np.float32)
CARD_T0=None
def build(out_dur,card_t0):
    mix,env,info,tot=voice.build()
    sf.write("../work3/voice_edit.wav",mix[:int(tot*SR)],SR)
    subprocess.run(["ffmpeg","-v","error","-y","-i","../work3/voice_edit.wav","-af","atempo=1.1","../work3/voice_fast.wav"],check=True)
    v,_=sf.read("../work3/voice_fast.wav"); v=v.astype(np.float32)
    N=int(out_dur*SR); V=np.zeros(N,np.float32); V[:min(N,len(v))]=v[:N]
    # envolvente de voz para ducking
    e=np.abs(V); e=signal.sosfilt(signal.butter(2,6,'lp',fs=SR,output='sos'),e)
    d=np.clip(e/ (np.percentile(e,95)+1e-9),0,1); duck=1-0.55*d
    M=music(out_dur+0.5)[:N]*duck
    M*=10**(-17/20)/ (np.sqrt(np.mean(M**2))+1e-9)*10**(-20/20)*10**(17/20)*10**(-4/20)   # nivel relativo a voz (-22 dBFS rms)
    fade=int(0.35*SR); M[-fade:]*=np.linspace(1,0,fade)
    M[:int(0.05*SR)]*=np.linspace(0,1,int(0.05*SR))
    S=np.zeros(N,np.float32)
    r=riser(1.45)*10**(-14/20); add(S,r,0.0); add(S,hit()*10**(-17/20),1.45)
    add(S,pop()*10**(-22/20),card_t0); add(S,click()*10**(-24/20),card_t0+1.0)
    out=V+M+S
    sf.write("../work3/mix_raw.wav",out,SR)
    return out
if __name__=="__main__":
    import sys
    dur=float(sys.argv[1]); ct=float(sys.argv[2])
    o=build(dur,ct)
    subprocess.run(["ffmpeg","-v","error","-y","-i","../work3/mix_raw.wav","-af","loudnorm=I=-15:TP=-2:LRA=7,alimiter=limit=0.79","-ar","48000","-ac","2","../work3/final_audio.wav"],check=True)
    for f,nm in [("../work3/mix_raw.wav","raw"),("../work3/final_audio.wav","final")]:
        r=subprocess.run(["ffmpeg","-i",f,"-af","ebur128=peak=true","-f","null","-"],capture_output=True,text=True).stderr
        print(nm,[l.strip() for l in r.splitlines() if "I:" in l or "Peak:" in l][-2:])
