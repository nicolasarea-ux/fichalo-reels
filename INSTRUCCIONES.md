# Rutina diaria de Reels de @fichalo.app

Objetivo: que haya **10 Reels programados en Instagram cada día** (franjas en `huecos.py`), sin intervención humana.
Esta rutina se ejecuta cada mañana y deja completo **el día de hoy (franjas restantes) y el día de mañana**.

Datos fijos
- Metricool blogId / brandId: `7603867` · timezone `Europe/Madrid` · red: instagram, tipo REEL.
- Repo público: `nicolasarea-ux/fichalo-reels`, rama `main`.
- URL pública de un vídeo: `https://raw.githubusercontent.com/nicolasarea-ux/fichalo-reels/main/videos/<id>.mp4`

## Pasos

1. Para HOY y MAÑANA (fechas de Madrid):
   - `getScheduledPosts` (brandId 7603867, timezone Europe/Madrid, rango de ese día 00:00–23:59).
   - Guarda las horas programadas (`publicationDate.dateTime`, formato `YYYY-MM-DDTHH:MM`) en un JSON y ejecuta
     `python3 huecos.py <día> <json>` → lista de franjas libres.
2. Junta todas las franjas libres. Necesitas un vídeo por franja.
3. Usa primero los reels de `cola.json` con `estado: "pendiente"` (en orden). Si no llegan, **crea los que falten**:
   - Escribe un `guiones/lote_<siguiente número>.json` con el mismo formato que `guiones/lote_015.json`.
   - Ids correlativos: `NN_<angulo>_<slug>` (NN = siguiente número tras el mayor de `cola.json`).
   - Reglas de contenido (ver abajo). Lee el campo `tema` de TODOS los reels de `cola.json` y **no repitas temas**.
   - `python3 generador.py guiones/lote_XXX.json videos/`
   - Revisa 1 fotograma de cada vídeo (ffmpeg a PNG + leerlo) para comprobar que el texto cabe y se lee.
   - Añade cada reel a `cola.json` con `id, tema, copy, hashtags, estado: "pendiente"`.
4. `git add -A && git commit && git push`. Comprueba con `curl -sI <URL pública>` que cada vídeo da 200 (espera y reintenta si no).
5. Por cada franja libre, `createScheduledPost`:
   - date `<franja>:00` con su offset de Madrid, `publicationDate {dateTime, timezone:"Europe/Madrid"}`
   - `media: [URL pública]`, `providers: [{"network":"instagram"}]`, `instagramData: {"type":"REEL","showReelOnFeed":true}`
   - `text`: copy + "\n\n" + hashtags · `autoPublish: true`, `draft: false`
   - Marca el reel en `cola.json` como `estado: "programado"`, `fecha: <franja>`.
6. Commit y push de `cola.json`. Si algo falla, no inventes: déjalo anotado en `registro.md` (fecha, qué falló).
   Añade siempre una línea a `registro.md` con lo que se programó.

## Reglas de contenido (Fíchalo, app de control horario/fichaje para pymes en España)
- 15 s, 3–5 escenas, la última siempre `cierre`. Gancho fuerte en la primera escena (pregunta o dato).
- Rota ángulos: dolor, demo de función, sector (hostelería, comercio, taller, clínica, peluquería, gimnasio, limpieza, obra…), ley, tip, mito/realidad.
- Funciones que SÍ existen (solo usa estas): fichar desde el móvil, con tarjeta o con código en tablet; avisos si alguien olvida fichar;
  ver quién está trabajando; horas por persona y horas extra; informes en PDF y Excel; vacaciones (pedir y aprobar);
  acceso de solo lectura para Inspección; varios centros/turnos.
- **No inventes precios, cifras de clientes, testimonios ni funciones nuevas.** Datos legales solo si son ciertos
  (registro de jornada obligatorio desde 2019, conservar 4 años, a disposición de trabajadores e Inspección).
- Textos cortos (máx. ~4 líneas de 2–4 palabras por escena), español de España, tuteo.
- **Descripción fija para TODOS los Reels (orden de Nicks, no cambiarla):** `text` = "Link en bio!!!\n\n#fichaje #fichajedigital #fichalo #empresa". En `cola.json` guarda copy="Link en bio!!!" y hashtags="#fichaje #fichajedigital #fichalo #empresa".
