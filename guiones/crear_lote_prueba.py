"""Crea guiones/lote_082.json: semana de prueba de formatos (4–10 nov 2026), 5 formatos × 7 días.
Se ejecuta una vez; el JSON resultante es el que usa generador.py."""
import json, os

CTAS = ["¿Te suena? 👇", "Guárdalo para fin de mes 📌", "Etiqueta a quien necesita ver esto 👇", "¿Cómo lo hacéis vosotros? 👇",
        "Mándaselo a tu socio/a 📲", "¿Te ha pasado? Cuéntamelo 👇", "Comparte con tu gestor/a 📲"]
HT = {"hosteleria": "#hosteleria #bares", "limpieza": "#limpieza #empresasdelimpieza", "clinica": "#clinicadental #clinicas",
      "gestoria": "#gestoria #asesorialaboral", "comercio": "#comercio #tiendas", "taller": "#taller #talleres",
      "peluqueria": "#peluqueria #salondebelleza", "ley": "#registrodejornada #pymes"}
_n = [0]

def copy(gancho, valor, nicho):
    c = CTAS[_n[0] % len(CTAS)]; _n[0] += 1
    return f"{gancho}\n{valor}\n\n{c}\nLink en bio!!!\n\n#fichaje #fichajedigital #fichalo #empresa {HT[nicho]}"

R = []
def add(id_, formato, nicho, tema, cp, **kw):
    R.append(dict(id=id_, formato=formato, nicho=nicho, tema=tema, copy=cp, **kw))

OK = "1"
# ---------------------------------------------------------------- MONIGOTES (7)
add("82_monigotes_bar-dia-30", "monigotes", "hosteleria", "monigotes: dueño de bar sumando horas el día 30",
    copy("Día 30 en el bar: sumar las horas de 6 camareros a mano 🍺", "Con Fíchalo fichan desde el móvil y las horas salen ya sumadas.", "hosteleria"),
    titular="Día 30 en un bar con 6 camareros", acento="Día 30", escenas=[
    {"escena": "caos", "voz": "Es día treinta. Toca sumar las horas de seis camareros. Otra vez.", "postit": "Iker: 38?\nAne: ver hoja\nJon: ¿extras?"},
    {"escena": "llega", "voz": "Con Fíchalo, cada camarero ficha desde el móvil al llegar.", "lugar": "Bar Txoko", "hora": "17:58", "acc": ["delantal"]},
    {"escena": "jefe_movil", "voz": "Y tú ves las horas de todos, ya sumadas.", "cab": "Horas de octubre", "sub": "Calculadas solas",
     "filas": [["Iker", "162 h", OK], ["Ane", "158 h", OK], ["Jon", "171 h · 11 extra", OK]]}])
add("83_monigotes_limpieza-610", "monigotes", "limpieza", "monigotes: encargada de limpieza llamando a 4 edificios a las 6",
    copy("6:10 de la mañana y cuatro edificios por abrir 🧹", "Con Fíchalo sabes quién ha empezado y dónde sin hacer ni una llamada.", "limpieza"),
    titular="6:10. ¿Ha empezado ya tu equipo?", acento="6:10", escenas=[
    {"escena": "caos", "voz": "Seis y diez de la mañana. Cuatro edificios. Y tú llamando uno por uno para saber si han llegado.", "postit": "Edif. 1 ok\nEdif. 3 ¿?\nRosa no coge"},
    {"escena": "llega", "voz": "Con Fíchalo, cada limpiadora ficha al llegar al edificio.", "lugar": "Edificio 3", "hora": "06:02", "acc": ["escoba"]},
    {"escena": "jefe_movil", "voz": "Y tú lo ves en el móvil, sin llamar a nadie.", "cab": "Quién está trabajando",
     "filas": [["Rosa · Edif. 1", "Fichó 05:58", OK], ["Mari · Edif. 3", "Fichó 06:02", OK], ["Lucía · Edif. 4", "Fichó 06:05", OK]]}])
add("84_monigotes_clinica-inspeccion", "monigotes", "clinica", "monigotes: llega Inspección a una clínica y piden el registro",
    copy("Llega Inspección a tu clínica y pide el registro de jornada 📋", "Con Fíchalo lo tienes en PDF en un clic, sin buscar hojas.", "clinica"),
    titular="Llega Inspección a tu clínica", acento="Inspección", escenas=[
    {"escena": "caos", "voz": "Llega Inspección y te pide el registro de jornada de todo el año.", "postit": "¿Hojas de marzo?\n¿Dónde están?"},
    {"escena": "inspeccion", "voz": "Con Fíchalo, sacas el informe desde el móvil en un momento.", "pide": "Registro de jornada,\npor favor", "da": "Informe PDF"},
    {"escena": "feliz", "voz": "Todo guardado, como pide la ley. Cuatro años.", "texto": "Registro en regla"}])
add("85_monigotes_tienda-olvido", "monigotes", "comercio", "monigotes: dependienta se va sin fichar la salida y le llega el aviso",
    copy("Cierra la tienda y se va sin fichar la salida 🏪", "Fíchalo le avisa en el móvil y lo arregla en un segundo.", "comercio"),
    titular="Cierra la tienda y se olvida de fichar", acento="se olvida", escenas=[
    {"escena": "olvido", "voz": "Diez de la noche. Ane cierra la tienda y se va sin fichar la salida.", "aviso": "¿Te has olvidado de\nfichar la salida?", "ok": "Salida 22:01", "minimo": 3.4},
    {"escena": "jefe_movil", "voz": "Fíchalo le avisa, ficha, y tú tienes las horas bien al día siguiente.", "cab": "Tienda Gamarra", "sub": "Hoy",
     "filas": [["Ane", "14:00 – 22:01", OK], ["Leire", "10:00 – 14:00", OK]]},
    {"escena": "feliz", "voz": "Sin hojas, sin corregir nada a fin de mes.", "texto": "Horas correctas"}])
add("86_monigotes_taller-viernes", "monigotes", "taller", "monigotes: viernes en el taller calculando horas extra",
    copy("Viernes en el taller: ¿cuántas horas extra ha hecho cada uno? 🔧", "Con Fíchalo las horas extra salen solas, persona a persona.", "taller"),
    titular="Viernes en el taller: ¿y las horas extra?", acento="horas extra", escenas=[
    {"escena": "calcula", "voz": "Viernes. ¿Cuántas horas extra han hecho tus mecánicos esta semana? Ni idea.", "numeros": ["41h?", "¿38?", "+3?", "44?"]},
    {"escena": "llega", "voz": "Si fichan con el móvil al entrar y al salir...", "lugar": "Taller Zabala", "hora": "07:55"},
    {"escena": "jefe_movil", "voz": "Fíchalo te da las horas extra de cada uno, sin calculadora.", "cab": "Esta semana", "sub": "Horas extra",
     "filas": [["Unai", "43 h · 3 extra", OK], ["Mikel", "40 h", OK], ["Josu", "44 h · 4 extra", OK]]}])
add("87_monigotes_gestoria-papeles", "monigotes", "gestoria", "monigotes: gestor recibiendo horas de 20 clientes en papeles y fotos",
    copy("Gestorías: final de mes y las horas de los clientes llegan así 📲", "Si tus clientes fichan con Fíchalo, te pasan un Excel limpio.", "gestoria"),
    titular="Fin de mes en una gestoría", acento="gestoría", escenas=[
    {"escena": "caos", "voz": "Fin de mes en la gestoría. Las horas de los clientes llegan en fotos, papeles y audios.", "postit": "Bar Iruña: foto\nTaller: mañana\nTienda: ¿?"},
    {"escena": "jefe_movil", "voz": "Si tus clientes fichan con Fíchalo, te mandan un informe limpio en PDF o Excel.", "cab": "Informe · Octubre", "sub": "Exportar a Excel",
     "filas": [["Sonia", "164 h", OK], ["Iker", "171 h", OK], ["Paula", "96 h", OK]]},
    {"escena": "feliz", "voz": "Nóminas sin perseguir a nadie.", "texto": "Nóminas listas"}])
add("88_monigotes_peluqueria-turnos", "monigotes", "peluqueria", "monigotes: peluquería con turnos partidos, quién está ahora",
    copy("Peluquería con turnos partidos: ¿quién está ahora mismo? ✂️", "Con Fíchalo lo ves en el móvil, aunque no estés en el salón.", "peluqueria"),
    titular="¿Quién está ahora en tu peluquería?", acento="ahora", escenas=[
    {"escena": "caos", "voz": "Turnos partidos, dos salones, y tú sin saber quién está ahora mismo.", "postit": "Nerea: tarde?\nSara: ¿partido?\nLeire: libra"},
    {"escena": "llega", "voz": "Cada una ficha al llegar, desde su móvil.", "lugar": "Salón Centro", "hora": "15:58", "acc": ["pelo"]},
    {"escena": "jefe_movil", "voz": "Y tú ves quién está trabajando en cada salón.", "cab": "Quién está trabajando",
     "filas": [["Nerea · Centro", "Fichó 15:58", OK], ["Sara · Lakua", "Fichó 16:01", OK], ["Leire", "Libre hoy", ""]]}])

# ---------------------------------------------------------------- CHAT (7)
add("89_chat_peluqueria-foto-borrosa", "chat", "peluqueria", "chat: peluquera manda sus horas en foto borrosa",
    copy("Fin de mes en una peluquería: las horas llegan en una foto borrosa 📸", "Con Fíchalo se apuntan solas cada día.", "peluqueria"),
    titular="Cada fin de mes en una peluquería:", acento="fin de mes", contacto="Nerea (peluquera)", mensajes=[
    {"de": "el", "texto": "Hola! Te paso mis horas de octubre"},
    {"de": "el", "foto": ["Horas · Nerea", "lun 9-14 / 16-20", "mar 9-14 ¿?", "mié libre", "jue 10-20"]},
    {"de": "yo", "texto": "Nerea, no se lee nada. ¿El martes saliste a las 2?"},
    {"de": "el", "texto": "Creo que sí... o a las 3, no me acuerdo"}],
    giro={"texto": "O que se apunten solas", "acento": "solas", "cab": "Horas de octubre", "filas": [["Nerea", "148 h", OK], ["Leire", "151 h", OK], ["Sara", "139 h", OK]]})
add("90_chat_bar-horas-extra", "chat", "hosteleria", "chat: camarero reclama horas extra que nadie apuntó",
    copy("Tu camarero te reclama 20 horas extra. ¿Cómo sabes si es verdad? 🍺", "Con Fíchalo cada hora queda registrada, para él y para ti.", "hosteleria"),
    titular="Cuando un camarero te escribe esto:", acento="esto", contacto="Jon (camarero)", mensajes=[
    {"de": "el", "texto": "Jefe, en octubre hice unas 20 horas extra"},
    {"de": "el", "texto": "¿Me las pagas este mes?"},
    {"de": "yo", "texto": "¿20? Yo calculo que como mucho 10..."},
    {"de": "el", "texto": "Pues yo me quedé casi todos los sábados"},
    {"de": "yo", "texto": "¿Y dónde lo tenemos apuntado?"}],
    giro={"texto": "Con Fíchalo, no hay discusión", "acento": "no hay discusión", "cab": "Jon · Octubre", "sub": "Horas extra", "filas": [["Semana 1", "+3 h", OK], ["Semana 2", "+4 h", OK], ["Semana 3", "+2 h", OK], ["Total", "9 h extra", OK]]})
add("91_chat_limpieza-edificio-3", "chat", "limpieza", "chat: encargada pregunta si alguien ha llegado al edificio 3",
    copy("6:30 y el cliente pregunta si ya habéis empezado en su edificio 🧹", "Con Fíchalo lo ves al momento: quién ha fichado y dónde.", "limpieza"),
    titular="6:30 en una empresa de limpieza:", acento="6:30", contacto="Cliente · Edificio 3", mensajes=[
    {"de": "el", "texto": "Buenos días, ¿hoy viene alguien a limpiar el portal?"},
    {"de": "yo", "texto": "Sí, Rosa entra a las 6. Ahora la llamo"},
    {"de": "yo", "texto": "No me coge... te digo algo enseguida"},
    {"de": "el", "texto": "Es que aquí no hay nadie todavía"}],
    giro={"texto": "O míralo en un segundo", "acento": "un segundo", "cab": "Quién está trabajando", "filas": [["Rosa · Edif. 3", "Fichó 06:04", OK], ["Mari · Edif. 1", "Fichó 05:58", OK], ["Lucía · Edif. 4", "Fichó 06:02", OK]]})
add("92_chat_gestoria-mananate-las-paso", "chat", "gestoria", "chat: gestor pide horas para nóminas y el cliente las retrasa",
    copy("Gestor/a: ¿cuántas veces has escrito este mensaje este mes? 📲", "Si tu cliente usa Fíchalo, las horas salen en un Excel en un clic.", "gestoria"),
    titular="El chat de una gestoría el día 28:", acento="día 28", contacto="Bar Iruña (cliente)", mensajes=[
    {"de": "yo", "texto": "Hola! ¿Me pasas las horas de octubre para las nóminas?"},
    {"de": "el", "texto": "Sí sí, mañana te las paso"},
    {"de": "yo", "texto": "Hola de nuevo, ¿y las horas? Cierro nóminas hoy"},
    {"de": "el", "foto": ["Cuadrante oct.", "Iker: igual que sept.", "Ane: +2 sábados", "Jon: ver audio"]}],
    giro={"texto": "Si fichan con Fíchalo:", "acento": "Fíchalo", "cab": "Bar Iruña · Octubre", "sub": "Exportado a Excel", "filas": [["Iker", "160 h", OK], ["Ane", "168 h", OK], ["Jon", "152 h", OK]]})
add("93_chat_clinica-mis-horas", "chat", "clinica", "chat: higienista pide sus horas del mes",
    copy("Tu higienista te pide sus horas del mes. ¿Las tienes? 🦷", "En Fíchalo cada persona puede ver sus propias horas.", "clinica"),
    titular="Tu higienista te escribe esto:", acento="esto", contacto="Maite (higienista)", mensajes=[
    {"de": "el", "texto": "Hola! ¿Me puedes pasar mis horas de octubre?"},
    {"de": "el", "texto": "Creo que me falta una tarde en la nómina"},
    {"de": "yo", "texto": "Uf, lo tengo en la libreta de recepción, lo miro"},
    {"de": "yo", "texto": "La libreta no está... ¿te acuerdas qué tarde fue?"}],
    giro={"texto": "Con Fíchalo, ella misma lo ve", "acento": "ella misma", "cab": "Maite · Octubre", "sub": "Sus horas, en su móvil", "filas": [["Semana 1", "30 h", OK], ["Semana 2", "34 h", OK], ["Semana 3", "30 h", OK]]})
add("94_chat_comercio-quien-abre", "chat", "comercio", "chat: dueño de 3 tiendas pregunta quién ha abierto",
    copy("Tres tiendas y a las 10:05 no sabes cuál ha abierto 🏪", "Con Fíchalo ves quién ha fichado en cada tienda.", "comercio"),
    titular="Tienes 3 tiendas y son las 10:05", acento="10:05", contacto="Leire (encargada)", mensajes=[
    {"de": "yo", "texto": "Leire, ¿alguien ha abierto ya la tienda de Lakua?"},
    {"de": "el", "texto": "Ni idea, yo estoy en la del centro"},
    {"de": "el", "texto": "Llamo a Sara a ver"},
    {"de": "el", "texto": "Dice que está aparcando, que llega en 10 min"}],
    giro={"texto": "O míralo sin llamar a nadie", "acento": "sin llamar", "cab": "Tiendas · Hoy", "filas": [["Centro · Leire", "Fichó 09:56", OK], ["Lakua · Sara", "Sin fichar", ""], ["Gamarra · Ane", "Fichó 09:58", OK]]})
add("95_chat_taller-me-quede", "chat", "taller", "chat: mecánico dice que se quedó 2 horas más",
    copy("\"El viernes me quedé dos horas más\". ¿Y tú cómo lo compruebas? 🔧", "Con Fíchalo las horas extra quedan registradas solas.", "taller"),
    titular="Lunes por la mañana en el taller:", acento="Lunes", contacto="Unai (mecánico)", mensajes=[
    {"de": "el", "texto": "Jefe, el viernes me quedé 2 horas más con la furgoneta"},
    {"de": "el", "texto": "Apúntamelo como extra porfa"},
    {"de": "yo", "texto": "Vale, ¿dónde lo apunto? ¿en la pizarra?"},
    {"de": "el", "texto": "En la pizarra ya no cabe, ponlo en la hoja de la oficina"}],
    giro={"texto": "O que quede apuntado solo", "acento": "solo", "cab": "Unai · Esta semana", "sub": "Horas extra", "filas": [["Viernes", "08:00 – 19:05", OK], ["Extra", "+2 h", OK]]})

# ---------------------------------------------------------------- QUIZ (7)
Q = [
    ("Somos 4 en el taller, así que no llevamos registro de jornada.", "MULTA", "El registro es obligatorio en todas las empresas, tengan los trabajadores que tengan.", "todas"),
    ("Mis trabajadores fichan desde el móvil.", "LEGAL", "La ley no obliga a un sistema concreto: vale si es fiable y refleja la jornada real.", "fiable"),
    ("Borro los registros de jornada cada año para no acumular papeles.", "MULTA", "Hay que conservarlos 4 años.", "4 años"),
    ("Un trabajador me pide ver sus registros y le digo que no.", "MULTA", "Los registros tienen que estar a disposición de los trabajadores.", "trabajadores"),
    ("Solo apuntamos la hora de entrada.", "MULTA", "El registro incluye la hora de inicio y la de fin de la jornada de cada persona.", "inicio y la de fin"),
    ("Llevamos el registro en una hoja de papel que firman cada día.", "LEGAL", "El papel vale, si se rellena cada día con las horas reales.", "cada día"),
    ("Los que trabajan a media jornada no fichan.", "MULTA", "También hay que registrar la jornada de quien trabaja a tiempo parcial.", "tiempo parcial"),
    ("Inspección pide el registro y se lo doy en un informe en PDF.", "LEGAL", "El registro tiene que estar a disposición de la Inspección de Trabajo.", "Inspección"),
    ("A fin de mes relleno yo las horas de todos, de memoria.", "MULTA", "El registro es diario, con la hora real de inicio y fin.", "diario"),
    ("Mis empleados pueden consultar sus horas en la app.", "LEGAL", "Al contrario: tienen derecho a acceder a sus registros.", "derecho"),
    ("Hacen horas extra y no las apuntamos.", "MULTA", "Las horas extra también tienen que quedar registradas.", "también"),
    ("Guardo los registros de jornada durante 4 años.", "LEGAL", "Es justo lo que pide la ley.", "la ley"),
    ("En la clínica hay turnos y cada uno ficha en el suyo.", "LEGAL", "Cada persona registra su jornada, sea cual sea su turno.", "su jornada"),
    ("Tengo 3 centros y solo registro las horas en el principal.", "MULTA", "Hay que registrar la jornada de cada trabajador, esté en el centro que esté.", "cada trabajador"),
]
NICHOS_Q = ["taller", "ley", "ley", "hosteleria", "clinica", "comercio", "limpieza"]
GANCHOS_Q = ["¿Legal o multa? 2 preguntas sobre el registro de jornada ⚖️", "¿Cuántas aciertas? Registro de jornada, versión rápida ⚖️",
             "Test express para dueños de negocio: ¿legal o multa? ⚖️", "2 situaciones que vemos cada semana en bares. ¿Legal o multa? ⚖️",
             "Clínicas: ¿legal o multa? ⚖️", "Si tienes tienda, haz este test de 10 segundos ⚖️", "Empresas con varios centros: ¿legal o multa? ⚖️"]
for i in range(7):
    a, b = Q[2 * i], Q[2 * i + 1]
    add(f"{96 + i}_quiz_legal-o-multa-{i + 1}", "quiz", NICHOS_Q[i], f"quiz: {a[0][:40]} / {b[0][:40]}",
        copy(GANCHOS_Q[i], "Con Fíchalo tu registro de jornada está siempre en regla.", NICHOS_Q[i]),
        preguntas=[{"situacion": x[0], "respuesta": x[1], "porque": x[2], "acento_porque": x[3]} for x in (a, b)])

# ---------------------------------------------------------------- VOZ (7)
add("103_voz_clinica-postit", "voz", "clinica", "voz: clínica que apunta horas en pósits",
    copy("Si tienes una clínica, esto te interesa 🦷", "Fichaje desde el móvil y el informe para Inspección en un clic.", "clinica"),
    titular="Si tienes una clínica, mira esto", acento="clínica", frases=[
    {"voz": "¿Tus higienistas apuntan las horas en un pósit?", "postit": "Laura: 6h?\nMaite: salió\n¿a las 3?"},
    {"voz": "Si viene Inspección, eso no te sirve.", "emoji": "📋"},
    {"voz": "Con Fíchalo fichan desde el móvil, y tú lo ves todo en tiempo real.", "movil": {"cab": "Clínica Dental Arana", "filas": [["Laura", "Fichó 08:58", OK], ["Maite", "Fichó 09:02", OK], ["Iratxe", "Fichó 14:57", OK]]}},
    {"voz": "Y el informe para Inspección, en un clic.", "emoji": "✅"}])
add("104_voz_bar-3-errores", "voz", "hosteleria", "voz: 3 errores con el fichaje en un bar",
    copy("3 errores con el fichaje que vemos en casi todos los bares 🍺", "Fíchalo los resuelve desde el móvil de cada camarero.", "hosteleria"),
    titular="3 errores con el fichaje en tu bar", acento="3 errores", frases=[
    {"voz": "Tres errores con el fichaje que vemos en casi todos los bares.", "numero": "3"},
    {"voz": "Uno: la hoja de firmas que se rellena el día treinta.", "papel": ["Registro · Octubre", "Iker 8:00 – 16:00", "Iker 8:00 – 16:00", "Iker 8:00 – 16:00", "(firmado el día 30)"]},
    {"voz": "Dos: las horas extra que nadie apunta.", "emoji": "⏰"},
    {"voz": "Tres: no saber quién está trabajando ahora mismo.", "emoji": "❓"},
    {"voz": "Con Fíchalo, los tres resueltos desde el móvil.", "movil": {"cab": "Bar Txoko", "filas": [["Iker", "Fichó 17:58", OK], ["Ane", "Fichó 18:02", OK]]}}])
add("105_voz_limpieza-sin-llamar", "voz", "limpieza", "voz: saber quién ha empezado en cada edificio sin llamar",
    copy("Empresas de limpieza: deja de llamar a las 6 de la mañana 🧹", "Con Fíchalo ves quién ha fichado en cada edificio.", "limpieza"),
    titular="Empresas de limpieza: esto es para ti", acento="limpieza", frases=[
    {"voz": "¿Tienes una empresa de limpieza con gente en varios edificios?", "emoji": "🧹"},
    {"voz": "¿Cuántas llamadas haces cada mañana para saber si han llegado?", "postit": "6:05 Rosa ok\n6:12 Mari ¿?\n6:20 llamar"},
    {"voz": "Con Fíchalo cada persona ficha al llegar al edificio, desde su móvil.", "movil": {"cab": "Quién está trabajando", "filas": [["Rosa · Edif. 1", "Fichó 05:58", OK], ["Mari · Edif. 3", "Fichó 06:02", OK], ["Lucía · Edif. 4", "Fichó 06:05", OK]]}},
    {"voz": "Y tú lo ves todo sin hacer ni una llamada.", "emoji": "📵"}])
add("106_voz_gestoria-reenvia", "voz", "gestoria", "voz: gestorías, el vídeo para mandar a los clientes",
    copy("Gestoría: mándale este vídeo al cliente que siempre te pasa las horas tarde 📲", "Con Fíchalo las horas salen en PDF o Excel, listas para nóminas.", "gestoria"),
    titular="Gestoría: manda esto a tus clientes", acento="Gestoría", frases=[
    {"voz": "Si eres gestor, manda este vídeo a tus clientes.", "emoji": "📲"},
    {"voz": "Ese cliente que te pasa las horas en fotos, audios y papeles.", "postit": "Horas oct:\nver foto 1, 2\ny la 3 borrosa"},
    {"voz": "Con Fíchalo, su equipo ficha desde el móvil.", "emoji": "📱"},
    {"voz": "Y tú recibes un Excel limpio, listo para nóminas.", "movil": {"cab": "Informe · Octubre", "sub": "Exportar a Excel", "filas": [["Sonia", "164 h", OK], ["Iker", "171 h", OK], ["Paula", "96 h", OK]]}}])
add("107_voz_comercio-varias-tiendas", "voz", "comercio", "voz: varias tiendas, quién está en cada una",
    copy("¿Tienes más de una tienda? Esto es para ti 🏪", "Con Fíchalo ves quién está en cada tienda desde el móvil.", "comercio"),
    titular="¿Tienes más de una tienda?", acento="más de una", frases=[
    {"voz": "¿Tienes más de una tienda?", "emoji": "🏪"},
    {"voz": "Entonces sabes lo que es no saber quién ha abierto cada una.", "postit": "Centro ok\nLakua ¿?\nGamarra ¿?"},
    {"voz": "Con Fíchalo, cada dependienta ficha en su tienda, con el móvil o con la tablet.", "emoji": "📱"},
    {"voz": "Y tú ves las tres a la vez, estés donde estés.", "movil": {"cab": "Tiendas · Hoy", "filas": [["Centro · Leire", "Fichó 09:56", OK], ["Lakua · Sara", "Fichó 09:59", OK], ["Gamarra · Ane", "Fichó 09:58", OK]]}}])
add("108_voz_taller-horas-extra", "voz", "taller", "voz: horas extra en el taller sin pizarra",
    copy("¿En tu taller las horas extra se apuntan en una pizarra? 🔧", "Con Fíchalo se calculan solas, persona a persona.", "taller"),
    titular="Las horas extra de tu taller", acento="horas extra", frases=[
    {"voz": "¿En tu taller las horas extra se apuntan en una pizarra?", "emoji": "🔧"},
    {"voz": "Y a fin de mes nadie se acuerda de quién se quedó y cuánto.", "postit": "Unai +2?\nJosu viernes\n¿Mikel?"},
    {"voz": "Con Fíchalo, cada mecánico ficha al entrar y al salir.", "emoji": "📱"},
    {"voz": "Y las horas extra salen solas, persona a persona.", "movil": {"cab": "Horas extra · Octubre", "filas": [["Unai", "+9 h", OK], ["Josu", "+6 h", OK], ["Mikel", "+2 h", OK]]}}])
add("109_voz_ley-3-cosas", "voz", "ley", "voz: 3 cosas que tiene que cumplir el registro de jornada",
    copy("3 cosas que tiene que cumplir tu registro de jornada ⚖️", "Fíchalo cumple las tres sin que tengas que pensar en ello.", "ley"),
    titular="3 cosas que pide la ley de tu registro", acento="3 cosas", frases=[
    {"voz": "Tres cosas que tiene que cumplir tu registro de jornada.", "numero": "3"},
    {"voz": "Uno: hora de inicio y de fin, cada día, de cada trabajador.", "emoji": "⏰"},
    {"voz": "Dos: guardarlo cuatro años.", "numero": "4"},
    {"voz": "Tres: que lo puedan ver tus trabajadores y la Inspección.", "emoji": "📋"},
    {"voz": "Con Fíchalo, las tres, desde el móvil.", "emoji": "✅"}])

# ---------------------------------------------------------------- PÓSIT (4 nuevos; los otros 3 son 79, 75 y 81)
def postit_reel(id_, nicho, tema, cp, pregunta, acento, postit, subt, esc2, cierre, cierre_ac):
    add(id_, "postit", nicho, tema, cp, duracion=8.5, escenas=[
        {"tipo": "objeto", "pregunta": pregunta, "acento": acento, "fondo": "oscuro", "postit": postit, "subtitulo": subt},
        esc2, {"tipo": "cierre", "texto": cierre, "acento": cierre_ac}])

postit_reel("110_postit_bar-extras-sabado", "hosteleria", "pósit: horas extra del sábado en un bar",
    copy("Las extras del sábado, apuntadas en un pósit en la caja 🍺", "Con Fíchalo quedan registradas solas.", "hosteleria"),
    "¿Las extras del sábado\nestán apuntadas así?", "así", "Sábado:\nJon +2 ¿o 3?\nAne hasta cierre", "Hostelería",
    {"tipo": "tabla", "titulo": "Con Fíchalo,\nse apuntan solas", "acento": "solas", "cabecera": "Horas extra · Sábado",
     "filas": [["Jon · Sala", "+3 h"], ["Ane · Barra", "+2 h"], ["Iker · Cocina", "+1 h"]], "pie": ["Total", "6 h"], "fondo": "menta"},
    "Pruébalo en\ntu bar", "tu bar")
postit_reel("111_postit_limpieza-quien-falta", "limpieza", "pósit: quién falta hoy en limpieza",
    copy("¿Quién falta hoy? Si lo sabes por un pósit, mal empezamos 🧹", "Con Fíchalo lo ves en el móvil antes de que llame el cliente.", "limpieza"),
    "¿Sabes quién falta hoy\nsin hacer llamadas?", "quién falta", "Rosa ok\nMari ¿?\nLucía no coge", "Empresas de limpieza",
    {"tipo": "movil", "titulo": "Míralo en el móvil", "acento": "móvil", "cabecera": "Quién está trabajando",
     "filas": [["Rosa · Edif. 1", "Fichó 05:58"], ["Mari · Edif. 3", "Fichó 06:02"], ["Lucía · Edif. 4", "Sin fichar"]], "estado": "Aviso enviado a Lucía", "fondo": "cielo"},
    "Pruébalo con\ntu equipo", "tu equipo")
postit_reel("112_postit_gestoria-nominas", "gestoria", "pósit: gestoría con horas para nóminas en pósit",
    copy("Las horas para nóminas no deberían llegar en un pósit 📲", "Si tus clientes fichan con Fíchalo, recibes un Excel limpio.", "gestoria"),
    "¿Las horas para nóminas\nte llegan así?", "así", "Iker: igual\nque el mes pasado\nAne: +2", "Gestorías y asesorías",
    {"tipo": "tabla", "titulo": "O en un Excel,\nlisto para nóminas", "acento": "listo", "cabecera": "Informe · Octubre",
     "filas": [["Iker", "160 h"], ["Ane", "168 h"], ["Jon", "152 h"]], "pie": ["Exportar", "PDF / Excel"], "fondo": "menta"},
    "Recomiéndaselo\na tus clientes", "tus clientes")
postit_reel("113_postit_comercio-cambio-turno", "comercio", "pósit: cambio de turno apuntado en pósit en la tienda",
    copy("Cambios de turno apuntados en un pósit pegado a la caja 🏪", "Con Fíchalo cada uno ficha su turno real y tú lo ves todo.", "comercio"),
    "¿Los cambios de turno\nse apuntan así?", "así", "Sara cambia\ncon Leire\n¿el jueves?", "Comercio",
    {"tipo": "movil", "titulo": "Cada una ficha\nsu turno real", "acento": "turno real", "cabecera": "Tienda Centro · Jueves",
     "filas": [["Leire", "10:00 – 14:00"], ["Sara", "16:00 – 20:30"]], "estado": "Horas al día", "fondo": "cielo"},
    "Pruébalo en\ntu tienda", "tu tienda")

json.dump({"reels": R}, open(os.path.join(os.path.dirname(__file__), "lote_082.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(R), "reels")
