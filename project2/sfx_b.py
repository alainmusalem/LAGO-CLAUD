"""Audio de la V2B = audio de V1/V2A (idéntico) + pops muy sutiles al aparecer cada imagen."""
import json,numpy as np,soundfile as sf
import audiomix as A
SR=48000
v,_=sf.read("../work2/final_audio.wav"); v=v.astype(np.float32)
sched=json.load(open("../work2/image_schedule.json"))
S=np.zeros(len(v),np.float32)
for s in sched: A.add(S,A.pop()*10**(-27/20),s['t0']+0.02)
out=v+(S[:,None] if v.ndim==2 else S)
print("peak dBFS",20*np.log10(np.abs(out).max()))
sf.write("../work2/final_audio_B.wav",out,SR)
