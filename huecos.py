"""Calcula a qué horas hay que programar Reels nuevos un día para llegar a 20.
Uso: python3 huecos.py YYYY-MM-DD programados.json
programados.json = lista de "YYYY-MM-DDTHH:MM" (hora de Madrid) que devuelve getScheduledPosts para ese día.
Además cuenta los reels de cola.json con esa fecha (incluye los ya publicados, que Metricool ya no devuelve).
Imprime en JSON las horas nuevas a programar ("YYYY-MM-DDTHH:MM"), repartidas, sin pisar las existentes.
"""
import json, os, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

OBJETIVO = 20
TZ = ZoneInfo("Europe/Madrid")
# rejilla cada 15 min de 08:30 a 23:00
REJILLA = [f"{h:02d}:{m:02d}" for h in range(8, 24) for m in (0, 15, 30, 45) if (8, 30) <= (h, m) <= (23, 0)]

dia = sys.argv[1]
base = os.path.dirname(os.path.abspath(__file__))
existentes = set(x[:16] for x in json.load(open(sys.argv[2])))
for r in json.load(open(os.path.join(base, "cola.json")))["reels"]:
    if r.get("fecha", "").startswith(dia):
        existentes.add(r["fecha"][:16])
ex = [datetime.fromisoformat(x).replace(tzinfo=TZ) for x in existentes]
faltan = OBJETIVO - len(ex)
ahora = datetime.now(TZ)
cands = []
for f in REJILLA:
    t = datetime.fromisoformat(f"{dia}T{f}").replace(tzinfo=TZ)
    if t < ahora + timedelta(minutes=20):
        continue
    cands.append(t)
elegidas = []
for _ in range(max(0, faltan)):
    todas = ex + elegidas
    libres = [c for c in cands if c not in elegidas]
    if not libres:
        break
    # la franja más alejada de cualquier post ya existente o elegido
    mejor = max(libres, key=lambda c: min((abs((c - p).total_seconds()) for p in todas), default=1e9))
    elegidas.append(mejor)
print(json.dumps(sorted(t.strftime("%Y-%m-%dT%H:%M") for t in elegidas)))
