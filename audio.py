"""Audio de los Reels: voz en off (Piper, voz davefx CC0), música sintetizada y efectos de sonido.
Todo se genera aquí (sin descargar nada) → libre de derechos.
"""
import os, wave, random
import numpy as np

SR = 44100
BASE = os.path.dirname(os.path.abspath(__file__))
VOZ = os.path.join(BASE, "assets", "voz", "es_ES-davefx-medium.onnx")
_voice = None


class Mezcla:
    def __init__(self, dur):
        self.dur = dur
        self.buf = np.zeros(int(dur * SR) + SR, dtype=np.float32)
        self.voz = np.zeros_like(self.buf)  # pista aparte para hacer "ducking" de la música

    def add(self, x, t, g=1.0, voz=False):
        i = int(max(0, t) * SR)
        x = x[: max(0, len(self.buf) - i)]
        (self.voz if voz else self.buf)[i:i + len(x)] += x * g

    def musica(self, m, g=0.35):
        m = m[: len(self.buf)]
        env = np.abs(self.voz)
        k = int(0.15 * SR)
        env = np.convolve(env, np.ones(k) / k, mode="same")
        duck = 1 - 0.65 * np.clip(env * 12, 0, 1)  # baja la música cuando habla la voz
        self.buf[: len(m)] += m * g * duck[: len(m)]

    def guardar(self, path):
        x = self.buf + self.voz
        n = int(self.dur * SR)
        x = x[:n]
        fo = int(0.6 * SR)
        x[-fo:] *= np.linspace(1, 0, fo)
        pk = np.max(np.abs(x)) or 1
        x = x / pk * 0.95  # normalización limpia; el volumen final lo fija loudnorm al montar
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((x * 32767).astype(np.int16).tobytes())


# ---------- voz ----------
def voz(texto, velocidad=0.92):
    """Devuelve (audio float32 a 44.1 kHz, duración en s)."""
    global _voice
    from piper import PiperVoice, SynthesisConfig
    if _voice is None:
        _voice = PiperVoice.load(VOZ)
    chunks = []
    for ch in _voice.synthesize(texto, syn_config=SynthesisConfig(length_scale=velocidad)):
        chunks.append(ch.audio_float_array)
    x = np.concatenate(chunks).astype(np.float64)
    sr = _voice.config.sample_rate
    from scipy import signal
    from math import gcd
    g = gcd(SR, sr)
    x = signal.resample_poly(x, SR // g, sr // g)  # remuestreo limpio (antes: interpolación lineal → sonido sucio)
    x = _eq_voz(x)
    # recorta silencios del principio/final
    nz = np.where(np.abs(x) > 0.01)[0]
    if len(nz):
        x = x[max(0, nz[0] - 800): nz[-1] + 2000]
    x = x / (np.max(np.abs(x)) or 1) * 0.9   # sin saturación (antes tanh → distorsión)
    return x.astype(np.float32), len(x) / SR


def _peaking(f0, gain_db, q):
    A_ = 10 ** (gain_db / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A_, -2 * np.cos(w), 1 - al * A_]; a = [1 + al / A_, -2 * np.cos(w), 1 - al / A_]
    return np.array(b) / a[0], np.array(a) / a[0]

def _eq_voz(x):
    """Voz más nítida: quita graves que embarran, realza presencia e inteligibilidad."""
    from scipy import signal
    b, a = signal.butter(2, 85 / (SR / 2), "highpass"); x = signal.lfilter(b, a, x)
    for f0, g, q in ((250, -2.5, 1.0), (3200, 4.0, 1.0), (6500, 2.5, 1.2)):
        b, a = _peaking(f0, g, q); x = signal.lfilter(b, a, x)
    # compresión suave por envolvente (iguala volumen sin distorsionar)
    env = np.sqrt(np.convolve(x * x, np.ones(441) / 441, mode="same")) + 1e-6
    ref = np.percentile(env, 90)
    gain = np.minimum(1.0, (env / ref) ** -0.35)
    return x * gain


# ---------- efectos ----------
def _t(d):
    return np.arange(int(d * SR)) / SR

def _env(t, a=0.004, r=8.0):
    return np.minimum(1, t / a) * np.exp(-r * t)

def pop():
    t = _t(0.12)
    f = 900 * np.exp(-25 * t) + 300
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(t, 0.002, 30)).astype(np.float32) * 0.7

def whoosh(d=0.35):
    t = _t(d)
    n = np.random.default_rng(1).standard_normal(len(t))
    # ruido filtrado que sube y baja
    k = np.exp(-((t - d * 0.6) / (d * 0.3)) ** 2)
    y = np.convolve(n, np.ones(6) / 6, mode="same") * k
    return y.astype(np.float32) * 0.35

def ding(f=1318.5):
    t = _t(0.9)
    y = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * _env(t, 0.002, 5)
    return y.astype(np.float32) * 0.45

def exito():
    return np.concatenate([ding(1046.5)[:int(0.11 * SR)], ding(1318.5)[:int(0.11 * SR)], ding(1568)]) * 0.9

def error():
    t = _t(0.45)
    y = np.sign(np.sin(2 * np.pi * 140 * t)) * 0.5 + np.sin(2 * np.pi * 147 * t) * 0.5
    return (y * _env(t, 0.005, 3)).astype(np.float32) * 0.35

def tic():
    t = _t(0.05)
    return (np.sin(2 * np.pi * 2200 * t) * _env(t, 0.001, 90)).astype(np.float32) * 0.5

def tap():
    t = _t(0.06)
    n = np.random.default_rng(2).standard_normal(len(t))
    return (n * _env(t, 0.001, 120) * 0.4 + np.sin(2 * np.pi * 600 * t) * _env(t, 0.001, 80) * 0.4).astype(np.float32)

def mensaje():
    return np.concatenate([ding(987.8)[:int(0.08 * SR)], ding(1318.5)[:int(0.5 * SR)]]) * 0.6

def teclear(d=0.8):
    out = np.zeros(int(d * SR), dtype=np.float32)
    rng = random.Random(3)
    t = 0.0
    while t < d - 0.06:
        i = int(t * SR)
        x = tap() * rng.uniform(0.3, 0.6)
        out[i:i + len(x)] += x[: len(out) - i]
        t += rng.uniform(0.06, 0.13)
    return out

def papeles():
    t = _t(0.5)
    n = np.random.default_rng(4).standard_normal(len(t))
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 18 * t)
    return (np.diff(n, prepend=0) * am * _env(t, 0.02, 5)).astype(np.float32) * 0.25

def sello():
    t = _t(0.25)
    return (np.sin(2 * np.pi * 80 * t) * _env(t, 0.001, 20) + np.random.default_rng(5).standard_normal(len(t)) * _env(t, 0.001, 60) * 0.3).astype(np.float32) * 0.8

def campana():
    return ding(880) * 0.8 + np.pad(ding(1108.7), (int(0.12 * SR), 0))[: int(0.9 * SR)] * 0.6

SFX = {"pop": pop, "whoosh": whoosh, "ding": ding, "exito": exito, "error": error, "tic": tic, "tap": tap,
       "mensaje": mensaje, "teclear": teclear, "papeles": papeles, "sello": sello, "campana": campana}


# ---------- música ----------
NOTAS = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.0, "A": 440.0, "B": 493.88}
PROGS = [["A", "F", "C", "G"], ["C", "G", "A", "F"], ["F", "G", "E", "A"], ["D", "G", "C", "A"]]

def _acorde(raiz, menor):
    f = NOTAS[raiz] / 2
    return [f, f * (1.189 if menor else 1.26), f * 1.498]

def musica(dur, estilo="lofi", seed=0):
    """estilo: lofi (relajada), animada (ritmo), tension (quiz)."""
    rng = random.Random(seed)
    bpm = {"lofi": 88, "animada": 116, "tension": 100}[estilo]
    beat = 60 / bpm
    n = int(dur * SR) + SR
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    prog = rng.choice(PROGS)
    compas = beat * 4
    for k in range(int(dur / compas) + 2):
        raiz = prog[k % 4]
        menor = raiz in ("A", "E", "D") and estilo != "animada"
        i0 = int(k * compas * SR)
        if i0 >= n:
            break
        seg = np.arange(int(compas * SR)) / SR
        pad = sum(np.sin(2 * np.pi * f * seg) + 0.3 * np.sin(2 * np.pi * 2 * f * seg) for f in _acorde(raiz, menor))
        pad *= np.minimum(1, seg / 0.08) * (0.8 + 0.2 * np.cos(2 * np.pi * seg / compas))
        bajo = np.sin(2 * np.pi * NOTAS[raiz] / 4 * seg) * np.exp(-1.5 * (seg % beat * 2))
        out[i0:i0 + len(seg)] += (pad * (0.10 if estilo == "lofi" else 0.07) + bajo * 0.35)[: n - i0]
        # arpegio
        if estilo != "lofi" or rng.random() < 0.6:
            for j in range(8):
                f = _acorde(raiz, menor)[j % 3] * (4 if j % 2 else 2)
                a = int(i0 + j * beat / 2 * SR)
                if a >= n:
                    break
                s = np.arange(int(beat / 2 * SR)) / SR
                out[a:a + len(s)] += (np.sin(2 * np.pi * f * s) * np.exp(-9 * s) * 0.07)[: max(0, n - a)]
    # batería
    def golpe(x, tt, g):
        i = int(tt * SR)
        if i < n:
            out[i:i + len(x)] += x[: n - i] * g
    tk = _t(0.3)
    kick = np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-30 * tk)) / SR) * np.exp(-9 * tk)
    sn = np.random.default_rng(7).standard_normal(len(_t(0.18))) * np.exp(-22 * _t(0.18))
    hh = np.diff(np.random.default_rng(8).standard_normal(len(_t(0.05))), prepend=0) * np.exp(-70 * _t(0.05))
    b = 0
    while b * beat < dur + 1:
        tt = b * beat
        if b % 4 in (0, 2) or (estilo == "animada"):
            golpe(kick, tt, 0.55)
        if b % 4 in (1, 3):
            golpe(sn, tt, 0.18 if estilo == "lofi" else 0.25)
        golpe(hh, tt + beat / 2, 0.12)
        if estilo != "lofi":
            golpe(hh, tt, 0.08)
        b += 1
    if estilo == "lofi":  # "vinilo"
        pass  # sin ruido de vinilo: el audio queda más limpio
    # filtro paso bajo sencillo para que suene más suave
    k = 4 if estilo == "lofi" else 2
    out = np.convolve(out, np.ones(k) / k, mode="same")
    out[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    return (out / (np.max(np.abs(out)) or 1)).astype(np.float32)
