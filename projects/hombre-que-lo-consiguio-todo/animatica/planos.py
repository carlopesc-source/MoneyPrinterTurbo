"""Genera los fotogramas del vídeo: fondo + personajes + encuadre."""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dibujar as D
import escenas as E

PELO_VIEJO = (206, 202, 196)
MONO_VIEJO = (62, 78, 96)
CAMISA_VIEJO = (198, 190, 172)

# (nombre, fondo, [personajes], encuadre)
# personaje: (quien, x, y, escala, flip, ojos, boca)
PLANOS = [
    # --- bloque 1: hook
    ("01a-ventana-lejos",  "ventana_noche",    [("d", 1180, 700, 1.45, True, "cansado", "neutra")], 1.0),
    ("01b-ventana-medio",  "ventana_noche",    [("d", 1000, 780, 2.1, True, "cansado", "triste")], 1.0),
    ("01c-cara",           "liso_oscuro",      [("d", 900, 700, 3.4, False, "cansado", "triste")], 1.0),
    ("01d-cama",           "cama",             [("d", 900, 760, 1.9, False, "cansado", "neutra")], 1.0),
    # --- bloque 2: consigue todo
    ("02a-cocina",         "cocina",           [("d", 980, 720, 1.8, False, "normal", "neutra")], 1.0),
    ("02b-cocina-cerca",   "cocina",           [("d", 900, 800, 2.9, False, "normal", "neutra")], 1.0),
    ("02c-oficina",        "oficina",          [("d", 1120, 760, 1.7, True, "normal", "neutra")], 1.0),
    ("02d-oficina-dos",    "oficina",          [("d", 660, 760, 1.7, False, "normal", "neutra"),
                                                ("v", 1260, 760, 1.7, True, "normal", "neutra")], 1.0),
    ("02e-brindis",        "salon",            [("d", 960, 780, 2.4, False, "normal", "abierta")], 1.0),
    # --- bloque 3: algo no encaja
    ("03a-amanecer",       "ventana_amanecer", [("d", 1120, 720, 1.6, True, "normal", "abierta")], 1.0),
    ("03b-amanecer-medio", "ventana_amanecer", [("d", 1020, 800, 2.3, True, "normal", "neutra")], 1.0),
    ("03c-amanecer-igual", "ventana_amanecer", [("d", 1020, 800, 2.3, True, "cansado", "neutra")], 1.0),
    ("03d-salon-cruza",    "salon",            [("d", 700, 800, 2.0, False, "cansado", "neutra")], 1.0),
    # --- bloque 4: deterioro
    ("04a-coche",          "coche",            [("d", 960, 760, 2.2, False, "cansado", "neutra")], 1.0),
    ("04b-coche-cerca",    "coche",            [("d", 900, 820, 3.2, False, "cansado", "triste")], 1.0),
    ("04c-cena",           "salon",            [("d", 620, 800, 2.1, False, "cansado", "neutra"),
                                                ("d2", 1320, 800, 2.1, True, "normal", "triste")], 1.0),
    ("04d-insomnio",       "cama",             [("d", 900, 800, 2.4, False, "normal", "triste")], 1.0),
    # --- bloque 5: el pueblo
    ("05a-calle",          "calle",            [("d", 900, 940, 1.35, False, "normal", "neutra")], 1.0),
    ("05b-taller-puerta",  "taller",           [("d", 420, 860, 1.9, False, "normal", "neutra"),
                                                ("v", 1180, 860, 1.9, True, "cansado", "neutra")], 1.0),
    ("05c-viejo-motor",    "taller",           [("v", 1000, 860, 2.4, False, "cansado", "neutra")], 1.0),
    ("05d-viejo-mira",     "taller",           [("v", 940, 820, 3.0, True, "normal", "abierta")], 1.0),
    # --- bloque 6: primera revelación
    ("06a-dos-taller",     "taller",           [("d", 500, 880, 2.0, False, "normal", "abierta"),
                                                ("v", 1300, 880, 2.0, True, "cansado", "neutra")], 1.0),
    ("06b-daniel-mudo",    "taller",           [("d", 900, 840, 3.1, False, "normal", "abierta")], 1.0),
    ("06c-viejo-habla",    "taller",           [("v", 940, 840, 3.1, True, "cansado", "abierta")], 1.0),
    # --- bloque 7: adaptación
    ("07a-suelo",          "salon_vacio",      [("d", 900, 880, 2.2, False, "normal", "abierta")], 1.0),
    ("07b-salon-cruza",    "salon",            [("d", 1080, 820, 2.0, True, "cansado", "neutra")], 1.0),
    ("07c-escucha",        "taller",           [("d", 900, 840, 3.3, False, "cansado", "triste")], 1.0),
    # --- bloque 8: el cerebro
    ("08a-cocina-noche",   "cocina",           [("d", 1000, 800, 2.2, True, "cansado", "neutra")], 1.0),
    ("08b-cara-liso",      "liso",             [("d", 900, 720, 3.5, False, "normal", "neutra")], 1.0),
    ("08c-tren",           "tren",             [("d", 820, 820, 2.4, True, "cansado", "neutra")], 1.0),
    ("08d-tren-lejos",     "tren",             [("d", 1080, 780, 1.7, True, "cansado", "triste")], 1.0),
    # --- bloque 9: intenta cambiar
    ("09a-cajas",          "salon_vacio",      [("d", 900, 820, 2.2, False, "normal", "neutra")], 1.0),
    ("09b-piso-pequeno",   "salon_vacio",      [("d", 1060, 800, 1.9, True, "cansado", "neutra")], 1.0),
    ("09c-movil",          "liso",             [("d", 900, 780, 3.0, False, "normal", "neutra")], 1.0),
    ("09d-igual",          "salon_vacio",      [("d", 900, 800, 2.3, False, "cansado", "triste")], 1.0),
    # --- bloque 10: segundo giro
    ("10a-taller-verano",  "taller_verano",    [("d", 520, 880, 2.0, False, "normal", "abierta"),
                                                ("v", 1320, 880, 2.0, True, "cansado", "neutra")], 1.0),
    ("10b-viejo-cerca",    "taller_verano",    [("v", 940, 840, 3.2, True, "cansado", "abierta")], 1.0),
    ("10c-daniel-parado",  "taller_verano",    [("d", 900, 840, 3.0, False, "normal", "neutra")], 1.0),
    ("10d-aprendiz",       "taller_verano",    [("v", 660, 880, 2.0, False, "normal", "neutra"),
                                                ("a", 1300, 880, 1.9, True, "normal", "neutra")], 1.0),
    # --- bloque 11: conclusión
    ("11a-lee",            "salon",            [("d", 900, 800, 2.3, False, "normal", "neutra")], 1.0),
    ("11b-calle-calma",    "calle",            [("d", 1000, 940, 1.4, True, "normal", "neutra")], 1.0),
    ("11c-cara-calma",     "liso",             [("d", 900, 720, 3.4, False, "normal", "neutra")], 1.0),
    # --- bloque 12: cierre
    ("12a-ventana-igual",  "ventana_noche",    [("d", 1180, 700, 1.45, True, "cansado", "neutra")], 1.0),
    ("12b-ventana-vacia",  "ventana_noche",    [], 1.0),
]

QUIEN = {
    "d":  dict(),
    "d2": dict(pelo=(92, 60, 52), chaleco=(120, 78, 96), camisa=(240, 236, 232)),
    "v":  dict(pelo=PELO_VIEJO, chaleco=MONO_VIEJO, camisa=CAMISA_VIEJO),
    "a":  dict(pelo=(58, 44, 36), chaleco=(96, 108, 84), camisa=(238, 234, 226)),
}


def generar(destino):
    os.makedirs(destino, exist_ok=True)
    rutas = []
    for nombre, fondo, gente, _ in PLANOS:
        c = E.D.Lienzo() if False else None
        lienzo = D.Lienzo()
        E.FONDOS[fondo](lienzo.d)
        for quien, x, _y, esc, flip, ojos, boca in gente:
            # encuadre: figura entera si cabe, si no plano medio con la cara
            # en el tercio superior. Evita las "cabezas flotantes".
            y = (1080 - 416 * esc - 30) if esc <= 1.75 else 400
            D.daniel(lienzo.d, D.px(x), D.px(y), esc=D.S * esc, flip=flip,
                     ojos=ojos, boca=boca, **QUIEN[quien])
        ruta = os.path.join(destino, f"{nombre}.png")
        lienzo.guardar(ruta)
        rutas.append(ruta)
        # variante de plano corto sobre el mismo dibujo, para dar ritmo sin
        # repetir imagen: se recorta en el lienzo grande, no pierde calidad.
        if gente:
            _, gx, _, gesc, _, _, _ = gente[0]
            gy = (1080 - 416 * gesc - 30) if gesc <= 1.75 else 400
            corta = os.path.join(destino, f"{nombre}-corto.png")
            lienzo.guardar_recorte(corta, gx, gy + 40, 0.58 if gesc <= 1.75 else 0.68)
            rutas.append(corta)
    return rutas


if __name__ == "__main__":
    r = generar(sys.argv[1] if len(sys.argv) > 1 else "daniel")
    print(f"{len(r)} planos generados en {os.path.dirname(r[0])}")
