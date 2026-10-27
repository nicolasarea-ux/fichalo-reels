# Rutina diaria de Reels de @fichalo.app

Objetivo: que haya **3 Reels publicados en Instagram cada día (09:00, 14:00, 20:30)** (horas calculadas por `huecos.py`), sin intervención humana.
Esta rutina se ejecuta cada mañana y deja completos **hoy (franjas restantes), mañana y pasado mañana** (colchón por si un día falla). **Siempre 3 por día, todos los días** (Nicks bajó de 12 a 3 el 27/10 porque las views eran muy bajas: calidad > cantidad).

Datos fijos
- **Desde el 2026-10-26 ya NO se usa Metricool** (se alcanzó el límite del plan). Metricool está agotado hasta noviembre: TODOS los Reels pendientes (incluidos 26–28/10) se movieron a `publicaciones.json` el 26/10 a las 11:35. NO programes nada en Metricool. Los publica GitHub Actions (`publicar.py`, cada 15 min) con la API oficial de Instagram.
- Repo público: `nicolasarea-ux/fichalo-reels`, rama `main`. Zona horaria: `Europe/Madrid`.
- URL pública de un vídeo: `https://raw.githubusercontent.com/nicolasarea-ux/fichalo-reels/main/videos/<id>.mp4`
- `publicaciones.json` = cola del publicador: `{"reels":[{"id","fecha":"YYYY-MM-DDTHH:MM","estado":"pendiente"}]}`. El publicador pone `publicado` o `error`.

## Pasos

1. Para HOY, MAÑANA y PASADO MAÑANA (fechas de Madrid), solo días **≥ 2026-10-29**:
   `python3 huecos.py <día>` → horas libres para llegar a 3 ese día (cuenta las fechas de cola.json).
2. Junta todas las franjas libres. Necesitas un vídeo por franja.
3. **Crea siempre vídeos nuevos con el formato nuevo** (no reutilices los de `estado: "reserva"`, son del formato viejo que no funcionó):
   - Escribe un `guiones/lote_<siguiente número>.json` con el mismo formato que `guiones/lote_015.json`.
   - Ids correlativos: `NN_<angulo>_<slug>` (NN = siguiente número tras el mayor de `cola.json`).
   - Reglas de contenido (ver abajo). Lee el campo `tema` de TODOS los reels de `cola.json` y **no repitas temas**.
   - `python3 generador.py guiones/lote_XXX.json videos/` (tarda ~20 s por vídeo: lánzalo en segundo plano y espera) y borra los `.wav` sueltos de `videos/`.
   - Revisa 1 fotograma de cada vídeo (ffmpeg a PNG + leerlo) para comprobar que el texto cabe y se lee.
   - Añade cada reel a `cola.json` con `id, tema, copy, hashtags, estado: "pendiente"`.
4. Por cada franja libre:
   - En `cola.json`: `estado: "programado"`, `fecha: <franja>`.
   - En `publicaciones.json`: añade `{"id": <id>, "fecha": <franja>, "estado": "pendiente"}`.
   (La descripción fija y la portada en el segundo 1 las pone `publicar.py`; no hay que tocarlas.)
5. `git pull --rebase` (el publicador también hace commits), `git add -A && git commit && git push`. Comprueba con `curl -s -o /dev/null -w '%{http_code}' <URL pública>` que cada vídeo da 200.
6. Revisa `publicaciones.json`: si hay reels con `estado: "error"` o con fecha pasada y aún `pendiente` (más de 1 h), anótalo en `registro.md` y avisa a Nicks (el publicador puede estar desactivado o el token caducado).
   Añade siempre una línea a `registro.md` con lo que se dejó programado. No inventes: si algo falla, anótalo.

## Formato nuevo (desde 27/10) — OBLIGATORIO
Datos de las primeras 60 publicaciones: casi todos 0–30 views; el mejor (140) fue el del pósit de vacaciones (objeto reconocible + situación que todos viven). Por eso:
- **11 s** (`"duracion": 11`), **3 escenas**: `objeto` → `movil` o `tabla` (la solución) → `cierre`. Ver ejemplo: `guiones/lote_072.json`.
- **1ª escena siempre `objeto`**: `pregunta` directa al DUEÑO (2.ª persona, ≤3 líneas, con su sector: "¿Tu bar todavía ficha así?") + un objeto reconocible:
  `postit` (texto manuscrito con \n), `papel` (lista: título + líneas manuscritas, p. ej. hoja de firmas) o `emoji` (uno grande y claro: 🧹 🍺 ✂️ 🦷 🔧 🏪 ⏰ 📋 📞 …). Opcional `subtitulo` corto.
  Es la portada (segundo 1): tiene que entenderse sin sonido en 1 vistazo.
- Alterna `fondo`: `crema`, `menta`, `cielo`, `claro`, `oscuro` (no dos seguidos iguales).
- **Nichos prioritarios (~2 de cada 3 vídeos)**: hostelería (bares/restaurantes con turnos), empresas de limpieza (varios edificios), clínicas (dental/fisio/veterinaria), comercio con varios locales, y gestorías/asesorías laborales (vídeos que una gestoría compartiría con sus clientes). El 3.º: ley/mito/tip general.
- Si un vídeo publicado supera claramente al resto en views (Nicks lo dirá o lo verás en registro), haz variantes de ese formato.

## Reglas de contenido (Fíchalo, app de control horario/fichaje para pymes en España)
- 15 s, 3–5 escenas, la última siempre `cierre`. Gancho fuerte en la primera escena (pregunta o dato).
- Son 3 vídeos al día: cada uno tiene que ser bueno. Varía mucho. Combina sector × problema × función (ej. "farmacia + guardias + quién está trabajando"); un tema ya usado puede volver solo con un sector o un enfoque claramente distinto.
- Rota ángulos: dolor, demo de función, sector (hostelería, comercio, taller, clínica, peluquería, gimnasio, limpieza, obra…), ley, tip, mito/realidad.
- Funciones que SÍ existen (solo usa estas): fichar desde el móvil, con tarjeta o con código en tablet; avisos si alguien olvida fichar;
  ver quién está trabajando; horas por persona y horas extra; informes en PDF y Excel; vacaciones (pedir y aprobar);
  acceso de solo lectura para Inspección; varios centros/turnos.
- **No inventes precios, cifras de clientes, testimonios ni funciones nuevas.** Datos legales solo si son ciertos
  (registro de jornada obligatorio desde 2019, conservar 4 años, a disposición de trabajadores e Inspección).
- Textos cortos (máx. ~4 líneas de 2–4 palabras por escena), español de España, tuteo.
- **Descripción fija para TODOS los Reels (orden de Nicks, no cambiarla):** `text` = "Link en bio!!!\n\n#fichaje #fichajedigital #fichalo #empresa". En `cola.json` guarda copy="Link en bio!!!" y hashtags="#fichaje #fichajedigital #fichalo #empresa".
