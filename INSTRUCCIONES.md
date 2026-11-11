# Rutina diaria de Reels de @fichalo.app

Objetivo: **5 Reels/día desde el 4/11 (09:40, 12:40, 14:40, 17:40, 20:40), uno de cada formato** (horas calculadas por `huecos.py`), sin intervención humana. Ver la sección **PRUEBA DE FORMATOS** (manda sobre lo demás).
Esta rutina se ejecuta cada mañana y deja completos **hoy (franjas restantes), mañana y pasado mañana** (colchón por si un día falla). Lo calcula `huecos.py`. (Historial: 12/día hundió el alcance y Meta bloqueó la API el 27/10; objetivo ahora = máximas views por vídeo.)

Datos fijos
- **Desde el 2026-10-26 ya NO se usa Metricool** (se alcanzó el límite del plan). Metricool está agotado hasta noviembre: TODOS los Reels pendientes (incluidos 26–28/10) se movieron a `publicaciones.json` el 26/10 a las 11:35. NO programes nada en Metricool. Los publica GitHub Actions (`publicar.py`, cada 15 min) con la API oficial de Instagram.
- Repo público: `nicolasarea-ux/fichalo-reels`, rama `main`. Zona horaria: `Europe/Madrid`.
- URL pública de un vídeo: `https://raw.githubusercontent.com/nicolasarea-ux/fichalo-reels/main/videos/<id>.mp4`
- `publicaciones.json` = cola del publicador: `{"reels":[{"id","fecha":"YYYY-MM-DDTHH:MM","estado":"pendiente"}]}`. El publicador pone `publicado` o `error`.

## PRUEBA DE FORMATOS (4–10 nov 2026) — pedida por Nicks el 3/11
Nicks quiere multiplicar las views: 5 Reels/día de 5 formatos distintos durante una semana para ver cuál funciona.
Los 35 de la semana (4–10/11) YA están hechos y programados (`guiones/lote_082.json` + 79/75/81). Cada día, un formato en cada franja, rotando (que la hora no decida).
Formatos (campo `formato` en el guion y en `publicaciones.json`; `generador.py` los renderiza con `formatos.py` + `audio.py`):
- `postit`: el de siempre (objeto → móvil/tabla → cierre, 8,5 s) + música animada + efectos. Mismo esquema de escenas que antes.
- `monigotes`: monigotes animados + voz en off + subtítulos palabra a palabra. `titular` + `escenas` [{escena: caos|llega|jefe_movil|olvido|inspeccion|feliz|calcula, voz, …}]. Ejemplos: ids 82–88.
- `chat`: conversación de mensajería (sin emojis en los textos), `titular`, `contacto`, `mensajes` [{de: el|yo, texto | foto:[líneas]}], `giro` (móvil con la solución). Ejemplos: 89–95.
- `quiz`: "¿Legal o multa?", 2 `preguntas` {situacion, respuesta LEGAL|MULTA, porque, acento_porque}. **Solo datos legales ciertos** (ver la lista en `guiones/crear_lote_prueba.py`). Ejemplos: 96–102.
- `voz`: voz en off con subtítulos grandes + imagen por frase (`postit`, `papel`, `emoji`, `numero` o `movil`). Ejemplos: 103–109.
La voz es Piper `es_ES-davefx-medium` (licencia CC0, está en `assets/voz/`; `pip install --break-system-packages piper-tts` si falta). En `voz` escribe los números y horas en letra ("seis y diez") para que se lean bien.
Medición (cada día):
1. `publicar.py` guarda `permalink` de cada Reel publicado. Con Metricool (IGRE06 url, IGRE23 views, IGRE24 tiempo medio, IGRE28 % que pasa de 3 s) cruza por el código del enlace y apunta en `resultados_formatos.md` una tabla por formato: nº publicados, views medias y medianas, tiempo medio, % >3 s (solo reels de la prueba, con ≥24 h desde que se publicaron).
2. Añade 1 línea a `registro.md` con el ranking del día.
3. **El 11/11** escribe en `registro.md` una línea que empiece por `RESULTADO PRUEBA:` con el ranking final y termina tu respuesta con ese resumen para Nicks (le llega como notificación).
Dato de Nicks (5/11): el primer reel de **monigotes** (82, bar día 30, publicado 4/11) ya va por **~200 views** → el mejor automático hasta ahora. A Nicks le gusta mucho la voz (davefx): mantenla. Desde el 5/11 el audio va más limpio (sin saturación, remuestreo bueno, EQ de presencia, loudnorm -14 LUFS).
Después de la prueba (franjas libres desde el 11/11): sigue 5/día repartidos entre los 3 mejores formatos por views medias (2 + 2 + 1), hasta que Nicks diga otra cosa.
**Resultado final (11/11, n=6):** monigotes 143 > voz 113 > chat 103 > quiz 84 > postit 41 → reparto 2 monigotes + 2 voz + 1 chat (revísalo si el ranking de views medias cambia).

## Pasos

1. Para HOY, MAÑANA y PASADO MAÑANA (fechas de Madrid), solo días **≥ 2026-10-29**:
   `python3 huecos.py <día>` → horas libres para ese día (cuenta las fechas de cola.json).
2. Junta todas las franjas libres. Necesitas un vídeo por franja.
3. **Crea siempre vídeos nuevos** (no reutilices los de `estado: "reserva"`, son del formato viejo que no funcionó), en el formato que toque según la PRUEBA DE FORMATOS:
   - Escribe un `guiones/lote_<siguiente número>.json` con los ejemplos de `guiones/lote_082.json` (cada reel con `formato` y `copy`).
   - Ids correlativos: `NN_<angulo>_<slug>` (NN = siguiente número tras el mayor de `cola.json`).
   - Reglas de contenido (ver abajo). Lee el campo `tema` de TODOS los reels de `cola.json` y **no repitas temas**.
   - `python3 generador.py guiones/lote_XXX.json videos/` (20–60 s por vídeo: lánzalo en segundo plano y espera) y borra los `.wav` sueltos de `videos/`.
   - Revisa 1 fotograma de cada vídeo (ffmpeg a PNG + leerlo) para comprobar que el texto cabe y se lee.
   - Añade cada reel a `cola.json` con `id, tema, copy, hashtags, estado: "pendiente"`.
4. Por cada franja libre:
   - En `cola.json`: `estado: "programado"`, `fecha: <franja>`.
   - En `publicaciones.json`: añade `{"id": <id>, "fecha": <franja>, "estado": "pendiente", "formato": <formato>, "copy": <descripción variada, ver reglas>}`.
   - Sube también `videos/<id>.jpg` (portada de marca que crea generador.py); `publicar.py` la usa como portada.
5. `git pull --rebase` (el publicador también hace commits), `git add -A && git commit && git push`. Comprueba con `curl -s -o /dev/null -w '%{http_code}' <URL pública>` que cada vídeo da 200.
6. Revisa `publicaciones.json`: si hay reels con `estado: "error"` o con fecha pasada y aún `pendiente` (más de 1 h), anótalo en `registro.md` y avisa a Nicks (el publicador puede estar desactivado o el token caducado).
   Añade siempre una línea a `registro.md` con lo que se dejó programado. No inventes: si algo falla, anótalo.

## Formato `postit` (desde 27/10; en la prueba de formatos es uno de los 5)
Datos de las primeras 60 publicaciones: casi todos 0–30 views; el mejor (140) fue el del pósit de vacaciones (objeto reconocible + situación que todos viven). Por eso:
- **8,5 s** (`"duracion": 8.5`; más corto = más gente lo ve entero y se repite), **3 escenas**: `objeto` → `movil` o `tabla` (la solución) → `cierre`. Ver ejemplo: `guiones/lote_072.json`.
- **1ª escena siempre `objeto`**: `pregunta` directa al DUEÑO (2.ª persona, ≤3 líneas, con su sector: "¿Tu bar todavía ficha así?") + un objeto reconocible:
  `postit` (texto manuscrito con \n), `papel` (lista: título + líneas manuscritas, p. ej. hoja de firmas) o `emoji` (uno grande y claro: 🧹 🍺 ✂️ 🦷 🔧 🏪 ⏰ 📋 📞 …). Opcional `subtitulo` corto.
  Es la portada (segundo 1): tiene que entenderse sin sonido en 1 vistazo.
- **Datos 28/10 (Metricool)**: tiempo medio de visualización 1–2 s y <20 % pasa de 3 s → el gancho falla en el primer segundo. Los automáticos que mejor fueron (vacaciones-pósit 140, \"No quiero usar mi móvil para fichar\" 128, bar 1:30 72, \"tu trabajador te pide sus horas\" 67) abren con **fondo oscuro + una frase/situación real entre comillas o una pregunta muy concreta**. Prioriza `fondo: "oscuro"` en la 1.ª escena (2 de cada 3) y frases en boca del dueño o del trabajador. Los de apertura blanca y genérica (\"Farmacia.\", \"MITO:\") fueron los peores.
- **Datos 3/11 (captura de Nicks)** — formato nuevo: 76 gestoría "¿Tus clientes te mandan las horas así?" + pósit = 84 (el mejor); 77 "Es viernes. ¿Sabes cuántas horas ha hecho tu equipo?" + portapapeles = 62; 73 limpieza 6:10 + escoba = 25; 74 clínica pósit = 16; 80 "Tienes 3 tiendas" + emoji 24 = 10. Conclusión:
  - Tema ganador = **las HORAS** (cuántas ha hecho cada uno, cómo llegan, cómo se calculan) contado como un caos reconocible. Úsalo en ~2 de cada 3 vídeos, cambiando sector y situación.
  - **Objeto: prefiere `postit` o `papel` con datos manuscritos desordenados** ("ver foto 1, 2 y la 3 borrosa", "Laura 6h?") antes que `emoji`: los de emoji suelto rinden menos.
  - **Gestorías funcionan**: vídeos que una gestoría reenviaría a sus clientes (horas que llegan por WhatsApp/foto/papel a fin de mes).
  - Ganchos de calendario: viernes, fin de mes/nóminas, lunes. Programa el de "viernes" en viernes y el de "nóminas" a final de mes.
- Las escenas 2 y 3 pueden alternar `fondo`: `crema`, `menta`, `cielo`, `claro`.
- **Nichos prioritarios (~2 de cada 3 vídeos)**: hostelería (bares/restaurantes con turnos), empresas de limpieza (varios edificios), clínicas (dental/fisio/veterinaria), comercio con varios locales, y gestorías/asesorías laborales (vídeos que una gestoría compartiría con sus clientes). El 3.º: ley/mito/tip general.
- Si un vídeo publicado supera claramente al resto en views (Nicks lo dirá o lo verás en registro), haz variantes de ese formato.

## Reglas de contenido (Fíchalo, app de control horario/fichaje para pymes en España)
- Duración y escenas: ver "Formato nuevo" (8,5 s, 3 escenas, la última siempre `cierre`).
- Son 1–2 vídeos al día: cada uno tiene que ser bueno. Varía mucho. Combina sector × problema × función (ej. "farmacia + guardias + quién está trabajando"); un tema ya usado puede volver solo con un sector o un enfoque claramente distinto.
- Rota ángulos: dolor, demo de función, sector (hostelería, comercio, taller, clínica, peluquería, gimnasio, limpieza, obra…), ley, tip, mito/realidad.
- Funciones que SÍ existen (solo usa estas): fichar desde el móvil, con tarjeta o con código en tablet; avisos si alguien olvida fichar;
  ver quién está trabajando; horas por persona y horas extra; informes en PDF y Excel; vacaciones (pedir y aprobar);
  acceso de solo lectura para Inspección; varios centros/turnos.
- **No inventes precios, cifras de clientes, testimonios ni funciones nuevas.** Datos legales solo si son ciertos
  (registro de jornada obligatorio desde 2019, conservar 4 años, a disposición de trabajadores e Inspección).
- Textos cortos (máx. ~4 líneas de 2–4 palabras por escena), español de España, tuteo.
- **Descripción VARIADA en cada Reel (Nicks, 28/10)** — va en `publicaciones.json` → campo `copy` de cada reel (si falta, se usa "Link en bio!!!" + hashtags). Estructura:
  1) gancho de 1 línea distinto al texto del vídeo, con 1 emoji; 2) 1 línea de valor (qué resuelve Fíchalo);
  3) una pregunta o llamada que provoque comentarios / guardados / etiquetas ("¿Cómo lo lleváis? 👇", "Guárdalo para el viernes 📌", "Etiqueta a tu gestor/a");
  4) `Link en bio!!!`; 5) línea en blanco + SIEMPRE `#fichaje #fichajedigital #fichalo #empresa` + 1–2 hashtags del nicho. No repitas la misma pregunta dos días seguidos. Ejemplos en publicaciones.json (73–80).
- **Portada de marca obligatoria** (v2 desde 3/11, la pidió Nicks): `generador.py` crea `videos/<id>.jpg` con `formatos.portada_v2`: etiqueta del sector (campo `nicho`: hosteleria, limpieza, clinica, gestoria, comercio, taller, peluqueria, ley), titular enorme y una sola imagen, todo dentro del recorte 3:4 de la cuadrícula. Pon siempre `formato` y `nicho` en cada reel; opcional `portada` (texto corto para la portada) y `acento_portada`. Súbela junto al .mp4; `publicar.py` la usa como portada. Para rehacer solo portadas: `python3 generador.py guiones/lote_X.json videos/ --solo-portada`.

## Reels `saltado`
Si el publicador estuvo parado, marca `saltado` los que llevan >3 h de retraso. Reutilízalos en las siguientes franjas libres (son vídeos buenos) antes de crear nuevos, y anótalo en registro.md.
