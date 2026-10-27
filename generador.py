"""Generador de Reels de Fíchalo (1080x1920, 15 s) con el estilo de la marca.

Uso:  python3 generador.py guiones/LOTE.json videos/
Cada reel del JSON tiene: id, escenas[], copy, hashtags. Tipos de escena:
  titulo  {texto, acento?, fondo?: "claro"|"oscuro", emoji_img?: no se usa}
  dato    {numero, texto, acento?}
  movil   {titulo, acento?, cabecera, filas: [[izq, der], ...], boton?, estado?}
  tabla   {titulo, acento?, cabecera, filas: [[nombre, valor], ...], pie?: [txt, valor]}
  versus  {a_etiqueta, a_texto, b_etiqueta, b_texto}
  cierre  {texto, acento?}
"""
import json, os, sys, math, subprocess, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1080, 1920, 30, 15.0
FD = os.path.join(BASE, "assets", "fonts")

def F(w, s):
    return ImageFont.truetype(os.path.join(FD, f"montserrat-{w}.ttf"), s)
def N(s):
    return ImageFont.truetype(os.path.join(FD, "nunito-600.ttf"), s)

NAVY = (18, 52, 96)
NAVY_D = (16, 49, 91)
NAVY_L = (19, 71, 115)
TEAL = (31, 110, 138)
GREEN = (60, 192, 138)
BTN = (30, 150, 96)
GREY = (150, 160, 178)
LINE = (232, 236, 242)
WHITE = (255, 255, 255)
LOGO = Image.open(os.path.join(BASE, "assets", "logo.png")).convert("RGBA")


# ---------- utilidades ----------
def grad(size, c1, c2, horizontal=True):
    w, h = size
    g = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(g)
    n = w if horizontal else h
    for i in range(n):
        t = i / max(1, n - 1)
        c = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
        if horizontal:
            d.line([(i, 0), (i, h)], fill=c)
        else:
            d.line([(0, i), (w, i)], fill=c)
    return g


def text_block(text, acento, font, color, acc_c1=TEAL, acc_c2=GREEN, max_w=960, lh=1.18, align="center"):
    """Devuelve RGBA con el texto (líneas por \\n), palabra(s) de acento con degradado."""
    lines = text.split("\n")
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    asc, desc = font.getmetrics()
    lhp = int((asc + desc) * lh)
    widths = [tmp.textlength(l, font=font) for l in lines]
    bw = int(min(max(widths) + 20, W))
    bh = lhp * len(lines) + 10
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    acc_mask = Image.new("L", (bw, bh), 0)
    am = ImageDraw.Draw(acc_mask)
    for i, l in enumerate(lines):
        x = (bw - widths[i]) / 2 if align == "center" else 10
        y = i * lhp
        if acento and acento.lower() in l.lower():
            k = l.lower().index(acento.lower())
            pre, mid, post = l[:k], l[k:k + len(acento)], l[k + len(acento):]
            d.text((x, y), pre, font=font, fill=color)
            xm = x + tmp.textlength(pre, font=font)
            am.text((xm, y), mid, font=font, fill=255)
            d.text((xm + tmp.textlength(mid, font=font), y), post, font=font, fill=color)
        else:
            d.text((x, y), l, font=font, fill=color)
    bbox = acc_mask.getbbox()
    if bbox:
        g = grad((bbox[2] - bbox[0], bbox[3] - bbox[1]), acc_c1, acc_c2).convert("RGBA")
        layer = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        layer.paste(g, (bbox[0], bbox[1]))
        layer.putalpha(acc_mask)
        img = Image.alpha_composite(img, layer)
    return img


def auto_font(text, weight, start, max_w=960, min_s=56):
    s = start
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    while s > min_s:
        f = F(weight, s)
        if max(tmp.textlength(l, font=f) for l in text.split("\n")) <= max_w:
            return f
        s -= 4
    return F(weight, min_s)


def shadow(img, radius=28, off=14, alpha=40):
    w, h = img.size
    pad = radius * 2
    sh = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: alpha if v > 0 else 0)
    blk = Image.new("RGBA", (w, h), NAVY + (0,))
    blk.putalpha(a)
    sh.paste(blk, (pad, pad + off), blk)
    sh = sh.filter(ImageFilter.GaussianBlur(radius))
    sh.alpha_composite(img, (pad, pad))
    return sh


def rounded(size, r, fill):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=fill)
    return img


def with_alpha(img, a):
    if a >= 0.999:
        return img
    out = img.copy()
    out.putalpha(img.split()[3].point(lambda v: int(v * a)))
    return out


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_back(t):
    t = max(0.0, min(1.0, t))
    c = 1.4
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


# ---------- piezas ----------
def card_rows(cab, filas, width, pie=None, boton=None, estado=None):
    """Tarjeta tipo app: cabecera con degradado + filas."""
    rh = 104
    head_h = 96
    extra = (110 if pie else 0) + (130 if boton else 0) + (90 if estado else 0)
    h = head_h + rh * len(filas) + 30 + extra
    card = rounded((width, h), 28, WHITE)
    hd = grad((width, head_h), NAVY_D, GREEN).convert("RGBA")
    m = Image.new("L", (width, head_h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, width - 1, head_h + 40), 28, fill=255)
    card.paste(hd, (0, 0), m)
    d = ImageDraw.Draw(card)
    d.text((34, 28), cab, font=F(700, 36), fill=WHITE)
    rows = []
    y = head_h + 10
    for izq, der in filas:
        rows.append((y, izq, der))
        y += rh
    y_after = y + 10
    return card, rows, y_after


def draw_row(card, y, izq, der, width):
    d = ImageDraw.Draw(card)
    d.line([(30, y + rh_line(0)), (width - 30, y + rh_line(0))], fill=LINE, width=2)
    d.text((34, y + 30), izq, font=F(700, 38), fill=NAVY)
    tw = d.textlength(der, font=F(800, 38))
    d.text((width - 34 - tw, y + 30), der, font=F(800, 38), fill=NAVY)


def rh_line(_):
    return 100



EMOJI_F = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def emoji_img(ch, size):
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=EMOJI_F, embedded_color=True)
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

def emoji_disco(ch, oscuro=False):
    d = 560
    disco = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    ImageDraw.Draw(disco).ellipse((0, 0, d - 1, d - 1), fill=(255, 255, 255, 40) if oscuro else (231, 240, 247, 255))
    e = emoji_img(ch, 380)
    disco.alpha_composite(e, ((d - e.width) // 2, (d - e.height) // 2))
    return disco

def postit(texto):
    w = 560
    p = Image.new("RGBA", (w, w), (255, 224, 102, 255))
    d = ImageDraw.Draw(p)
    d.rectangle((0, 0, w, 60), fill=(250, 214, 80))
    f = ImageFont.truetype(os.path.join(FD, "caveat-700.ttf"), 84)
    y = 110
    for line in texto.split("\n"):
        d.text((50, y), line, font=f, fill=(60, 50, 40))
        y += 96
    p = p.rotate(-5, resample=Image.BICUBIC, expand=True)
    return shadow(p, 24, 16, 60)

def papel(lineas):
    w, h = 620, 760
    p = rounded((w, h), 12, WHITE)
    d = ImageDraw.Draw(p)
    d.text((44, 40), lineas[0], font=F(800, 40), fill=NAVY)
    fh = ImageFont.truetype(os.path.join(FD, "caveat-700.ttf"), 56)
    y = 120
    for l in lineas[1:]:
        d.line([(40, y + 66), (w - 40, y + 66)], fill=LINE, width=3)
        d.text((48, y), l, font=fh, fill=(40, 60, 140))
        y += 84
    p = p.rotate(3, resample=Image.BICUBIC, expand=True)
    return shadow(p, 24, 16, 50)

# ---------- escenas -> elementos animados ----------
class El:
    def __init__(self, img, x, y, t0, kind="up", dur=0.45):
        self.img, self.x, self.y, self.t0, self.kind, self.dur = img, x, y, t0, kind, dur


def scene_elements(sc):
    """Devuelve (fondo, [El]) para una escena."""
    tipo = sc["tipo"]
    oscuro = sc.get("fondo") == "oscuro"
    els = []
    if tipo == "titulo":
        f = auto_font(sc["texto"], 800, 108)
        col = WHITE if oscuro else NAVY
        tb = text_block(sc["texto"], sc.get("acento"), f, col,
                        acc_c1=(110, 220, 170) if oscuro else TEAL, acc_c2=GREEN)
        els.append(El(tb, (W - tb.width) // 2, (H - tb.height) // 2 - 120, 0.0))
    elif tipo == "dato":
        num = sc["numero"]
        f = F(800, 300 if len(num) <= 4 else 220)
        nb = text_block(num, num, f, NAVY, acc_c1=NAVY_D, acc_c2=TEAL)
        tb = text_block(sc["texto"], sc.get("acento"), auto_font(sc["texto"], 800, 92), NAVY)
        y0 = (H - nb.height - tb.height) // 2 - 120
        els.append(El(nb, (W - nb.width) // 2, y0, 0.0, "pop"))
        els.append(El(tb, (W - tb.width) // 2, y0 + nb.height, 0.35))
    elif tipo in ("movil", "tabla"):
        tt = text_block(sc["titulo"], sc.get("acento"), auto_font(sc["titulo"], 800, 88), NAVY)
        els.append(El(tt, (W - tt.width) // 2, 300, 0.0))
        if tipo == "movil":
            pw, ph = 600, 1060
            phone = rounded((pw, ph), 70, NAVY_D)
            screen = grad((pw - 36, ph - 36), WHITE, (240, 245, 250), horizontal=False).convert("RGBA")
            sm = Image.new("L", screen.size, 0)
            ImageDraw.Draw(sm).rounded_rectangle((0, 0, screen.width - 1, screen.height - 1), 54, fill=255)
            bar = grad((screen.width, 170), NAVY_D, GREEN).convert("RGBA")
            screen.paste(bar, (0, 0))
            sd = ImageDraw.Draw(screen)
            sd.rounded_rectangle((screen.width // 2 - 80, 18, screen.width // 2 + 80, 48), 15, fill=NAVY_D)
            sd.text((40, 92), "fichalo.app", font=F(700, 34), fill=WHITE)
            sd.text((40, 132), "Centro principal", font=N(24), fill=(220, 235, 240))
            sd.text((40, 210), sc["cabecera"], font=F(800, 38), fill=NAVY)
            phone.paste(screen, (18, 18), sm)
            px, py = (W - pw) // 2, 560
            els.append(El(shadow(phone), px - 56, py - 56, 0.25, "pop", 0.55))
            # filas como tarjetas dentro del móvil
            y = py + 18 + 280
            for i, (a, b) in enumerate(sc["filas"][:5]):
                row = rounded((pw - 100, 112), 22, (243, 246, 250))
                rd = ImageDraw.Draw(row)
                rd.text((28, 20), a, font=F(700, 34), fill=NAVY)
                rd.text((28, 64), b, font=N(26), fill=GREY)
                els.append(El(row, px + 50, y, 0.75 + 0.22 * i, "up", 0.35))
                y += 128
            if sc.get("boton"):
                btn = rounded((pw - 100, 96), 22, BTN)
                bd = ImageDraw.Draw(btn)
                tw = bd.textlength(sc["boton"], font=F(700, 36))
                bd.text(((btn.width - tw) / 2, 26), sc["boton"], font=F(700, 36), fill=WHITE)
                els.append(El(btn, px + 50, y + 10, 0.75 + 0.22 * len(sc["filas"][:5]) + 0.1, "pop", 0.35))
                y += 120
            if sc.get("estado"):
                st = rounded((pw - 100, 84), 22, (225, 245, 235))
                sd2 = ImageDraw.Draw(st)
                sd2.ellipse((24, 22, 64, 62), fill=BTN)
                sd2.line([(34, 42), (42, 50), (56, 34)], fill=WHITE, width=5)
                sd2.text((84, 22), sc["estado"], font=F(700, 32), fill=BTN)
                els.append(El(st, px + 50, y + 10, 2.0, "pop", 0.35))
        else:
            cw = 900
            filas = sc["filas"][:6]
            hh, rh = 110, 104
            ch = hh + rh * len(filas) + (120 if sc.get("pie") else 20)
            card = rounded((cw, ch), 30, WHITE)
            hd = grad((cw, hh), NAVY_D, GREEN).convert("RGBA")
            m = Image.new("L", (cw, hh), 0)
            ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, hh + 40), 30, fill=255)
            card.paste(hd, (0, 0), m)
            ImageDraw.Draw(card).text((40, 34), sc["cabecera"], font=F(700, 40), fill=WHITE)
            cx, cy = (W - cw) // 2, 640
            els.append(El(shadow(card), cx - 56, cy - 56, 0.25, "pop", 0.5))
            for i, (a, b) in enumerate(filas):
                row = Image.new("RGBA", (cw - 60, rh), (0, 0, 0, 0))
                rd = ImageDraw.Draw(row)
                rd.text((10, 30), a, font=F(700, 40), fill=NAVY)
                tw = rd.textlength(b, font=F(800, 40))
                rd.text((cw - 70 - tw, 30), b, font=F(800, 40), fill=NAVY)
                rd.line([(0, rh - 2), (cw - 60, rh - 2)], fill=LINE, width=2)
                els.append(El(row, cx + 30, cy + hh + i * rh, 0.7 + 0.2 * i, "up", 0.3))
            if sc.get("pie"):
                a, b = sc["pie"]
                pie = rounded((cw - 40, 90), 20, (243, 246, 250))
                pd = ImageDraw.Draw(pie)
                pd.text((26, 26), a, font=N(32), fill=GREY)
                tw = pd.textlength(b, font=F(800, 44))
                pd.text((cw - 40 - 26 - tw, 18), b, font=F(800, 44), fill=NAVY)
                els.append(El(pie, cx + 20, cy + hh + len(filas) * rh + 20, 0.7 + 0.2 * len(filas) + 0.2, "pop", 0.35))
    elif tipo == "objeto":
        # gancho: pregunta directa arriba + objeto reconocible grande (emoji, pósit o papel)
        col = WHITE if oscuro else NAVY
        q = text_block(sc["pregunta"], sc.get("acento"), auto_font(sc["pregunta"], 800, 96), col,
                       acc_c1=(110, 220, 170) if oscuro else TEAL, acc_c2=GREEN)
        els.append(El(q, (W - q.width) // 2, 250, 0.0))
        cy = max(250 + q.height + 80, 820)
        if sc.get("postit"):
            ob = postit(sc["postit"])
        elif sc.get("papel"):
            ob = papel(sc["papel"])
        else:
            ob = emoji_disco(sc.get("emoji", "⏰"), oscuro)
        els.append(El(ob, (W - ob.width) // 2, cy, 0.15, "flota", 0.5))
        if sc.get("subtitulo"):
            st = text_block(sc["subtitulo"], None, N(44), (200, 210, 225) if oscuro else GREY)
            els.append(El(st, (W - st.width) // 2, cy + ob.height + 40, 0.6))
    elif tipo == "versus":
        y = 420
        for et, tx, col, bg, t0 in ((sc["a_etiqueta"], sc["a_texto"], (214, 69, 65), (253, 232, 230), 0.0),
                                    (sc["b_etiqueta"], sc["b_texto"], BTN, (225, 245, 235), 1.2)):
            pill_f = F(700, 34)
            tw = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(et, font=pill_f)
            pill = rounded((int(tw) + 56, 64), 32, bg)
            ImageDraw.Draw(pill).text((28, 12), et, font=pill_f, fill=col)
            els.append(El(pill, (W - pill.width) // 2, y, t0, "pop", 0.35))
            tb = text_block(tx, None, auto_font(tx, 800, 84), NAVY)
            els.append(El(tb, (W - tb.width) // 2, y + 100, t0 + 0.15))
            y += 100 + tb.height + 140
    elif tipo == "cierre":
        lg = LOGO.resize((180, 240), Image.LANCZOS)
        els.append(El(lg, (W - 180) // 2, 360, 0.0, "pop", 0.5))
        wm = text_block("fichalo.app", None, F(500, 96), NAVY)
        els.append(El(wm, (W - wm.width) // 2, 640, 0.15))
        q = text_block(sc["texto"], sc.get("acento"), auto_font(sc["texto"], 800, 72), NAVY)
        els.append(El(q, (W - q.width) // 2, 860, 0.35))
        btn = rounded((940, 150), 36, BTN)
        bd = ImageDraw.Draw(btn)
        lab = "Pide una reunión por WhatsApp"
        bf = F(700, 50)
        tw = bd.textlength(lab, font=bf)
        bd.text(((940 - tw) / 2, 44), lab, font=bf, fill=WHITE)
        els.append(El(shadow(btn, 30, 18, 50), (W - 940) // 2 - 60, 860 + q.height + 80 - 60, 0.6, "pop", 0.45))
        sub = text_block("Link en la bio · te lo enseñamos en 15 minutos", None, N(38), GREY)
        els.append(El(sub, (W - sub.width) // 2, 860 + q.height + 270, 0.8))
    bg = background(sc.get("fondo", "claro"))
    return bg, els


_BG = {}
FONDOS = {"claro": WHITE, "crema": (250, 245, 234), "menta": (230, 246, 238), "cielo": (232, 241, 250)}
def background(estilo):
    if estilo is True: estilo = "oscuro"
    if estilo in (False, None): estilo = "claro"
    if estilo not in _BG:
        _BG[estilo] = (grad((W, H), NAVY_D, NAVY_L, horizontal=False) if estilo == "oscuro"
                       else Image.new("RGB", (W, H), FONDOS.get(estilo, WHITE))).convert("RGBA")
    return _BG[estilo]


def render_frame(bg, els, t, t_out):
    frame = bg.copy()
    # salida: todo se desvanece y sube un poco en los últimos 0.25 s
    out_p = ease((t - t_out) / 0.25) if t_out is not None else 0.0
    for e in els:
        p = (t - e.t0) / e.dur
        if p <= 0:
            continue
        a = ease(p) * (1 - out_p)
        if a <= 0.01:
            continue
        img = e.img
        dx = dy = 0
        if e.kind == "up":
            dy = int((1 - ease(p)) * 70)
        elif e.kind == "flota":
            s_ = 0.8 + 0.2 * ease_back(min(1, p))
            if abs(s_ - 1) > 0.004:
                nw, nh = max(1, int(img.width * s_)), max(1, int(img.height * s_))
                img = img.resize((nw, nh), Image.BILINEAR)
                dx, dy = (e.img.width - nw) // 2, (e.img.height - nh) // 2
            dy += int(math.sin(t * 2.2) * 12)
        elif e.kind == "pop":
            s = 0.85 + 0.15 * ease_back(min(1, p))
            if abs(s - 1) > 0.004:
                nw, nh = max(1, int(img.width * s)), max(1, int(img.height * s))
                img = img.resize((nw, nh), Image.BILINEAR)
                dx, dy = (e.img.width - nw) // 2, (e.img.height - nh) // 2
        dy -= int(out_p * 40)
        frame.alpha_composite(with_alpha(img, a), (e.x + dx, e.y + dy))
    z = 1 + 0.025 * min(1.0, t / 4.0)  # zoom muy suave para dar movimiento
    if z > 1.002:
        zw, zh = int(W * z), int(H * z)
        frame = frame.resize((zw, zh), Image.BILINEAR).crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H))
    return frame


def musica(n_esc, seg_starts, out_wav):
    """Base suave libre de derechos + 'whoosh' en cada cambio de escena."""
    rnd = random.Random(sum(seg_starts) * 1000)
    roots = rnd.choice([(220.0, 277.18, 329.63), (196.0, 246.94, 293.66), (233.08, 293.66, 349.23)])
    pad = "+".join(f"0.05*sin(2*PI*{f}*t)" for f in roots)
    pluck = f"0.10*sin(2*PI*{roots[2]*2}*t)*exp(-7*mod(t,0.5))"
    kick = "0.35*sin(2*PI*58*t)*exp(-14*mod(t,1))"
    expr = f"({pad})*(0.6+0.4*sin(2*PI*0.2*t))+{pluck}+{kick}"
    whoosh = "+".join(f"0.18*(random(0)-0.5)*exp(-18*abs(t-{s:.2f}))" for s in seg_starts[1:])
    expr = f"({expr}+{whoosh})*0.55"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                    "-i", f"aevalsrc='{expr}':s=44100:d={DUR}",
                    "-af", f"lowpass=f=6000,afade=t=in:d=0.4,afade=t=out:st={DUR-1.2}:d=1.2",
                    out_wav], check=True)


def render_reel(reel, out_path):
    global DUR
    DUR = float(reel.get("duracion", 11.0))
    escenas = reel["escenas"]
    # el cierre dura 3.6 s, el resto se reparte
    cierre_d = 3.0 if escenas[-1]["tipo"] == "cierre" else 0
    resto = len(escenas) - (1 if cierre_d else 0)
    seg = (DUR - cierre_d) / resto
    starts, t = [], 0.0
    for i in range(len(escenas)):
        starts.append(t)
        t += cierre_d if (cierre_d and i == len(escenas) - 1) else seg
    built = [scene_elements(s) for s in escenas]
    wav = out_path + ".wav"
    musica(len(escenas), starts, wav)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav, "-map", "0:v", "-map", "1:a", "-t", str(DUR),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
    total = int(DUR * FPS)
    for fi in range(total):
        tt = fi / FPS
        si = max(i for i in range(len(starts)) if starts[i] <= tt)
        end = starts[si + 1] if si + 1 < len(starts) else None
        bg, els = built[si]
        frame = render_frame(bg, els, tt - starts[si], (end - starts[si] - 0.25) if end else None)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    ff.wait()
    os.remove(wav)


if __name__ == "__main__":
    src, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    data = json.load(open(src, encoding="utf-8"))
    for reel in data["reels"]:
        p = os.path.join(out_dir, reel["id"] + ".mp4")
        render_reel(reel, p)
        print("OK", p)
