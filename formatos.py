"""Formatos nuevos de Reels (prueba de formatos de noviembre 2026).
  postit     – el formato de siempre (pregunta + pósit → móvil → cierre) con música y efectos
  monigotes  – historia con monigotes animados + voz en off + subtítulos + efectos
  chat       – conversación de mensajería dueño ↔ trabajador, con sonidos de mensaje
  quiz       – "¿Legal o multa?": pregunta con voz, cuenta atrás y respuesta
  voz        – voz en off con subtítulos grandes palabra a palabra e imágenes que acompañan
Uso: lo llama generador.py cuando el reel tiene "formato".
"""
import math, os, random, subprocess, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generador as G
import audio as A

W, H, FPS = G.W, G.H, G.FPS
NAVY, NAVY_D, TEAL, GREEN, BTN, GREY, WHITE = G.NAVY, G.NAVY_D, G.TEAL, G.GREEN, G.BTN, G.GREY, G.WHITE
RED = (214, 69, 65)
SKIN = (255, 255, 255)
F, N, ease, ease_back = G.F, G.N, G.ease, G.ease_back


# =====================================================================
# Plano = trozo del vídeo con su duración, su dibujo y sus sonidos
# =====================================================================
class Plano:
    def __init__(self, dur, draw, fondo="claro", sfx=None, voz=None, voz_t0=0.0, subs=True):
        self.dur, self.draw, self.fondo = dur, draw, fondo
        self.sfx = sfx or []          # [(nombre, t, ganancia)]
        self.voz, self.voz_t0, self.subs = voz, voz_t0, subs   # voz = (audio, dur, texto)


def plano_con_voz(texto, draw_fn, fondo="claro", sfx=None, extra=0.45, minimo=2.0, voz_t0=0.15, subs=True):
    v, d = A.voz(texto)
    return Plano(max(minimo, voz_t0 + d + extra), draw_fn, fondo, sfx, (v, d, texto), voz_t0, subs)


# ---------- fondos ----------
_BGC = {}
def fondo(estilo, t=0.0):
    if estilo == "vivo":  # fondo oscuro con manchas de color que se mueven despacio
        base = G.background("oscuro").copy()
        lay = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for i, (c, r) in enumerate(((TEAL, 110), (GREEN, 80), ((40, 90, 160), 130))):
            x = W // 8 + math.sin(t * 0.5 + i * 2.1) * 90 + i * 40
            y = H // 8 + math.cos(t * 0.4 + i * 1.7) * 160 + (i - 1) * 120
            d.ellipse((x - r, y - r, x + r, y + r), fill=c + (70,))
        lay = lay.filter(ImageFilter.GaussianBlur(40)).resize((W, H), Image.BILINEAR)
        base.alpha_composite(lay)
        return base
    return G.background(estilo).copy()


def envolver(texto, weight, size, max_w):
    if "\n" in texto:
        return texto
    dd = ImageDraw.Draw(Image.new("L", (1, 1)))
    f = F(weight, size)
    lines, cur = [], ""
    for wd in texto.split():
        c = (cur + " " + wd).strip()
        if cur and dd.textlength(c, font=f) > max_w:
            lines.append(cur); cur = wd
        else:
            cur = c
    lines.append(cur)
    return "\n".join(lines)

def bloque(texto, acento, weight, start, max_w, min_s, color, max_lineas=3, oscuro=False):
    s = start
    while True:
        t = envolver(texto, weight, s, max_w)
        if t.count("\n") < max_lineas or s <= min_s:
            break
        s -= 4
    return G.text_block(t, acento, F(weight, s), color, acc_c1=(110, 220, 170) if oscuro else TEAL, acc_c2=GREEN)


# ---------- titular fijo arriba (gancho visible todo el vídeo y en la portada) ----------
_TIT = {}
def titular(img, texto, acento=None, oscuro=False, y=150):
    k = (texto, acento, oscuro)
    if k not in _TIT:
        col = WHITE if oscuro else NAVY
        tb = bloque(texto, acento, 800, 80, 940, 60, col, 2, oscuro)
        _TIT[k] = tb
    tb = _TIT[k]
    img.alpha_composite(tb, ((W - tb.width) // 2, y))
    return y + tb.height


# ---------- subtítulos palabra a palabra ----------
def _tiempos_palabras(texto, dur):
    pal = texto.split()
    pesos = [len(p) + 2 + (5 if p[-1] in ".?!:" else 2 if p[-1] in ",;" else 0) for p in pal]
    tot = sum(pesos)
    t, out = 0.0, []
    for p, w in zip(pal, pesos):
        out.append((p, t, t + dur * w / tot))
        t += dur * w / tot
    return out

def _grupos(pal, max_c=17):
    grupos, cur = [], []
    for i, p in enumerate(pal):
        if cur and (sum(len(pal[j][0]) + 1 for j in cur) + len(p[0]) > max_c or pal[cur[-1]][0][-1] in ".?!"):
            grupos.append(cur); cur = []
        cur.append(i)
    if cur:
        grupos.append(cur)
    return grupos

def subtitulos(img, texto, t, dur, y=1180, size=88, max_c=17, oscuro=False):
    if t < 0 or t > dur + 0.35:
        return
    pal = _tiempos_palabras(texto, dur)
    grupos = _grupos(pal, max_c)
    tt = min(t, dur - 1e-3)
    gi = next((g for g in grupos if pal[g[-1]][2] >= tt), grupos[-1])
    d = ImageDraw.Draw(img)
    f = F(800, size)
    words = [pal[i][0] for i in gi]
    widths = [d.textlength(w + " ", font=f) for w in words]
    x = (W - sum(widths)) / 2
    # aparece con un pequeño "pop" al cambiar de grupo
    g0 = pal[gi[0]][1]
    s = min(1, (t - g0) / 0.12) if t >= g0 else 1
    yy = y + int((1 - s) * 20)
    for i, w, wd in zip(gi, words, widths):
        activo = pal[i][1] <= tt < pal[i][2] + 0.05
        col = GREEN if activo else WHITE
        d.text((x, yy), w, font=f, fill=col, stroke_width=9, stroke_fill=NAVY_D)
        x += wd


# =====================================================================
# Monigotes
# =====================================================================
def _p(x, y, ang, L, dirx):
    a = math.radians(ang)
    return (x + dirx * math.sin(a) * L, y + math.cos(a) * L)

def _seg(d, a, b, w, c):
    d.line([a, b], fill=c, width=w)
    r = w / 2
    for p in (a, b):
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=c)

POSES = {
    # (hombro_i, codo_i, hombro_d, codo_d, cadera_i, rodilla_i, cadera_d, rodilla_d)  grados desde la vertical; + = hacia delante
    "pie":     (-12, 0, 12, 0, -6, 0, 6, 0),
    "movil":   (-10, 0, 35, 110, -6, 0, 6, 0),
    "estres":  (-150, -80, 150, 80, -10, 0, 10, 0),
    "feliz":   (-150, 0, 150, 0, -12, 0, 12, 0),
    "senala":  (-10, 0, 90, 0, -6, 0, 6, 0),
    "brazos":  (-30, 120, 30, -120, -6, 0, 6, 0),
    "ok":      (-10, 0, 40, 130, -6, 0, 6, 0),
}

def pose_t(nombre, t):
    p = list(POSES.get(nombre, POSES["pie"]))
    if nombre == "andar":
        s = math.sin(t * 2 * math.pi * 1.7)
        return (-28 * s, 15, 28 * s, 15, 26 * s, -abs(s) * 30 - 5, -26 * s, -abs(s) * 30 - 5)
    if nombre == "estres":
        p[0] += math.sin(t * 25) * 6; p[2] += math.sin(t * 25 + 1) * 6
    if nombre == "feliz":
        p[0] += math.sin(t * 8) * 10; p[2] -= math.sin(t * 8) * 10
    return tuple(p)

def monigote(img, x, y, t, pose="pie", dirx=1, s=1.0, cara="normal", acc=(), color=NAVY, salto=0.0):
    """x, y = punto entre los pies. acc: corbata, gorra, delantal, escoba, movil, portapapeles, bata, pelo"""
    d = ImageDraw.Draw(img)
    hi, rd, ha, hd, ci, ri, cd, rrd = pose_t(pose, t)
    w = int(16 * s)
    y = y - salto
    cadera = (x, y - 230 * s)
    cuello = (x, y - 430 * s)
    hombro = (x, y - 405 * s)
    if "bata" in acc:
        d.polygon([(x - 70 * s, y - 180 * s), (x + 70 * s, y - 180 * s), (x + 48 * s, y - 410 * s), (x - 48 * s, y - 410 * s)], fill=(235, 242, 250), outline=color)
    if "delantal" in acc:
        d.rounded_rectangle((x - 42 * s, y - 320 * s, x + 42 * s, y - 170 * s), int(10 * s), fill=GREEN)
    # piernas
    for ang, rod in ((ci, ri), (cd, rrd)):
        k = _p(*cadera, ang, 120 * s, dirx)
        pie = _p(*k, ang + rod, 115 * s, dirx)
        _seg(d, cadera, k, w, color); _seg(d, k, pie, w, color)
        d.line([pie, (pie[0] + dirx * 26 * s, pie[1])], fill=color, width=w)
    _seg(d, cuello, cadera, w, color)
    if "corbata" in acc:
        d.polygon([(x, y - 410 * s), (x - 14 * s, y - 330 * s), (x, y - 300 * s), (x + 14 * s, y - 330 * s)], fill=RED)
    manos = []
    for ang, codo in ((hi, rd), (ha, hd)):
        c = _p(*hombro, ang, 95 * s, dirx)
        m = _p(*c, ang + codo, 90 * s, dirx)
        _seg(d, hombro, c, w, color); _seg(d, c, m, w, color)
        manos.append(m)
    if "escoba" in acc:
        m = manos[0]
        a, b = (m[0] - dirx * 30 * s, m[1] - 120 * s), (m[0] + dirx * 40 * s, m[1] + 200 * s)
        d.line([a, b], fill=(150, 100, 60), width=int(10 * s))
        d.polygon([(b[0] - 40 * s, b[1]), (b[0] + 40 * s, b[1]), (b[0] + 55 * s, b[1] + 50 * s), (b[0] - 55 * s, b[1] + 50 * s)], fill=(240, 200, 80))
    if "portapapeles" in acc:
        m = manos[0]
        d.rounded_rectangle((m[0] - 40 * s, m[1] - 70 * s, m[0] + 40 * s, m[1] + 30 * s), int(6 * s), fill=(200, 160, 110), outline=color, width=4)
        d.rectangle((m[0] - 30 * s, m[1] - 55 * s, m[0] + 30 * s, m[1] + 20 * s), fill=WHITE)
    if "movil" in acc or pose in ("movil", "ok"):
        m = manos[1]
        d.rounded_rectangle((m[0] - 24 * s, m[1] - 62 * s, m[0] + 24 * s, m[1] + 18 * s), int(8 * s), fill=NAVY_D)
        d.rounded_rectangle((m[0] - 18 * s, m[1] - 54 * s, m[0] + 18 * s, m[1] + 8 * s), int(5 * s), fill=GREEN)
    # cabeza
    hr = 62 * s
    hc = (x, y - 430 * s - hr + 8 * s)
    d.ellipse((hc[0] - hr, hc[1] - hr, hc[0] + hr, hc[1] + hr), fill=SKIN, outline=color, width=w)
    if "pelo" in acc:
        d.chord((hc[0] - hr, hc[1] - hr, hc[0] + hr, hc[1] + hr), 180, 360, fill=color)
    if "gorra" in acc:
        d.chord((hc[0] - hr, hc[1] - hr - 6 * s, hc[0] + hr, hc[1] + hr * 0.6), 180, 360, fill=(40, 60, 90))
        xa, xb = sorted((hc[0], hc[0] + dirx * hr * 1.4))
        d.rectangle((xa, hc[1] - 18 * s, xb, hc[1] - 6 * s), fill=(40, 60, 90))
    ex = hc[0] + dirx * 14 * s
    for dx in (-20, 20):
        d.ellipse((ex + dx * s - 7 * s, hc[1] - 8 * s - 7 * s, ex + dx * s + 7 * s, hc[1] - 8 * s + 7 * s), fill=color)
    bb = (ex - 26 * s, hc[1] + 2 * s, ex + 26 * s, hc[1] + 36 * s)
    if cara == "feliz":
        d.arc(bb, 10, 170, fill=color, width=int(7 * s))
    elif cara == "triste":
        d.arc((bb[0], bb[1] + 22 * s, bb[2], bb[3] + 22 * s), 200, 340, fill=color, width=int(7 * s))
    else:
        d.line([(ex - 16 * s, hc[1] + 24 * s), (ex + 16 * s, hc[1] + 24 * s)], fill=color, width=int(7 * s))
    if cara == "triste" or pose == "estres":  # gota de sudor
        gx, gy = hc[0] - dirx * (hr + 6 * s), hc[1] - 10 * s + (t * 60 % 30) * s
        d.polygon([(gx, gy - 18 * s), (gx - 10 * s, gy + 4 * s), (gx + 10 * s, gy + 4 * s)], fill=(110, 180, 240))
        d.ellipse((gx - 10 * s, gy - 6 * s, gx + 10 * s, gy + 14 * s), fill=(110, 180, 240))
    return {"cabeza": hc, "manos": manos}


def suelo(img, y=1560, oscuro=False):
    ImageDraw.Draw(img).line([(60, y + 4), (W - 60, y + 4)], fill=(200, 210, 225) if not oscuro else (60, 90, 130), width=6)

def edificio(img, x, y, w, h, etiqueta, color=(226, 234, 244)):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y - h, x + w, y), 16, fill=color, outline=(190, 200, 215), width=4)
    for i in range(2):
        for j in range(int((h - 200) / 120)):
            wx, wy = x + 40 + i * (w - 140), y - h + 50 + j * 120
            d.rounded_rectangle((wx, wy, wx + 60, wy + 70), 8, fill=(255, 255, 255))
    d.rounded_rectangle((x + w / 2 - 50, y - 170, x + w / 2 + 50, y), 10, fill=NAVY)
    f = F(700, 34)
    tw = d.textlength(etiqueta, font=f)
    d.rounded_rectangle((x + w / 2 - tw / 2 - 18, y - h - 70, x + w / 2 + tw / 2 + 18, y - h - 14), 14, fill=NAVY)
    d.text((x + w / 2 - tw / 2, y - h - 64), etiqueta, font=f, fill=WHITE)

def mesa(img, x, y, w=420):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x - w / 2, y - 230, x + w / 2, y - 200), 8, fill=(180, 130, 90))
    d.rectangle((x - w / 2 + 20, y - 200, x - w / 2 + 40, y), fill=(160, 115, 80))
    d.rectangle((x + w / 2 - 40, y - 200, x + w / 2 - 20, y), fill=(160, 115, 80))

_HOJA = None
def hoja(rot, s=1.0):
    global _HOJA
    if _HOJA is None:
        h = Image.new("RGBA", (120, 150), (255, 255, 255, 255))
        d = ImageDraw.Draw(h)
        d.rectangle((0, 0, 119, 149), outline=(190, 200, 215), width=3)
        for i in range(6):
            d.line([(14, 22 + i * 20), (100 - (i % 3) * 18, 22 + i * 20)], fill=(120, 140, 190), width=4)
        _HOJA = h
    im = _HOJA.resize((int(120 * s), int(150 * s)), Image.BILINEAR) if s != 1 else _HOJA
    return im.rotate(rot, resample=Image.BILINEAR, expand=True)

def papeles_volando(img, cx, cy, t, n=9, radio=360):
    rng = random.Random(7)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi) + t * rng.uniform(0.3, 0.9)
        r = radio * rng.uniform(0.55, 1.0)
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r * 0.6 + math.sin(t * 3 + i) * 20
        h = hoja(rng.uniform(-40, 40) + t * 60 * rng.choice([-1, 1]), rng.uniform(0.7, 1.1))
        img.alpha_composite(h, (int(x - h.width / 2), int(y - h.height / 2)))

def burbuja(img, x, y, texto, t, t0=0.0, color=WHITE, txt=NAVY, size=46, check=False):
    """Bocadillo con texto; aparece con un 'pop' en t0."""
    if t < t0:
        return
    p = min(1, (t - t0) / 0.3)
    s = 0.6 + 0.4 * ease_back(p)
    f = F(800, size)
    dd = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines = texto.split("\n")
    tw = max(dd.textlength(l, font=f) for l in lines)
    extra = 70 if check else 0
    bw, bh = int(tw + 60 + extra), int(len(lines) * size * 1.25 + 44)
    b = G.rounded((bw, bh), 28, color)
    bd = ImageDraw.Draw(b)
    if check:
        bd.ellipse((24, bh / 2 - 26, 76, bh / 2 + 26), fill=BTN)
        bd.line([(37, bh / 2), (47, bh / 2 + 11), (64, bh / 2 - 11)], fill=WHITE, width=7)
    for i, l in enumerate(lines):
        bd.text((30 + extra, 20 + i * size * 1.25), l, font=f, fill=txt)
    b = G.shadow(b, 18, 10, 45)
    if s != 1:
        b = b.resize((max(1, int(b.width * s)), max(1, int(b.height * s))), Image.BILINEAR)
    img.alpha_composite(G.with_alpha(b, min(1, p * 2)), (int(x - b.width / 2), int(y - b.height / 2)))

def panel_movil(img, x, y, cab, filas, t, t0=0.0, sub="Ahora mismo", w=560):
    """Móvil grande con la app (filas = [(nombre, estado, ok?)])."""
    if t < t0:
        return
    p = ease(min(1, (t - t0) / 0.4))
    h = 220 + len(filas) * 118 + 40
    ph = G.rounded((w, h), 60, NAVY_D)
    sc = G.rounded((w - 32, h - 32), 46, (244, 247, 251))
    bar = G.grad((w - 32, 170), NAVY_D, GREEN).convert("RGBA")
    m = Image.new("L", bar.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, bar.width - 1, bar.height + 60), 46, fill=255)
    sc.paste(bar, (0, 0), m)
    d = ImageDraw.Draw(sc)
    d.text((34, 52), cab, font=F(800, 40), fill=WHITE)
    d.text((34, 106), sub, font=N(28), fill=(220, 238, 240))
    for i, fila in enumerate(filas):
        nombre, estado = fila[0], fila[1]
        ok = fila[2] if len(fila) > 2 else True
        if t - t0 < 0.45 + i * 0.18:
            continue
        yy = 200 + i * 118
        d.rounded_rectangle((20, yy, w - 52, yy + 104), 22, fill=WHITE)
        d.ellipse((40, yy + 36, 72, yy + 68), fill=BTN if ok else (230, 160, 60))
        d.text((92, yy + 14), nombre, font=F(700, 36), fill=NAVY)
        d.text((92, yy + 58), estado, font=N(28), fill=GREY)
    ph.paste(sc, (16, 16), sc)
    ph = G.shadow(ph, 30, 18, 55)
    img.alpha_composite(G.with_alpha(ph, p), (int(x - ph.width / 2), int(y + (1 - p) * 120)))


# ---------- escenas de monigotes (cada una es una función draw(img, t)) ----------
def esc_caos(o):
    """Dueño agobiado en su mesa, papeles volando y lo que diga el pósit."""
    def draw(img, t):
        suelo(img)
        mesa(img, 560, 1560)
        papeles_volando(img, 540, 900, t, 10, 380)
        monigote(img, 540, 1560, t, "estres", 1, 1.0, "triste", o.get("acc", ("corbata",)))
        if o.get("postit"):
            pz = G.postit(o["postit"]).resize((330, 330), Image.BILINEAR)
            img.alpha_composite(pz, (700, 760 + int(math.sin(t * 2) * 10)))
    return draw, [("papeles", 0.1, 0.9), ("papeles", 1.2, 0.6)]

def esc_llega(o):
    """Trabajador llega al sitio, saca el móvil y ficha: burbuja ✓."""
    lugar, hora = o.get("lugar", "Bar Txoko"), o.get("hora", "07:58")
    acc = tuple(o.get("acc", ()))
    def draw(img, t):
        suelo(img)
        edificio(img, 560, 1560, 420, 620, lugar)
        x = -120 + min(1, t / 1.4) * 520
        if t < 1.4:
            monigote(img, x, 1560, t, "andar", 1, 0.92, "normal", acc)
        else:
            monigote(img, 400, 1560, t, "movil", 1, 0.92, "feliz", acc)
            burbuja(img, 400, 860, f"Fichado {hora}", t, 1.75, check=True)
    return draw, [("tap", 1.6, 0.9), ("ding", 1.75, 0.7)]

def esc_jefe_movil(o):
    """Dueño tranquilo mirando el móvil; panel grande con quién está trabajando."""
    filas = o.get("filas", [("Ane", "Fichó 07:58", True), ("Iker", "Fichó 08:02", True), ("Marta", "Fichó 08:05", True)])
    def draw(img, t):
        suelo(img)
        monigote(img, 230, 1560, t, "movil", 1, 0.85, "feliz", o.get("acc", ("corbata",)))
        panel_movil(img, 700, 560, o.get("cab", "Quién está trabajando"), filas, t, 0.2, o.get("sub", "Ahora mismo"), 560)
    return draw, [("whoosh", 0.15, 0.8)] + [("pop", 0.65 + i * 0.18, 0.5) for i in range(len(filas))]

def esc_olvido(o):
    """Trabajador se va sin fichar: aviso en el móvil y lo arregla."""
    acc = tuple(o.get("acc", ()))
    def draw(img, t):
        suelo(img)
        if t < 1.2:
            monigote(img, 300 + t * 300, 1560, t, "andar", 1, 0.92, "normal", acc)
        else:
            monigote(img, 660, 1560, t, "movil", -1, 0.92, "feliz" if t > 2.2 else "normal", acc)
        burbuja(img, 540, 760, o.get("aviso", "¿Te has olvidado de\nfichar la salida?"), t, 1.2, color=(255, 244, 214), size=44)
        if t > 2.2:
            burbuja(img, 540, 980, o.get("ok", "Salida 16:02"), t, 2.2, check=True)
    return draw, [("campana", 1.2, 0.8), ("tap", 2.1, 0.8), ("ding", 2.2, 0.6)]

def esc_inspeccion(o):
    def draw(img, t):
        suelo(img)
        monigote(img, 780, 1560, t, "pie" if t < 1.6 else "feliz", -1, 0.92, "normal" if t < 1.6 else "feliz", ("gorra", "portapapeles"))
        monigote(img, 280, 1560, t, "pie" if t < 0.8 else "movil", 1, 0.92, "feliz", o.get("acc", ("corbata",)))
        burbuja(img, 760, 820, o.get("pide", "Registro de jornada,\npor favor"), t, 0.0, size=40)
        if t > 0.9:
            burbuja(img, 300, 1000, o.get("da", "Informe PDF"), t, 0.9, color=(225, 245, 235), txt=BTN, size=44, check=True)
    return draw, [("tap", 0.85, 0.8), ("sello", 1.0, 0.8), ("exito", 1.6, 0.5)]

def esc_feliz(o):
    def draw(img, t):
        suelo(img)
        monigote(img, 540, 1560, t, "feliz", 1, 1.0, "feliz", o.get("acc", ("corbata",)), salto=abs(math.sin(t * 6)) * 30)
        if o.get("texto"):
            burbuja(img, 540, 820, o["texto"], t, 0.1, color=(225, 245, 235), txt=BTN)
    return draw, [("exito", 0.1, 0.6)]

def esc_calcula(o):
    """Dueño con la calculadora: números flotando con interrogaciones."""
    nums = o.get("numeros", ["38h?", "41,5?", "¿40?", "37h?"])
    def draw(img, t):
        suelo(img)
        mesa(img, 560, 1560)
        monigote(img, 540, 1560, t, "brazos", 1, 1.0, "triste", o.get("acc", ("corbata",)))
        d = ImageDraw.Draw(img)
        for i, n in enumerate(nums):
            a = i * 1.6 + t * 0.8
            x, y = 540 + math.cos(a) * 330, 860 + math.sin(a) * 160
            d.text((x - 60, y), n, font=F(800, 64), fill=RED if i % 2 else NAVY, stroke_width=6, stroke_fill=WHITE)
    return draw, [("teclear", 0.2, 0.7), ("teclear", 1.4, 0.5)]

ESCENAS = {"caos": esc_caos, "llega": esc_llega, "jefe_movil": esc_jefe_movil, "olvido": esc_olvido,
           "inspeccion": esc_inspeccion, "feliz": esc_feliz, "calcula": esc_calcula}


def plano_cierre(texto="Pruébalo gratis", voz_txt="Fíchalo. Link en la bio.", acento=None):
    bg, els = G.scene_elements({"tipo": "cierre", "texto": texto, "acento": acento})
    def draw(img, t):
        fr = G.render_frame(Image.new("RGBA", (W, H), (0, 0, 0, 0)), els, t, None)
        img.alpha_composite(fr)
    p = plano_con_voz(voz_txt, draw, "claro", [("whoosh", 0.0, 0.7), ("pop", 0.6, 0.5)], extra=1.0, minimo=2.8, subs=False)
    return p


# =====================================================================
# Montaje: planos → mp4 (vídeo + audio)
# =====================================================================
def montar(planos, out_path, estilo_musica="lofi", seed=0, overlay=None, subs_y=1180, gain_musica=0.32):
    starts, t = [], 0.0
    for p in planos:
        starts.append(t); t += p.dur
    dur = t
    m = A.Mezcla(dur)
    for p, s in zip(planos, starts):
        if p.voz:
            m.add(p.voz[0], s + p.voz_t0, 1.0, voz=True)
        for nombre, tt, g in p.sfx:
            m.add(A.SFX[nombre](), s + tt, g)
        if s > 0:
            m.add(A.whoosh(), s - 0.1, 0.5)
    m.musica(A.musica(dur, estilo_musica, seed), gain_musica)
    wav = out_path + ".wav"
    m.guardar(wav)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-t", f"{dur:.2f}",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
    for fi in range(int(dur * FPS)):
        tt = fi / FPS
        i = max(k for k in range(len(starts)) if starts[k] <= tt)
        frame = frame_en(planos[i], tt - starts[i], tt, overlay, subs_y, i == 0)
        ff.stdin.write(frame.convert("RGBA").tobytes())
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    return dur


def frame_en(p, tl, tg, overlay, subs_y, primero=False):
    img = fondo(p.fondo, tg)
    # entrada: zoom pequeño al empezar el plano (menos en el primero, que debe verse entero desde el fotograma 0)
    p.draw(img, tl)
    if overlay and p.subs is not False:
        overlay(img, tg)
    if p.voz and p.subs:
        subtitulos(img, p.voz[2], tl - p.voz_t0, p.voz[1], subs_y, oscuro=p.fondo in ("oscuro", "vivo"))
    if tl < 0.18 and not primero:
        z = 1.06 - 0.06 * ease(tl / 0.18)
        zw, zh = int(W * z), int(H * z)
        img = img.resize((zw, zh), Image.BILINEAR).crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H))
    return img


def guardar_portada(img, out_jpg, oscuro=False):
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img)
    lg = G.LOGO.resize((66, 88), Image.LANCZOS)
    f = F(700, 52)
    tw = d.textlength("fichalo.app", font=f)
    x0, y0 = int((W - (66 + 22 + tw)) / 2), 1700
    pill = G.rounded((int(66 + 22 + tw + 70), 124), 62, (255, 255, 255, 235) if oscuro else (18, 52, 96, 240))
    img.alpha_composite(pill, (x0 - 35, y0 - 18))
    img.alpha_composite(lg, (x0, y0))
    d.text((x0 + 66 + 22, y0 + 14), "fichalo.app", font=f, fill=NAVY if oscuro else WHITE)
    img.convert("RGB").save(out_jpg, "JPEG", quality=90)


# =====================================================================
# FORMATO monigotes
# =====================================================================
def construir_monigotes(reel):
    tit = reel["titular"]
    oscuro = False
    planos = []
    for e in reel["escenas"]:
        draw, sfx = ESCENAS[e["escena"]](e)
        planos.append(plano_con_voz(e["voz"], draw, e.get("fondo", "claro"), sfx, minimo=e.get("minimo", 2.6)))
    planos.append(plano_cierre(reel.get("cierre", "Pruébalo gratis"), reel.get("voz_cierre", "Fíchalo. Link en la bio.")))
    overlay = lambda img, t: titular(img, tit, reel.get("acento"), oscuro, 150)
    yb = titular(Image.new("RGBA", (W, H)), tit, reel.get("acento"), oscuro, 150)
    return planos, overlay, yb + 40

# =====================================================================
# FORMATO chat
# =====================================================================
def _avatar(letra, col, r=44):
    a = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    d = ImageDraw.Draw(a)
    d.ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=col)
    f = F(800, int(r * 1.0))
    tw = d.textlength(letra, font=f)
    d.text((r - tw / 2, r * 0.45), letra, font=f, fill=WHITE)
    return a

def _sin_emoji(t):
    return "".join(c for c in t if ord(c) < 0x2190).replace("  ", " ").strip()

def _burbuja_chat(texto, mio, foto=None, hora="09:12"):
    texto = _sin_emoji(texto)
    f = N(46)
    maxw = 700
    dd = ImageDraw.Draw(Image.new("L", (1, 1)))
    # partir en líneas
    lines, cur = [], ""
    for wd in texto.split():
        if dd.textlength((cur + " " + wd).strip(), font=f) > maxw - 60:
            lines.append(cur); cur = wd
        else:
            cur = (cur + " " + wd).strip()
    if cur:
        lines.append(cur)
    tw = max([dd.textlength(l, font=f) for l in lines] + [180])
    fh = 0
    if foto is not None:
        fh = foto.height + 16
        tw = max(tw, foto.width - 10)
    bw, bh = int(tw + 60), int(fh + len(lines) * 56 + 70)
    b = G.rounded((bw, bh), 30, (214, 245, 226) if mio else WHITE)
    d = ImageDraw.Draw(b)
    y = 18
    if foto is not None:
        b.alpha_composite(foto, (16, 16)); y = 16 + fh
    for l in lines:
        d.text((30, y), l, font=f, fill=(30, 40, 50)); y += 56
    d.text((bw - 110 - (40 if mio else 0), bh - 42), hora, font=N(26), fill=(130, 140, 150))
    if mio:
        for dx in (0, 12):
            d.line([(bw - 66 + dx, bh - 30), (bw - 60 + dx, bh - 24), (bw - 48 + dx, bh - 38)], fill=(70, 150, 230), width=3)
    return G.shadow(b, 10, 4, 25)

def _foto_borrosa(lineas):
    p = G.papel(lineas).convert("RGBA")
    p = p.resize((p.width * 46 // 100, p.height * 46 // 100), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.6))
    fondo_ = Image.new("RGBA", (p.width + 20, p.height + 20), (150, 140, 120, 255))
    fondo_.alpha_composite(p.rotate(8, expand=False), (10, 10))
    return fondo_

def construir_chat(reel):
    msgs = reel["mensajes"]
    contacto = reel["contacto"]
    tit = reel["titular"]
    bubbles = []
    for i, mm in enumerate(msgs):
        foto = _foto_borrosa(mm["foto"]) if mm.get("foto") else None
        bubbles.append((mm.get("de") == "yo", _burbuja_chat(mm.get("texto", ""), mm.get("de") == "yo", foto, mm.get("hora", f"20:{14 + i:02d}"))))
    # tiempos: el primer mensaje ya está a la vista en el fotograma 0
    tiempos, t = [], 0.0
    for i, (mio, b) in enumerate(bubbles):
        tiempos.append(t)
        t += 1.25 + min(1.6, len(msgs[i].get("texto", "")) / 38) + (0.8 if msgs[i].get("foto") else 0)
    dur_chat = t + 0.6
    av = _avatar(contacto[0].upper(), TEAL)
    top, bottom = 490, 1560

    def draw(img, tl):
        d = ImageDraw.Draw(img)
        # cabecera de la app de mensajes (genérica)
        d.rounded_rectangle((40, 360, W - 40, 470), 28, fill=NAVY_D)
        img.alpha_composite(av, (70, 371))
        d.text((175, 376), contacto, font=F(700, 40), fill=WHITE)
        escribiendo = any(tiempos[k] - 0.7 <= tl < tiempos[k] and not bubbles[k][0] for k in range(1, len(tiempos)))
        d.text((175, 424), "escribiendo..." if escribiendo else "en línea", font=N(28), fill=(170, 230, 200))
        # pila de mensajes visibles, se desplaza hacia arriba si no caben
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        vis = [k for k in range(len(bubbles)) if tiempos[k] <= tl]
        hs = [bubbles[k][1].height + 18 for k in vis]
        total = sum(hs)
        y = bottom - total if total > bottom - top - 40 else top + 40
        for k, hh in zip(vis, hs):
            mio, b = bubbles[k]
            p = min(1, (tl - tiempos[k]) / 0.22) if k > 0 else 1
            s = 0.85 + 0.15 * ease_back(p)
            bb = b if s == 1 else b.resize((max(1, int(b.width * s)), max(1, int(b.height * s))), Image.BILINEAR)
            x = W - 50 - bb.width if mio else 50
            if y + hh > top:
                capa.alpha_composite(G.with_alpha(bb, min(1, p * 1.6)), (int(x), int(y)))
            y += hh
        if escribiendo:
            dots = G.rounded((150, 80), 30, WHITE)
            dd = ImageDraw.Draw(dots)
            for j in range(3):
                yy = 40 + math.sin(tl * 10 + j) * 6
                dd.ellipse((28 + j * 36 - 9, yy - 9, 28 + j * 36 + 9, yy + 9), fill=(150, 160, 170))
            capa.alpha_composite(dots, (50, min(bottom - 90, int(y))))
        img.alpha_composite(capa.crop((0, top + 5, W, bottom + 100)), (0, top + 5))
        titular(img, tit, reel.get("acento"), False, 120)

    sfx = []
    for k in range(1, len(bubbles)):
        sfx.append(("mensaje" if not bubbles[k][0] else "tap", tiempos[k], 0.7))
        if bubbles[k][0]:
            sfx.append(("teclear", max(0, tiempos[k] - 0.7), 0.4))
    p_chat = Plano(dur_chat, draw, "cielo", sfx)
    planos = [p_chat]
    if reel.get("giro"):
        g = reel["giro"]
        def draw2(img, t):
            titular(img, g["texto"], g.get("acento"), False, 200)
            panel_movil(img, 540, 620, g.get("cab", "Horas de octubre"), [tuple(x) for x in g["filas"]], t, 0.1, g.get("sub", "Calculado automáticamente"), 600)
        planos.append(Plano(3.0, draw2, "menta", [("whoosh", 0, 0.7)] + [("pop", 0.55 + i * 0.18, 0.5) for i in range(len(g["filas"]))]))
    planos.append(plano_cierre(reel.get("cierre", "Pruébalo gratis"), reel.get("voz_cierre", "Fíchalo. Link en la bio.")))
    return planos, None, 1290

# =====================================================================
# FORMATO quiz  "¿Legal o multa?"
# =====================================================================
def construir_quiz(reel):
    planos = []
    preguntas = reel["preguntas"]
    total = len(preguntas)
    for qi, q in enumerate(preguntas):
        v, dv = A.voz(q["situacion"])
        t_cuenta = 0.15 + dv + 0.25
        t_resp = t_cuenta + 2.1
        dur = t_resp + 2.6

        def draw(img, t, q=q, qi=qi, t_cuenta=t_cuenta, t_resp=t_resp):
            d = ImageDraw.Draw(img)
            # cabecera: ¿LEGAL o MULTA?
            f = F(800, 92)
            x = (W - (d.textlength("¿LEGAL ", font=f) + d.textlength("o ", font=f) + d.textlength("MULTA?", font=f))) / 2
            d.text((x, 150), "¿LEGAL ", font=f, fill=(110, 220, 170)); x += d.textlength("¿LEGAL ", font=f)
            d.text((x, 150), "o ", font=f, fill=WHITE); x += d.textlength("o ", font=f)
            d.text((x, 150), "MULTA?", font=f, fill=(255, 120, 110))
            sub = f"Pregunta {qi + 1} de {total}"
            d.text(((W - d.textlength(sub, font=N(40))) / 2, 268), sub, font=N(40), fill=(190, 205, 225))
            # tarjeta con la situación
            card = G.rounded((940, 520), 40, WHITE)
            tb = bloque(q["situacion"], q.get("acento"), 800, 70, 840, 48, NAVY, 5)
            card.alpha_composite(tb, ((940 - tb.width) // 2, (520 - tb.height) // 2))
            img.alpha_composite(G.shadow(card, 30, 18, 60), (70 - 56, 400 - 56))
            # cuenta atrás
            if t_cuenta <= t < t_resp:
                n = 3 - int((t - t_cuenta) / 0.7)
                fr = ((t - t_cuenta) % 0.7) / 0.7
                r = 120
                cx, cy = W // 2, 1140
                d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(80, 110, 150), width=14)
                d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * (1 - fr), fill=(110, 220, 170), width=14)
                fn = F(800, 130)
                d.text((cx - d.textlength(str(max(1, n)), font=fn) / 2, cy - 82), str(max(1, n)), font=fn, fill=WHITE)
            elif t >= t_resp:
                multa = q["respuesta"].upper() == "MULTA"
                p = min(1, (t - t_resp) / 0.25)
                s = 1.6 - 0.6 * ease(p)
                lab = "MULTA" if multa else "LEGAL"
                col = (230, 70, 60) if multa else BTN
                st = G.rounded((560, 170), 30, col)
                sd = ImageDraw.Draw(st)
                fl = F(800, 110)
                sd.text(((560 - sd.textlength(lab, font=fl)) / 2, 18), lab, font=fl, fill=WHITE)
                st = st.rotate(-6, resample=Image.BICUBIC, expand=True)
                st = st.resize((int(st.width * s), int(st.height * s)), Image.BILINEAR)
                img.alpha_composite(G.with_alpha(st, p), ((W - st.width) // 2, 1000 - st.height // 2 + 60))
                if t - t_resp > 0.35:
                    pb = bloque(q["porque"], q.get("acento_porque"), 700, 54, 920, 40, WHITE, 4, True)
                    a = min(1, (t - t_resp - 0.35) / 0.3)
                    img.alpha_composite(G.with_alpha(pb, a), ((W - pb.width) // 2, 1210))

        sfx = [("tic", t_cuenta + k * 0.7, 0.8) for k in range(3)]
        sfx.append(("sello", t_resp, 0.9))
        sfx.append(("error" if q["respuesta"].upper() == "MULTA" else "exito", t_resp + 0.05, 0.7))
        p = Plano(dur, draw, "oscuro", sfx, (v, dv, q["situacion"]), 0.15, subs=False)
        planos.append(p)
    planos.append(plano_cierre(reel.get("cierre", "Tu registro, en regla"), reel.get("voz_cierre", "Con Fíchalo, tu registro de jornada siempre en regla. Link en la bio.")))
    return planos, None, 1290

# =====================================================================
# FORMATO voz (subtítulos grandes + imagen que acompaña)
# =====================================================================
def _visual(v):
    if not v:
        return None
    if v.get("postit"):
        return G.postit(v["postit"]).resize((470, 470), Image.BILINEAR)
    if v.get("papel"):
        p = G.papel(v["papel"]); return p.resize((p.width * 75 // 100, p.height * 75 // 100), Image.BILINEAR)
    if v.get("emoji"):
        return G.emoji_disco(v["emoji"], True).resize((460, 460), Image.BILINEAR)
    if v.get("numero"):
        return G.text_block(v["numero"], v["numero"], F(800, 300), WHITE, acc_c1=(110, 220, 170), acc_c2=GREEN)
    return None

def construir_voz(reel):
    planos = []
    tit = reel["titular"]
    for i, fr in enumerate(reel["frases"]):
        vis = _visual(fr)
        movil = fr.get("movil")

        def draw(img, t, vis=vis, movil=movil, i=i):
            if movil:
                panel_movil(img, 540, 430, movil["cab"], [tuple(x) for x in movil["filas"]], t, 0.0 if i else -1, movil.get("sub", "Ahora mismo"), 540)
            elif vis is not None:
                p = 1 if i == 0 else min(1, t / 0.3)
                s = 0.8 + 0.2 * ease_back(p)
                im = vis if s == 1 else vis.resize((max(1, int(vis.width * s)), max(1, int(vis.height * s))), Image.BILINEAR)
                img.alpha_composite(G.with_alpha(im, p), ((W - im.width) // 2, 640 - im.height // 2 + int(math.sin(t * 2) * 10)))
        sfx = [("pop", 0.05, 0.5)] if (vis is not None or movil) and i else []
        planos.append(plano_con_voz(fr["voz"], draw, "vivo", sfx, extra=0.25, minimo=1.6))
    planos.append(plano_cierre(reel.get("cierre", "Pruébalo gratis"), reel.get("voz_cierre", "Fíchalo. Link en la bio.")))
    overlay = lambda img, t: titular(img, tit, reel.get("acento"), True, 120)
    return planos, overlay, 1230

# =====================================================================
# FORMATO postit (el de siempre) con música y efectos
# =====================================================================
def render_postit(reel, out_path):
    def musica_fx(n_esc, starts, out_wav):
        dur = G.DUR
        m = A.Mezcla(dur)
        esc = reel["escenas"]
        m.add(A.pop(), 0.05, 0.6)
        for i, s in enumerate(starts[1:], 1):
            m.add(A.whoosh(), s - 0.12, 0.7)
            sc = esc[i]
            if sc["tipo"] in ("movil", "tabla"):
                m.add(A.pop(), s + 0.3, 0.5)
                for k in range(len(sc.get("filas", [])[:5])):
                    m.add(A.tap(), s + 0.75 + 0.22 * k, 0.6)
                if sc.get("estado"):
                    m.add(A.exito(), s + 2.0, 0.6)
            if sc["tipo"] == "cierre":
                m.add(A.ding(), s + 0.6, 0.4)
        m.musica(A.musica(dur, "animada", zlib.crc32(reel["id"].encode()) % 97), 0.45)
        m.guardar(out_wav)
    orig = G.musica
    G.musica = musica_fx
    try:
        G.render_reel(reel, out_path)
    finally:
        G.musica = orig


CONSTRUIR = {"monigotes": construir_monigotes, "chat": construir_chat, "quiz": construir_quiz, "voz": construir_voz}
MUSICA = {"monigotes": "lofi", "chat": "lofi", "quiz": "tension", "voz": "animada"}


def render(reel, out_mp4, out_jpg):
    fmt = reel["formato"]
    if fmt == "postit":
        render_postit(reel, out_mp4)
        G.portada(reel, out_jpg)
        return
    planos, overlay, sy = CONSTRUIR[fmt](reel)
    montar(planos, out_mp4, MUSICA[fmt], zlib.crc32(reel["id"].encode()) % 97, overlay, sy,
           0.22 if fmt in ("monigotes", "voz", "quiz") else 0.4)
    # portada: el primer plano ya avanzado (todo visible), sin subtítulos
    p0 = planos[0]
    img = fondo(p0.fondo, 1.0)
    p0.draw(img, min(p0.dur - 0.1, 2.4 if fmt == "monigotes" else 1.2))
    if overlay:
        overlay(img, 1.0)
    guardar_portada(img, out_jpg, p0.fondo in ("oscuro", "vivo"))
