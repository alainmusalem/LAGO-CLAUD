# Lista de edición (EDL): tiempos en segundos del material original (30 fps)
# (inicio_P, fin_P, inicio_R, fin_R)  P = clip POBRE (72522), R = clip RICO (72631)
SEGS=[
 (3.70,6.10, 3.70,6.10),       # POBRE 1
 (7.05,11.55, 7.05,11.55),     # RICO 1
 (13.30,19.10, 12.73,18.53),   # POBRE 2 + RICO 2 (RICO desplazado 0.57 s: sin solape de voces)
 (21.40,24.95, 21.40,24.95),   # POBRE 3
 (25.15,28.78, 25.15,28.78),   # RICO 3
 (29.06,33.78, 29.06,33.78),   # POBRE 4
 (34.30,36.18, 34.30,36.18),   # RICO 4 (cierre)
]
SPEED=1.1
FPS=30
def edit_time_map():
    out=[];te=0.0
    for a,b,c,d in SEGS:
        out.append((te,te+(b-a),a,c)); te+=b-a
    return out,te
def src_times(te):
    m,tot=edit_time_map()
    for s,e,a,c in m:
        if te<e or (s,e,a,c)==m[-1]:
            return a+(te-s), c+(te-s)
