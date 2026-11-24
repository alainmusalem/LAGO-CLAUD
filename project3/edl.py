# Lista de edición (EDL) — AHORRO / "cuando gane más" (POBRE vs RICO). Tiempos en segundos del material original (30 fps)
# (inicio_P, fin_P, inicio_R, fin_R)  P = clip POBRE 74222; R = clip RICO (74454, salvo la toma 74345 para la línea R2)
PCLIP='74222'
SEGS=[
 (1.90,5.75, 1.90,5.75),        # POBRE 1 "Cuando gane más dinero, voy a empezar a ahorrar"
 (8.30,15.85, 8.30,15.85),      # RICO 1a "Empieza con lo que puedas desde hoy. Ahorrar es un hábito, no un lujo," + POBRE 2 "El dinero no compra la felicidad"
 (16.75,21.80, 16.75,21.80),    # RICO 1b "pero bien administrado puede darte tranquilidad..."
 (22.85,34.79, 21.80,33.74),    # POBRE 3 + RICO 2 (toma 74345, desplazada 1.05 s para no solapar voces)
 (34.79,44.70, 34.49,44.40),    # POBRE 4 + RICO 3 (desplazada 0.30 s)
 (46.15,54.64, 45.25,53.74),    # POBRE 5 + RICO 4 (cierre; desplazada 0.90 s)
]
RCLIP=['74454','74454','74454','74345','74454','74454']
SPEED=1.1
FPS=30
def edit_time_map():
    out=[];te=0.0
    for a,b,c,d in SEGS:
        out.append((te,te+(b-a),a,c)); te+=b-a
    return out,te
def src_info(te):
    m,tot=edit_time_map()
    for i,(s,e,a,c) in enumerate(m):
        if te<e or i==len(m)-1:
            return a+(te-s), c+(te-s), RCLIP[i]
def src_times(te):
    a,b,_=src_info(te); return a,b
def ranges_for(clip):
    r=[]
    if clip==PCLIP: r+=[(a,b) for a,b,c,d in SEGS]
    for i,(a,b,c,d) in enumerate(SEGS):
        if RCLIP[i]==clip: r.append((c,d))
    return r
