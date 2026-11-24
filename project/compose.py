import cv2,numpy as np,subprocess,sys,os,glob
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from edl import *
import captions
W,H=1080,1920
FB="../assets/fonts/Poppins-Bold.ttf"; FX="../assets/fonts/Poppins-ExtraBold.ttf"
YEL=(0xFF,0xD7,0x21)   # #FFD721 (RGB)
SCALE=1.2; CX0=90; CY0=0           # encuadre fijo: recorte 900x1600 de la placa -> 1080x1920
TARGET={'P':315,'R':765}           # centro de cada personaje en la placa (-> 0.25 y 0.75 del encuadre final)
CROP={'P':(380,480,1080,1920),'R':(0,480,700,1920)}
CLIP={'P':'72522','R':'72631'}
def ss(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
# ---------------- placa de fondo ----------------
def build_plate():
    P=cv2.imread("../work/med_P.png").astype(np.float32); R=cv2.imread("../work/med_R.png").astype(np.float32)
    zone=slice(490,575)
    ratio=(P[:,zone].mean(1)/(R[:,zone].mean(1)+1e-3))            # por fila y canal
    ratio=cv2.GaussianBlur(ratio.astype(np.float32),(1,0),sigmaX=0.1,sigmaY=40)
    ratio=np.clip(ratio,0.88,1.12)
    Rg=R*ratio[:,None,:]
    x=np.arange(W,dtype=np.float32); w=ss(490,575,x)[None,:,None]      # 0 -> P, 1 -> R
    plate=P*(1-w)+Rg*w
    return plate,ratio
# ---------------- lectura de frames ----------------
class Reader:
    def __init__(s,which):
        s.p=subprocess.Popen(["ffmpeg","-v","error","-i",f"../material_original/clip_{CLIP[which]}.mp4","-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE,bufsize=W*H*3*2)
        s.i=-1; s.f=None
    def get(s,idx):
        while s.i<idx:
            b=s.p.stdout.read(W*H*3)
            if len(b)<W*H*3: break
            s.f=np.frombuffer(b,np.uint8).reshape(H,W,3); s.i+=1
        return s.f
def load_alpha(which,idx):
    a=cv2.imread(f"../work/alpha_{which}/{idx:05d}.png",0)
    if a is None: raise FileNotFoundError(f"{which} {idx}")
    return a.astype(np.float32)/255
def centroid(which,idxs):
    cs=[]
    for i in idxs:
        if not os.path.exists(f"../work/alpha_{which}/{i:05d}.png"): continue
        a=load_alpha(which,i)
        x0=CROP[which][0]
        rs=a.sum(1); r0=int(np.argmax(rs>6))
        band=a[r0+8:r0+120]           # cabeza
        m=band.sum(0)
        if m.sum()>50: cs.append(x0+(m*np.arange(len(m))).sum()/m.sum())
    return float(np.median(cs))
# ---------------- texto ----------------
def text_layer(txt,fontpath,size,fill,shadow_a=0.6,off=(0,4),blur=4,pad=24):
    f=ImageFont.truetype(fontpath,size); l,t,r,b=f.getbbox(txt)
    w=int(r-l+2*pad+abs(off[0])); h=int(b-t+2*pad+abs(off[1]))
    sh=Image.new("RGBA",(w,h),(0,0,0,0)); ImageDraw.Draw(sh).text((pad-l+off[0],pad-t+off[1]),txt,font=f,fill=(0,0,0,int(255*shadow_a)))
    sh=sh.filter(ImageFilter.GaussianBlur(blur))
    fg=Image.new("RGBA",(w,h),(0,0,0,0)); ImageDraw.Draw(fg).text((pad-l,pad-t),txt,font=f,fill=fill+(255,))
    out=Image.alpha_composite(sh,fg); return np.array(out)
def blend(frame,rgba,cx,cy,opacity=1.0):
    h,w=rgba.shape[:2]; x0=int(round(cx-w/2)); y0=int(round(cy-h/2))
    X0,Y0=max(0,x0),max(0,y0); X1,Y1=min(W,x0+w),min(H,y0+h)
    if X1<=X0 or Y1<=Y0: return
    s=rgba[Y0-y0:Y1-y0,X0-x0:X1-x0]; a=(s[:,:,3:4].astype(np.float32)/255)*opacity
    rgb=s[:,:,2::-1].astype(np.float32)
    frame[Y0:Y1,X0:X1]=frame[Y0:Y1,X0:X1]*(1-a)+rgb*a
# ---------------- gráficos ----------------
LABEL_Y=500; SUB_Y=602
def layers():
    L={}
    L['lab']={k:text_layer(k,FB,76,(255,255,255),shadow_a=0.9,off=(0,5),blur=4) for k in ('POBRE','RICO')}
    L['t_pobre']=text_layer("POBRE",FX,176,YEL,shadow_a=0.8,off=(0,10),blur=10,pad=40)
    L['t_vs']=text_layer("VS.",FX,88,(255,255,255),shadow_a=0.8,off=(0,7),blur=8,pad=40)
    L['t_rico']=text_layer("RICO",FX,176,YEL,shadow_a=0.8,off=(0,10),blur=10,pad=40)
    return L
def card_frames():
    fs=sorted(glob.glob("../work/card_clean/c_*.png")); out={}
    return fs
def card_img(i,cache={}):
    if i in cache: return cache[i]
    im=cv2.imread(f"../work/card_clean/c_{i+1:03d}.png",cv2.IMREAD_UNCHANGED)
    crop=im[70:200,95:450]                      # recorte de la tarjeta
    crop=cv2.resize(crop,None,fx=1.75,fy=1.75,interpolation=cv2.INTER_CUBIC)
    rgba=np.dstack([crop[:,:,:3],crop[:,:,3]]); cache[i]=rgba; return rgba
def main(out_path,start=0,count=None,test_frames=None):
    mp,tot=edit_time_map(); OUT_DUR=tot/SPEED; N=int(round(OUT_DUR*FPS))
    plate,ratio=build_plate()
    # centros
    idxP=list(range(int(7.05*30),int(11.5*30),6)); idxR=list(range(int(13.4*30),int(18.4*30),6))
    cP=centroid('P',[int(t*30) for t in np.arange(3.8,6.0,0.2)]+[int(t*30) for t in np.arange(21.5,24.8,0.2)])
    cR=centroid('R',[int(t*30) for t in np.arange(7.3,11.3,0.2)]+[int(t*30) for t in np.arange(25.4,28.5,0.2)])
    dx={'P':int(round(TARGET['P']-cP)),'R':int(round(TARGET['R']-cR))}
    print("centroides",cP,cR,"desplazamientos",dx,flush=True)
    L=layers(); caps=captions.build()
    cap_cache={}
    rd={'P':Reader('P'),'R':Reader('R')}
    prevA={}
    gain=ratio
    # gradiente superior para legibilidad
    yy=np.arange(H,dtype=np.float32)[:,None,None]
    shade=1-0.38*ss(330,560,yy)*(1-ss(780,1000,yy))
    tone_lut=np.array([255*(0.5-0.5*np.cos(np.pi*(i/255)))*0.35+i*0.65 for i in range(256)],np.float32)
    enc=None
    if out_path:
        enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
            "-c:v","libx264","-preset","slow","-crf","17","-pix_fmt","yuv420p","-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-movflags","+faststart",out_path],stdin=subprocess.PIPE)
    rng=np.random.default_rng(3)
    frames_to=range(N) if test_frames is None else test_frames
    last=-1
    for k in frames_to:
        te=min(k*SPEED/FPS,tot-1e-3); tp,tr=src_times(te); out_t=k/FPS
        fi={'P':int(round(tp*30)),'R':int(round(tr*30))}
        canvas=plate.copy()
        for which in ('P','R'):
            if test_frames is None: img=rd[which].get(fi[which])
            else:
                img=cv2.VideoCapture(f"../material_original/clip_{CLIP[which]}.mp4"); img.set(cv2.CAP_PROP_POS_FRAMES,fi[which]); img=img.read()[1]
            a=load_alpha(which,fi[which])
            if which in prevA and prevA[which][0]==fi[which]-1: a=0.7*a+0.3*prevA[which][1]
            prevA[which]=(fi[which],a)
            a=np.clip((a-0.04)/0.92,0,1); a=cv2.erode(a,np.ones((2,2),np.uint8)); a=cv2.GaussianBlur(a,(3,3),0)
            x0,y0,x1,y1=CROP[which]; fg=img[y0:y1,x0:x1].astype(np.float32)
            if which=='R': fg=fg*gain[y0:y1,None,:]
            d=dx[which]; dx0=x0+d; dx1=x1+d
            sx0=max(0,-dx0); sx1=(x1-x0)-max(0,dx1-W)
            tx0=dx0+sx0; tx1=dx0+sx1
            reg=canvas[y0:y1,tx0:tx1]; al=a[:,sx0:sx1,None]
            canvas[y0:y1,tx0:tx1]=reg*(1-al)+fg[:,sx0:sx1]*al
        # encuadre fijo
        crop=canvas[CY0:CY0+1600,CX0:CX0+900]
        fr=cv2.resize(crop,(W,H),interpolation=cv2.INTER_LANCZOS4)
        fr=np.clip(fr,0,255)
        fr=fr*shade
        fr+=rng.normal(0,1.6,fr.shape[:2])[:,:,None].astype(np.float32)   # grano ligero uniforme
        fr=np.clip(fr,0,255)
        # --- gráficos ---
        lx={'POBRE':TARGET['P'],'RICO':TARGET['R']}
        for nm,cxp in (('POBRE',int((TARGET['P']-CX0)*SCALE)),('RICO',int((TARGET['R']-CX0)*SCALE))):
            blend(fr,L['lab'][nm],cxp,LABEL_Y)
        # subtítulos
        for which,txt,t0,t1 in caps:
            if t0-0.0<=out_t<t1:
                key=(txt,)
                if key not in cap_cache: cap_cache[key]=text_layer(txt,FB,70,YEL,shadow_a=0.6,off=(0,4),blur=3)
                cxp=int((TARGET[which]-CX0)*SCALE); lay=cap_cache[key]
                blend(fr,lay,cxp,SUB_Y+lay.shape[0]//2-20)
        # título inicial (0-1.5 s)
        if out_t<1.5:
            tt=out_t; sc=1.0
            op=1.0
            if tt<0.2: sc=0.92+0.08*ss(0,0.2,tt)
            if tt>1.35: op=1-ss(1.35,1.5,tt)
            for nm,cy,s2 in (('t_pobre',940,1),('t_vs',1085,1),('t_rico',1235,1)):
                lay=L[nm]
                if sc!=1.0: lay=cv2.resize(lay,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
                blend(fr,lay,540,cy,op)
        # tarjeta de cierre
        CARD_T0=OUT_DUR-1.85
        ct=out_t-CARD_T0
        if ct>=0:
            c=ct if ct<0.6 else ct+0.4
            ci=min(int(c*60),155)
            blend(fr,card_img(ci),540,1600)
        buf=np.clip(fr,0,255).astype(np.uint8)
        if enc: enc.stdin.write(buf.tobytes())
        else: cv2.imwrite(f"../work/test_{k:04d}.jpg",buf)
        if k%60==0: print("frame",k,"/",N,flush=True)
    if enc: enc.stdin.close(); enc.wait()
if __name__=="__main__":
    if sys.argv[1]=="test": main(None,test_frames=[int(x) for x in sys.argv[2:]])
    else: main(sys.argv[1])
