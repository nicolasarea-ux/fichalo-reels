"""Publica en Instagram (API oficial con Instagram Login) los Reels de publicaciones.json cuya hora ya ha llegado.
Lo ejecuta GitHub Actions cada 15 minutos. Variables de entorno: IG_TOKEN, IG_USER_ID.
publicaciones.json = {"reels": [{"id": "...", "fecha": "YYYY-MM-DDTHH:MM" (Madrid), "estado": "pendiente|publicado|error", ...}]}
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

API = "https://graph.instagram.com/v21.0"
REPO_RAW = "https://raw.githubusercontent.com/nicolasarea-ux/fichalo-reels/main/videos/"
CAPTION = "Link en bio!!!\n\n#fichaje #fichajedigital #fichalo #empresa"
TZ = ZoneInfo("Europe/Madrid")
TOKEN = os.environ["IG_TOKEN"]
USER = os.environ["IG_USER_ID"]


def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(f"{API}/{path}?{data.decode()}")
    else:
        req = urllib.request.Request(f"{API}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:  # que el error de Instagram quede legible en publicaciones.json
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:250]}") from None


def publicar(reel):
    c = call("POST", f"{USER}/media", media_type="REELS", video_url=REPO_RAW + reel["id"] + ".mp4",
             caption=CAPTION, thumb_offset=1000, share_to_feed="true")
    cid = c["id"]
    for _ in range(40):  # hasta ~10 min procesando
        st = call("GET", cid, fields="status_code")["status_code"]
        if st == "FINISHED":
            break
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"contenedor {st}")
        time.sleep(15)
    else:
        raise RuntimeError("timeout procesando el vídeo")
    return call("POST", f"{USER}/media_publish", creation_id=cid)["id"]


def main():
    # comprueba el token en cada pasada: si caduca, el workflow falla y GitHub avisa por email
    yo = call("GET", "me", fields="user_id,username")
    print("Cuenta:", yo.get("username"), yo.get("user_id"))
    path = "publicaciones.json"
    data = json.load(open(path, encoding="utf-8"))
    ahora = datetime.now(TZ)
    cambios = 0
    for r in sorted(data["reels"], key=lambda x: x["fecha"]):
        if r.get("estado") != "pendiente":
            continue
        t = datetime.fromisoformat(r["fecha"]).replace(tzinfo=TZ)
        if t > ahora:
            continue
        if ahora - t > timedelta(hours=6):  # muy atrasado: se publica igualmente, pero se anota
            r["nota"] = "publicado con retraso"
        try:
            r["ig_media_id"] = publicar(r)
            r["estado"] = "publicado"
            r["publicado_en"] = datetime.now(TZ).strftime("%Y-%m-%dT%H:%M")
            print("OK", r["id"])
        except Exception as e:  # noqa
            r["intentos"] = r.get("intentos", 0) + 1
            r["ultimo_error"] = str(e)[:300]
            if r["intentos"] >= 3:
                r["estado"] = "error"
            print("ERROR", r["id"], e, file=sys.stderr)
        cambios += 1
    if cambios:
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
