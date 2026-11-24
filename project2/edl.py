# Lista de edición (EDL) — DINERO / QUINCENA E INVERSIÓN. Tiempos en segundos del material original (30 fps)
# (inicio_P, fin_P, inicio_R, fin_R)  P = clip POBRE (73356), R = clip RICO (73701)
SEGS=[
 (3.00,6.32, 3.00,6.32),       # POBRE 1 "Todo lo que me sobra de la quincena me lo gasto"
 (7.22,10.72, 7.22,10.72),     # RICO 1
 (12.52,16.72, 12.52,16.72),   # POBRE 2 "Compro un carro nuevo..."
 (17.92,26.18, 17.92,26.18),   # RICO 2 + POBRE 3
 (27.98,36.42, 27.98,36.42),   # RICO 3 + POBRE 4
 (37.92,44.58, 37.92,44.58),   # RICO 4 + POBRE 5 "Yo no sigo a Raúl Torres"
 (45.82,50.15, 45.82,50.15),   # RICO 5 (cierre)
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
