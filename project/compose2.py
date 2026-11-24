"""V2: mismo montaje/audio que V1; nuevos rótulos, subtítulos, tarjeta arriba y (B) imágenes."""
import cv2,numpy as np,subprocess,sys,os,glob,json
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from edl import *
import compose as C
import captions2
from compose import W,H,FB,FX,YEL,SCALE,CX0,CY0,TARGET,CROP,ss,blend,load_alpha,centroid,build_plate,Reader,text_layer
RED=(0xFF,0x38,0x38); GREEN=(0x32,0xD7,0x4B)
LABEL_SIZE=106; LABEL_Y=470
SUB_SIZE=56; SUB_TOP=1170; CARD_Y=320
IMG_W,IMG_H,IMG_Y=420,280,688
def text_block(lines,size=SUB_SIZE,fill=YEL,shadow_a=0.6,off=(0,4),blur=3,pad=22,lh=1.10):
    f=ImageFont.truetype(FB,size); asc,desc=f.getmetrics()
    ws=[f.getlength(l) for l in lines]; w=int(max(ws))+2*pad; step=int(size*lh); h=step*(len(lines)-1)+asc+desc+2*pad
    sh=Image.new("RGBA",(w,h),(0,0,0,0)); fg=Image.new("RGBA",(w,h),(0,0,0,0))
    ds=ImageDraw.Draw(sh); df=ImageDraw.Draw(fg)
    for i,l in enumerate(lines):
        x=(w-f.getlength(l))/2; y=pad+i*step
        ds.text((x+off[0],y+off[1]),l,font=f,fill=(0,0,0,int(255*shadow_a))); df.text((x,y),l,font=f,fill=fill+(255,))
    sh=sh.filter(ImageFilter.GaussianBlur(blur))
    return np.array(Image.alpha_composite(sh,fg))
def rounded_image(path,w=IMG_W,h=IMG_H,r=22):
    im=Image.open(path).convert("RGB"); iw,ih=im.size; ar=w/h
    if iw/ih>ar: nw=int(ih*ar); im=im.crop(((iw-nw)//2,0,(iw-nw)//2+nw,ih))
    else: nh=int(iw/ar); t=(ih-nh)//3; im=im.crop((0,t,iw,t+nh))
    im=im.resize((w,h),Image.LANCZOS)
    pad=26; canvas=Image.new("RGBA",(w+2*pad,h+2*pad),(0,0,0,0))
    mask=Image.new("L",(w,h),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),r,fill=255)
    shadow=Image.new("RGBA",canvas.size,(0,0,0,0)); sm=Image.new("L",canvas.size,0); sm.paste(mask,(pad,pad+6))
    shadow.putalpha(sm.point(lambda v:int(v*0.45))); shadow=shadow.filter(ImageFilter.GaussianBlur(9))
    canvas=Image.alpha_composite(canvas,shadow); tile=im.convert("RGBA"); tile.putalpha(mask); canvas.alpha_composite(tile,(pad,pad))
    return np.array(canvas)
def layout_labels():
    return {'P':text_layer("POBRE",FX,LABEL_SIZE,RED,shadow_a=0.55,off=(0,4),blur=4),
            'R':text_layer("RICO",FX,LABEL_SIZE,GREEN,shadow_a=0.55,off=(0,4),blur=4)}
def scale_rgba(a,s):
    return cv2.resize(a,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
def eob(t): c1=1.70158; c3=c1+1; return 1+c3*(t-1)**3+c1*(t-1)**2
def image_schedule(plan):
    """plan: lista de dicts {who,file,word,approx,t_end_from} -> intervalos en tiempo de salida"""
    caps=captions2.build(); out=[]
    for p in plan:
        t0=captions2.word_time(p['who'],p['word'],p['approx'])+p.get('dt0',-0.12)
        line_end=max(c[3] for c in caps if c[0]==p['who'] and c[2]<=t0+0.05 and c[3]>t0) if True else 0
        end=p.get('end') or line_end+0.25
        out.append(dict(p,t0=t0,t1=max(end,t0+1.3)))
    return out
def main(outA,outB,plan,start=0,test_frames=None):
    mp,tot=edit_time_map(); OUT_DUR=tot/SPEED; N=int(round(OUT_DUR*FPS))
    plate,ratio=build_plate()
    cP=centroid('P',[int(t*30) for t in np.arange(3.8,6.0,0.2)]+[int(t*30) for t in np.arange(21.5,24.8,0.2)])
    cR=centroid('R',[int(t*30) for t in np.arange(7.3,11.3,0.2)]+[int(t*30) for t in np.arange(25.4,28.5,0.2)])
    dx={'P':int(round(TARGET['P']-cP)),'R':int(round(TARGET['R']-cR))}
    labs=layout_labels(); caps=captions2.build(); cap_cache={}
    sched=image_schedule(plan) if plan else []
    imgs={p['file']:rounded_image(p['file']) for p in sched}
    json.dump([{k:v for k,v in s.items()} for s in sched],open("../work/image_schedule.json","w"),ensure_ascii=False,indent=1)
    rd={'P':Reader('P'),'R':Reader('R')} if test_frames is None else {}
    prevA={}; gain=ratio
    yy=np.arange(H,dtype=np.float32)[:,None,None]
    shade=1-0.38*ss(330,560,yy)*(1-ss(780,1000,yy))
    def enc(path):
        return subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","slow","-crf","17","-pix_fmt","yuv420p","-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",path],stdin=subprocess.PIPE)
    eA=enc(outA) if outA else None; eB=enc(outB) if outB else None
    rng=np.random.default_rng(3)
    for k in (range(N) if test_frames is None else test_frames):
        te=min(k*SPEED/FPS,tot-1e-3); tp,tr=src_times(te); out_t=k/FPS
        fi={'P':int(round(tp*30)),'R':int(round(tr*30))}
        canvas=plate.copy()
        for which in ('P','R'):
            if test_frames is None: img=rd[which].get(fi[which])
            else:
                cap=cv2.VideoCapture(f"../material_original/clip_{C.CLIP[which]}.mp4"); cap.set(cv2.CAP_PROP_POS_FRAMES,fi[which]); img=cap.read()[1]
            a=load_alpha(which,fi[which])
            if which in prevA and prevA[which][0]==fi[which]-1: a=0.7*a+0.3*prevA[which][1]
            prevA[which]=(fi[which],a)
            a=np.clip((a-0.04)/0.92,0,1); a=cv2.erode(a,np.ones((2,2),np.uint8)); a=cv2.GaussianBlur(a,(3,3),0)
            x0,y0,x1,y1=CROP[which]; fg=img[y0:y1,x0:x1].astype(np.float32)
            if which=='R': fg=fg*gain[y0:y1,None,:]
            d=dx[which]; dx0=x0+d; dx1=x1+d
            sx0=max(0,-dx0); sx1=(x1-x0)-max(0,dx1-W); tx0=dx0+sx0; tx1=dx0+sx1
            reg=canvas[y0:y1,tx0:tx1]; al=a[:,sx0:sx1,None]
            canvas[y0:y1,tx0:tx1]=reg*(1-al)+fg[:,sx0:sx1]*al
        crop=canvas[CY0:CY0+1600,CX0:CX0+900]
        fr=np.clip(cv2.resize(crop,(W,H),interpolation=cv2.INTER_LANCZOS4),0,255)*shade
        fr+=rng.normal(0,1.6,fr.shape[:2])[:,:,None].astype(np.float32); fr=np.clip(fr,0,255)
        cxs={'P':int((TARGET['P']-CX0)*SCALE),'R':int((TARGET['R']-CX0)*SCALE)}
        for w_ in 'PR': blend(fr,labs[w_],cxs[w_],LABEL_Y)
        for which,lines,t0,t1 in caps:
            if t0<=out_t<t1:
                key=tuple(lines)
                if key not in cap_cache: cap_cache[key]=text_block(list(lines))
                lay=cap_cache[key]; blend(fr,lay,cxs[which],SUB_TOP+lay.shape[0]//2-22)
        if out_t<1.5:
            sc=0.92+0.08*ss(0,0.2,out_t) if out_t<0.2 else 1.0; op=1-ss(1.35,1.5,out_t) if out_t>1.35 else 1.0
            for nm,cy in (('t_pobre',940),('t_vs',1085),('t_rico',1235)):
                lay=Ltitle[nm]; lay=scale_rgba(lay,sc) if sc!=1.0 else lay; blend(fr,lay,540,cy,op)
        ct=out_t-(OUT_DUR-1.85)
        if ct>=0:
            c=ct if ct<0.6 else ct+0.4; blend(fr,C.card_img(min(int(c*60),155)),540,CARD_Y)
        bufA=np.clip(fr,0,255).astype(np.uint8)
        if eA: eA.stdin.write(bufA.tobytes())
        if eB or test_frames is not None:
            frB=fr.copy()
            for s in sched:
                tt=out_t-s['t0']
                if -0.0<=tt<=s['t1']-s['t0']:
                    dur=s['t1']-s['t0']; lay=imgs[s['file']]
                    if tt<0.2: u=tt/0.2; sc=0.80+0.20*eob(u); op=min(1,u*1.6); yoff=int(26*(1-u))
                    elif tt>dur-0.16: u=(tt-(dur-0.16))/0.16; sc=1-0.08*u; op=1-u; yoff=int(-8*u)
                    else: sc,op,yoff=1.0,1.0,0
                    l2=scale_rgba(lay,sc) if abs(sc-1)>1e-3 else lay
                    blend(frB,l2,cxs[s['who']],IMG_Y+yoff,op)
            bufB=np.clip(frB,0,255).astype(np.uint8)
            if eB: eB.stdin.write(bufB.tobytes())
            if test_frames is not None: cv2.imwrite(f"../work/v2test_{k:04d}.jpg",bufB); cv2.imwrite(f"../work/v2testA_{k:04d}.jpg",bufA)
        if k%90==0: print("frame",k,"/",N,flush=True)
    for e in (eA,eB):
        if e: e.stdin.close(); e.wait()
Ltitle={'t_pobre':text_layer("POBRE",FX,176,YEL,shadow_a=0.8,off=(0,10),blur=10,pad=40),
        't_vs':text_layer("VS.",FX,88,(255,255,255),shadow_a=0.8,off=(0,7),blur=8,pad=40),
        't_rico':text_layer("RICO",FX,176,YEL,shadow_a=0.8,off=(0,10),blur=10,pad=40)}
if __name__=="__main__":
    plan=json.load(open("../work/imgs/plan.json")) if os.path.exists("../work/imgs/plan.json") else []
    if sys.argv[1]=="test": main(None,None,plan,test_frames=[int(x) for x in sys.argv[2:]])
    else: main(sys.argv[1] if sys.argv[1]!="-" else None,sys.argv[2] if len(sys.argv)>2 and sys.argv[2]!="-" else None,plan)
