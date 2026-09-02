"""Fondos planos + composición de planos para el vídeo."""
import random
from PIL import Image, ImageDraw
import dibujar as D

px = D.px
LINEA = D.LINEA


def rect(d, x0, y0, x1, y1, fill, borde=None, w=4):
    d.rectangle([px(x0), px(y0), px(x1), px(y1)], fill=fill,
                outline=borde, width=px(w) if borde else 0)


def elipse(d, x0, y0, x1, y1, fill, borde=None, w=4):
    d.ellipse([px(x0), px(y0), px(x1), px(y1)], fill=fill,
              outline=borde, width=px(w) if borde else 0)


def linea(d, pts, fill, w=4):
    d.line([(px(x), px(y)) for x, y in pts], fill=fill, width=px(w), joint="curve")


def skyline(d, y_base, color, alto=340, rnd=None, ventanas=None):
    rnd = rnd or random.Random(7)
    x = -40
    while x < 1960:
        an = rnd.randint(70, 170)
        al = rnd.randint(int(alto * 0.35), alto)
        rect(d, x, y_base - al, x + an, y_base, color)
        if ventanas:
            for fy in range(int(y_base - al) + 26, int(y_base) - 24, 46):
                for fx in range(int(x) + 18, int(x + an) - 22, 40):
                    if rnd.random() < 0.42:
                        rect(d, fx, fy, fx + 18, fy + 24, ventanas)
        x += an + rnd.randint(8, 26)


# ---------------------------------------------------------------- fondos
def f_ventana_noche(d, amanecer=False):
    pared = (44, 46, 56) if not amanecer else (226, 214, 200)
    rect(d, 0, 0, 1920, 1080, pared)
    cielo = (18, 22, 40) if not amanecer else (250, 206, 150)
    rect(d, 250, 60, 1670, 900, cielo)
    if amanecer:
        elipse(d, 1180, 560, 1400, 780, (255, 236, 178))
    skyline(d, 900, (10, 12, 24) if not amanecer else (150, 122, 120),
            ventanas=(252, 226, 140) if not amanecer else None)
    for x in (250, 950, 1670):
        rect(d, x - 16, 40, x + 16, 920, (28, 28, 34))
    rect(d, 230, 40, 1690, 74, (28, 28, 34))
    rect(d, 230, 886, 1690, 924, (28, 28, 34))
    rect(d, 0, 900, 1920, 1080, (34, 34, 42) if not amanecer else (196, 178, 158))


def f_habitacion(d, pared=(216, 210, 198), suelo=(150, 128, 104), zocalo=True):
    rect(d, 0, 0, 1920, 1080, pared)
    rect(d, 0, 760, 1920, 1080, suelo)
    if zocalo:
        rect(d, 0, 748, 1920, 772, (120, 100, 80))


def f_cocina(d):
    f_habitacion(d, (196, 206, 196), (140, 132, 120))
    rect(d, 90, 620, 760, 660, (120, 96, 70))       # encimera
    rect(d, 90, 660, 760, 780, (168, 148, 122))
    rect(d, 1180, 300, 1500, 780, (200, 200, 204))  # nevera
    rect(d, 1180, 300, 1500, 320, (150, 150, 156))
    linea(d, [(1340, 330), (1340, 770)], (150, 150, 156), 5)
    rect(d, 240, 150, 620, 400, (150, 168, 150), (60, 60, 60), 6)


def f_oficina(d):
    f_habitacion(d, (206, 214, 226), (120, 124, 132))
    for x in (120, 640, 1160, 1680):
        rect(d, x, 90, x + 300, 620, (168, 200, 226), (70, 74, 84), 7)
    rect(d, 0, 700, 1920, 730, (96, 100, 110))


def f_coche(d):
    rect(d, 0, 0, 1920, 1080, (26, 28, 36))
    rect(d, 120, 60, 1800, 620, (16, 20, 34))
    skyline(d, 620, (8, 10, 18), 260, random.Random(3), (250, 220, 130))
    rect(d, 90, 40, 1830, 90, (44, 46, 56))
    rect(d, 90, 600, 1830, 660, (44, 46, 56))
    rect(d, 0, 780, 1920, 1080, (52, 46, 44))       # salpicadero
    elipse(d, 620, 830, 1300, 1180, (30, 28, 30), (16, 16, 18), 8)
    elipse(d, 730, 930, 1190, 1180, (52, 46, 44))


def f_taller(d, verano=False):
    pared = (176, 166, 142) if verano else (140, 134, 122)
    rect(d, 0, 0, 1920, 1080, pared)
    rect(d, 0, 800, 1920, 1080, (108, 100, 90))
    rect(d, 1380, 120, 1860, 560, (120, 132, 130), (60, 56, 50), 8)   # ventanuco
    if verano:
        rect(d, 1380, 120, 1860, 560, (240, 226, 170))
        d.polygon([(px(1390), px(560)), (px(1850), px(130)),
                   (px(1900), px(300)), (px(1560), px(700))], fill=(250, 240, 200, 90))
    for i, y in enumerate((180, 260, 340)):
        rect(d, 90, y, 620, y + 26, (96, 88, 76))
        for x in range(120, 580, 90):
            rect(d, x, y - 46, x + 54, y, (150, 140, 120) if i % 2 else (120, 128, 130))
    rect(d, 700, 640, 1300, 690, (110, 96, 76))     # banco de trabajo
    rect(d, 700, 690, 1300, 820, (86, 74, 60))
    elipse(d, 820, 540, 1120, 660, (86, 90, 96), (40, 40, 44), 7)     # motor
    rect(d, 900, 470, 1010, 560, (70, 74, 80))


def f_calle(d):
    rect(d, 0, 0, 1920, 1080, (198, 214, 226))
    for x, an, al, c in ((-40, 420, 620, (214, 200, 176)), (400, 360, 700, (196, 178, 156)),
                         (790, 400, 560, (222, 210, 190)), (1210, 340, 660, (202, 186, 164)),
                         (1570, 400, 600, (216, 202, 182))):
        rect(d, x, 1080 - al, x + an, 900, c, (110, 96, 80), 6)
        for fy in range(1080 - al + 70, 860, 170):
            for fx in range(int(x) + 50, int(x + an) - 90, 150):
                rect(d, fx, fy, fx + 80, fy + 110, (120, 140, 156), (80, 70, 60), 5)
    rect(d, 0, 900, 1920, 1080, (150, 146, 142))


def f_cama(d):
    rect(d, 0, 0, 1920, 1080, (36, 38, 50))
    rect(d, 0, 700, 1920, 1080, (26, 28, 38))
    rect(d, 240, 660, 1680, 1080, (58, 60, 76))
    rect(d, 240, 620, 700, 700, (200, 200, 206))
    rect(d, 1500, 200, 1860, 700, (48, 50, 64))


def f_tren(d):
    rect(d, 0, 0, 1920, 1080, (52, 54, 62))
    rect(d, 220, 120, 1700, 760, (168, 196, 176))
    rect(d, 220, 560, 1700, 760, (120, 156, 110))
    for x in range(260, 1700, 210):
        rect(d, x, 470, x + 26, 600, (86, 118, 80))
    rect(d, 200, 100, 1720, 140, (34, 34, 40))
    rect(d, 200, 740, 1720, 800, (34, 34, 40))
    rect(d, 0, 800, 1920, 1080, (70, 66, 72))


def f_liso(d, c=(232, 228, 220)):
    rect(d, 0, 0, 1920, 1080, c)


FONDOS = {
    "ventana_noche": lambda d: f_ventana_noche(d, False),
    "ventana_amanecer": lambda d: f_ventana_noche(d, True),
    "cocina": f_cocina,
    "oficina": f_oficina,
    "coche": f_coche,
    "taller": lambda d: f_taller(d, False),
    "taller_verano": lambda d: f_taller(d, True),
    "calle": f_calle,
    "cama": f_cama,
    "tren": f_tren,
    "salon": lambda d: f_habitacion(d, (222, 216, 204), (162, 138, 112)),
    "salon_vacio": lambda d: f_habitacion(d, (236, 232, 224), (176, 154, 128)),
    "liso": f_liso,
    "liso_oscuro": lambda d: f_liso(d, (46, 48, 58)),
}
