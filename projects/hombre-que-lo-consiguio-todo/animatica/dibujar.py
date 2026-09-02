"""Generador del personaje Daniel en estilo plano de dibujo animado, con PIL."""
from PIL import Image, ImageDraw

S = 3
W, H = 1920 * S, 1080 * S

PIEL = (86, 165, 230)
PIEL_S = (66, 140, 205)
PELO = (40, 38, 42)
CHALECO = (78, 65, 50)
CHALECO_S = (62, 51, 39)
CAMISA = (250, 250, 247)
CAMISA_S = (223, 223, 218)
LINEA = (18, 18, 21)
BLANCO = (255, 255, 255)


def px(v):
    return max(1, int(round(v * S)))


def suave(pts, cerrado=True, n=14):
    """Catmull-Rom: convierte pocos puntos de control en una curva densa."""
    p = list(pts)
    if cerrado:
        p = [p[-1]] + p + [p[0], p[1]]
    else:
        p = [p[0]] + p + [p[-1]]
    out = []
    for i in range(len(p) - 3):
        p0, p1, p2, p3 = p[i], p[i + 1], p[i + 2], p[i + 3]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    return out


# Silueta de la cabeza en 3/4 mirando a la derecha, con la nariz integrada.
CABEZA = [(-22, -132), (32, -130), (78, -112), (103, -78), (106, -44),
          (101, -28), (128, -20), (137, -7), (108, 3), (104, 16),
          (110, 30), (98, 52), (72, 70), (26, 79), (-18, 74),
          (-62, 56), (-90, 26), (-102, -14), (-98, -62), (-76, -106)]

PELO_F = [(-106, -62), (-102, -104), (-74, -134), (-24, -152), (36, -150),
          (86, -130), (110, -98), (112, -64), (98, -92), (58, -114),
          (6, -122), (-46, -114), (-84, -92)]


class Lienzo:
    def __init__(self, fondo=(236, 236, 231)):
        self.img = Image.new("RGB", (W, H), fondo)
        self.d = ImageDraw.Draw(self.img)

    def guardar(self, ruta):
        self.img.resize((W // S, H // S), Image.LANCZOS).save(ruta, quality=95)

    def guardar_recorte(self, ruta, cx, cy, zoom=0.62):
        """Recorta sobre el lienzo supermuestreado: el plano corto no pierde nitidez."""
        aw, ah = int(W * zoom), int(H * zoom)
        x = min(max(int(cx * S) - aw // 2, 0), W - aw)
        y = min(max(int(cy * S) - ah // 2, 0), H - ah)
        self.img.crop((x, y, x + aw, y + ah)).resize((W // S, H // S), Image.LANCZOS).save(ruta, quality=95)


def _tr(pts, cx, cy, esc, flip):
    f = -1 if flip else 1
    return [(cx + x * esc * f, cy + y * esc) for x, y in pts]


def daniel(d, cx, cy, esc=1.0, flip=False, ojos="normal", boca="neutra",
           cuerpo=True, mirada=(0, 0), pelo=None, chaleco=None, camisa=None,
           calvo=False):
    """esc=1.0 -> cabeza de ~210 px de alto."""
    lw = px(4.2 * esc)
    PELO = pelo or globals()["PELO"]
    CHALECO = chaleco or globals()["CHALECO"]
    CAMISA = camisa or globals()["CAMISA"]

    def T(pts):
        return _tr(pts, cx, cy, esc, flip)

    def P(x, y):
        f = -1 if flip else 1
        return (cx + x * esc * f, cy + y * esc)

    if cuerpo:
        hy = 96  # arranque del cuello bajo la barbilla
        # cuello
        d.polygon(T([(-30, hy - 30), (34, hy - 30), (38, hy + 34), (-34, hy + 34)]), fill=PIEL_S)
        # torso con camisa
        torso = suave([(-176, hy + 300), (-158, hy + 120), (-104, hy + 46),
                       (-34, hy + 26), (46, hy + 26), (114, hy + 48),
                       (166, hy + 122), (182, hy + 300)], cerrado=False, n=10)
        d.polygon(T(torso + [(182, hy + 320), (-176, hy + 320)]), fill=CAMISA)
        d.line(T(torso), fill=LINEA, width=lw, joint="curve")
        # chaleco
        ch = suave([(-118, hy + 300), (-116, hy + 110), (-78, hy + 52),
                    (-30, hy + 40), (4, hy + 132), (40, hy + 40),
                    (86, hy + 54), (122, hy + 112), (126, hy + 300)],
                   cerrado=False, n=10)
        d.polygon(T(ch + [(126, hy + 320), (-118, hy + 320)]), fill=CHALECO)
        d.line(T(ch), fill=LINEA, width=lw, joint="curve")
        # cuello de la camisa
        d.polygon(T([(-30, hy + 38), (-4, hy + 34), (4, hy + 128), (-64, hy + 74)]), fill=CAMISA)
        d.polygon(T([(40, hy + 38), (12, hy + 34), (4, hy + 128), (74, hy + 76)]), fill=CAMISA)
        d.line(T([(-30, hy + 38), (-64, hy + 74), (4, hy + 128)]), fill=LINEA, width=lw, joint="curve")
        d.line(T([(40, hy + 38), (74, hy + 76), (4, hy + 128)]), fill=LINEA, width=lw, joint="curve")

    # oreja (detrás de la cabeza)
    ox0, oy0 = P(-116, -26)
    ox1, oy1 = P(-82, 20)
    d.ellipse([min(ox0, ox1), min(oy0, oy1), max(ox0, ox1), max(oy0, oy1)],
              fill=PIEL_S, outline=LINEA, width=px(3.2 * esc))

    # cabeza
    cab = T(suave(CABEZA, n=12))
    d.polygon(cab, fill=PIEL)
    d.line(cab + [cab[0]], fill=LINEA, width=lw, joint="curve")

    # pelo
    pel = T(suave(PELO_F, n=12))
    d.polygon(pel, fill=PELO)
    d.line(pel + [pel[0]], fill=LINEA, width=px(3 * esc), joint="curve")
    # mechón
    d.polygon(T([(104, -96), (132, -118), (120, -74)]), fill=PELO)

    # ojos
    dx, dy = mirada
    for sx in (26, 74):
        x0, y0 = P(sx - 27, -66)
        x1, y1 = P(sx + 27, -14)
        caja = [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]
        d.ellipse(caja, fill=BLANCO)
        if ojos == "cerrado":
            d.line([P(sx - 24, -40), P(sx + 24, -40)], fill=LINEA, width=px(4.5 * esc))
        else:
            r = 8.5
            a0, b0 = P(sx + dx - r, -36 + dy - r)
            a1, b1 = P(sx + dx + r, -36 + dy + r)
            d.ellipse([min(a0, a1), min(b0, b1), max(a0, a1), max(b0, b1)], fill=LINEA)
            # parpado superior caido
            corte = 0.46 if ojos == "cansado" else 0.32
            alto = (caja[3] - caja[1]) * corte
            d.pieslice([caja[0], caja[1], caja[2], caja[1] + 2 * alto], 180, 360, fill=PIEL)
            d.line([(caja[0] + px(1), caja[1] + alto), (caja[2] - px(1), caja[1] + alto)],
                   fill=LINEA, width=px(4 * esc))
        # el contorno se vuelve a trazar encima para que el ojo quede limpio
        d.ellipse(caja, outline=LINEA, width=px(3.4 * esc))

    # cejas
    d.line(T(suave([(2, -78), (26, -86), (50, -80)], cerrado=False, n=8)),
           fill=PELO, width=px(6.5 * esc), joint="curve")
    d.line(T(suave([(58, -80), (82, -86), (102, -76)], cerrado=False, n=8)),
           fill=PELO, width=px(6.5 * esc), joint="curve")

    # boca
    if boca == "neutra":
        d.line(T(suave([(58, 30), (78, 36), (96, 28)], cerrado=False, n=8)),
               fill=LINEA, width=px(4 * esc), joint="curve")
    elif boca == "abierta":
        mx0, my0 = P(56, 22)
        mx1, my1 = P(100, 48)
        d.ellipse([min(mx0, mx1), min(my0, my1), max(mx0, mx1), max(my0, my1)],
                  fill=(72, 36, 40), outline=LINEA, width=px(3.2 * esc))
    elif boca == "triste":
        d.line(T(suave([(58, 40), (78, 28), (98, 38)], cerrado=False, n=8)),
               fill=LINEA, width=px(4 * esc), joint="curve")
