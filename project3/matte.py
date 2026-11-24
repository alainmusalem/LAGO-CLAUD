import cv2,numpy as np,onnxruntime as ort,subprocess,sys,os
from edl import *
W,H=1080,1920
sess=ort.InferenceSession("../work/models/modnet/onnx/model.onnx",providers=["CPUExecutionProvider"])
CROPR={'P':(380,480,1080,1920),'R':(0,480,700,1920)}
def role(clip): return 'P' if clip==PCLIP else 'R'
def matte(img,box):
    x0,y0,x1,y1=box
    c=img[y0:y1,x0:x1]
    rgb=cv2.cvtColor(c,cv2.COLOR_BGR2RGB)
    s=cv2.resize(rgb,(480,992),interpolation=cv2.INTER_AREA).astype(np.float32)
    s=(s-127.5)/127.5
    o=sess.run(None,{"input":s.transpose(2,0,1)[None]})[0][0,0]
    a=cv2.resize(o,(x1-x0,y1-y0),interpolation=cv2.INTER_CUBIC)
    return np.clip(a,0,1)
def needed(clip):
    idx=set()
    for lo,hi in ranges_for(clip):
        for f in range(int(lo*30)-2,int(hi*30)+3): idx.add(f)
    return sorted(idx)
if __name__=="__main__":
    clip=sys.argv[1]
    os.makedirs(f"../work3/alpha_{clip}",exist_ok=True)
    need=needed(clip); ns=set(need)
    p=subprocess.Popen(["ffmpeg","-v","error","-i",f"../material_original_3/clip_{clip}.mp4","-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
    i=0
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        if i in ns:
            img=np.frombuffer(b,np.uint8).reshape(H,W,3)
            a=matte(img,CROPR[role(clip)])
            cv2.imwrite(f"../work3/alpha_{clip}/{i:05d}.png",(a*255).astype(np.uint8))
        i+=1
        if i>max(need)+1: break
    p.kill(); print("done",clip,len(need))
