"""Calcula las franjas libres de un día.
Uso: python3 huecos.py YYYY-MM-DD programados.json
programados.json = lista de strings "YYYY-MM-DDTHH:MM" (hora de Madrid) ya programados en Metricool.
Imprime en JSON la lista de franjas libres ("YYYY-MM-DDTHH:MM"), descartando las que ya han pasado
o empiezan en menos de 45 min. Una franja está ocupada si hay un post a menos de 40 min.
"""
import json, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FRANJAS = ["09:00", "10:30", "12:00", "13:30", "15:00", "16:30", "18:00", "19:30", "21:00", "22:15"]
TZ = ZoneInfo("Europe/Madrid")

dia = sys.argv[1]
prog = [datetime.fromisoformat(x[:16]).replace(tzinfo=TZ) for x in json.load(open(sys.argv[2]))]
ahora = datetime.now(TZ)
libres = []
for f in FRANJAS:
    t = datetime.fromisoformat(f"{dia}T{f}").replace(tzinfo=TZ)
    if t < ahora + timedelta(minutes=45):
        continue
    if any(abs((t - p).total_seconds()) < 40 * 60 for p in prog):
        continue
    libres.append(t.strftime("%Y-%m-%dT%H:%M"))
print(json.dumps(libres))
