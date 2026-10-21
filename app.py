import re
import html
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuración de límite de caracteres para evitar sobrecarga
MAX_TEXT_LENGTH = 2000

# -----------------------------------------------------------------------------
# DEFINICIÓN DE PATRONES DE EXPRESIONES REGULARES GENERALES (SIS120)
# Diseñados mediante unión formal (|), concatenación, clases de caracteres
# y cuantificadores de Kleene para reconocer familias lingüísticas,
# sin depender de oraciones memorizadas rígidas.
# -----------------------------------------------------------------------------
PATTERNS = [
    {
        "id": "urgencia",
        "name": "Lenguaje de urgencia y presión para actuar",
        "category": "urgencia",
        "category_label": "Presión temporal / Urgencia",
        "regex": r"\b(?:urgente(?:s)?|urgencia|inmediat[oa](?:mente)?|de\s+inmediato|hoy|cuanto\s+antes|a\s+la\s+brevedad|act[uú](?:a|e)\s+(?:ya|ahora)|[uú]ltimo\s+(?:aviso|recordatorio|plazo)|plazo\s+l[ií]mite|tiempo\s+l[ií]mite|(?:vence|expira)\s+(?:hoy|pronto|en\s+\d+\s*(?:horas?|minutos?)))\b",
        "flags": re.IGNORECASE,
        "flags_desc": "re.IGNORECASE (Ignora mayúsculas y minúsculas)",
        "explanation": "Detecta familias de expresiones que ejercen presión psicológica o urgencia temporal para forzar una reacción apresurada del usuario.",
        "operators": [
            {
                "symbol": r"\b",
                "meaning": "Límites de palabra (word boundary) para evitar falsos positivos dentro de otras palabras (ej. 'joya')."
            },
            {
                "symbol": r"(?:...|...)",
                "meaning": "Grupo de no captura con el operador de alternancia '|' que representa la unión formal de lenguajes regulares L1 ∪ L2 ∪ ... ∪ Ln."
            },
            {
                "symbol": r"[uú] / [ií]",
                "meaning": "Clases de caracteres que reconocen variantes ortográficas con o sin tilde (concatenación de alfabetos extendidos)."
            },
            {
                "symbol": r"\s+",
                "meaning": "Cuantificador cerradura positiva '+' sobre espacios en blanco (uno o más espacios)."
            }
        ],
        "sample_match": "Aviso URGENTE: debe responder inmediatamente o su plazo límite vence hoy.",
        "sample_nomatch": "Mañana tengo una reunión normal en la universidad."
    },
    {
        "id": "dinero",
        "name": "Cantidades monetarias (Bolivianos / Bs)",
        "category": "dinero",
        "category_label": "Monto económico (Bs)",
        "regex": r"\b(?:(?:Bs\.?|BOB)\s*[0-9]+(?:[.,][0-9]+)*|[0-9]+(?:[.,][0-9]+)*\s*(?:Bs\.?|BOB|bolivianos?))\b",
        "flags": re.IGNORECASE,
        "flags_desc": "re.IGNORECASE (Reconoce 'bs', 'Bs', 'BS', 'bob', 'bolivianos')",
        "explanation": "Reconoce cantidades monetarias en moneda nacional con prefijo o sufijo (Bs, BOB, bolivianos), contemplando números simples o con separadores de miles y decimales.",
        "operators": [
            {
                "symbol": r"\b",
                "meaning": "Delimitadores de frontera de palabra al inicio y fin de la cifra."
            },
            {
                "symbol": r"(?:Bs\.?|BOB)",
                "meaning": "Prefijo monetario opcional con punto escapado '\\.' opcional ('?' cuantifica 0 o 1 ocurrencia)."
            },
            {
                "symbol": r"[0-9]+",
                "meaning": "Clase de caracteres para dígitos decimales del 0 al 9 con '+' (cerradura positiva de Kleene)."
            },
            {
                "symbol": r"(?:[.,][0-9]+)*",
                "meaning": "Cerradura de Kleene '*' (0 o más repeticiones) para agrupaciones numéricas de miles y decimales con punto o coma."
            }
        ],
        "sample_match": "Su premio acumulado asciende a Bs 5000 o 3500 bolivianos disponibles.",
        "sample_nomatch": "El código de autorización es 849204 sin valor financiero."
    },
    {
        "id": "solicitud_datos",
        "name": "Verificación o actualización de cuentas y datos",
        "category": "solicitud_datos",
        "category_label": "Solicitud de credenciales / Datos",
        "regex": r"\b(?:(?:confirm(?:a|e|ar)|verific(?:a|e|ar)|actualiz(?:a|e|ar)|valid(?:a|e|ar)|proporcion(?:a|e|ar)|ingres(?:a|e|ar)\s+a\s+verificar|reactiv(?:a|e|ar))\s+(?:de\s+nuevo\s+)?(?:(?:tu|tus|su|sus|el|la)\s+)?(?:cuenta|datos(?:\s+personales)?|informaci[oó]n(?:\s+personal)?|identidad|credenciales|perfil))\b",
        "flags": re.IGNORECASE,
        "flags_desc": "re.IGNORECASE (Ignora mayúsculas y minúsculas)",
        "explanation": "Detecta familias sintácticas de solicitudes de credenciales combinando verbos de acción (imperativos o infinitivos), pronombres posesivos y sustantivos objeto.",
        "operators": [
            {
                "symbol": r"(?:confirm(?:a|e|ar)...)",
                "meaning": "Alternancia morfológica que engloba conjugaciones en modo imperativo ('verifica', 'verifique') e infinitivo ('verificar')."
            },
            {
                "symbol": r"(?:(?:tu|tus|su|sus|el|la)\s+)?",
                "meaning": "Cuantificador opcional '?' aplicado a la concatenación de pronombres determinantes posesivos o artículos."
            },
            {
                "symbol": r"(?:cuenta|datos...)",
                "meaning": "Unión formal de sustantivos clave que representan información sensible del usuario."
            }
        ],
        "sample_match": "Por favor verifica tus datos o actualice su información personal de inmediato.",
        "sample_nomatch": "Consulta el cronograma de clases en el panel de la facultad."
    },
    {
        "id": "enlaces",
        "name": "Enlaces web",
        "category": "enlaces",
        "category_label": "Hipervínculo / Enlace externo",
        "regex": r"https?://\S+|www\.\S+",
        "flags": re.IGNORECASE,
        "flags_desc": "re.IGNORECASE (Reconoce HTTP, HTTPS y WWW)",
        "explanation": "Localiza direcciones URL completas con protocolo (http:// o https://) o con prefijo www dirigidas a servidores externos.",
        "operators": [
            {
                "symbol": "https?://",
                "meaning": "Protocolo 'http' con carácter 's' opcional ('s?') seguido literalmente del separador '://'."
            },
            {
                "symbol": "|",
                "meaning": "Operador de unión de lenguajes (OR): URL con protocolo O dominio que empiece en 'www.'."
            },
            {
                "symbol": r"\S+",
                "meaning": "Secuencia de uno o más caracteres distintos del espacio en blanco (alfabeto de caracteres de URL)."
            }
        ],
        "sample_match": "Acceda al formulario oficial en https://sitio-oficial.edu.bo/login",
        "sample_nomatch": "Comunícate por teléfono al interno 204."
    },
    {
        "id": "exclamacion",
        "name": "Exceso de signos de exclamación",
        "category": "exclamacion",
        "category_label": "Énfasis excesivo (!!!)",
        "regex": r"!{2,}|¡{2,}",
        "flags": 0,
        "flags_desc": "Sin modificación de mayúsculas (símbolos de puntuación)",
        "explanation": "Identifica dos o más signos de admiración contiguos de apertura o cierre, empleados comúnmente para llamar la atención en mensajes fraudulentos.",
        "operators": [
            {
                "symbol": "! / ¡",
                "meaning": "Símbolos literales de admiración."
            },
            {
                "symbol": "{2,}",
                "meaning": "Cuantificador de rango acotado inferiormente: exige un mínimo de 2 repeticiones sin límite superior."
            }
        ],
        "sample_match": "¡¡¡Atención!!! Has sido seleccionado entre los finalistas!!",
        "sample_nomatch": "¡Hola! Que tengas un excelente día de estudio."
    },
    {
        "id": "cuenta_bloqueada",
        "name": "Cuentas o tarjetas comprometidas (canceladas, bloqueadas, etc.)",
        "category": "cuenta_bloqueada",
        "category_label": "Estado de cuenta / Tarjeta comprometida",
        "regex": r"\b(?:(?:cuenta|tarjeta)s?(?:\s+(?:de\s+)?(?:cr[eé]dito|d[eé]bito|ahorros?|bancaria|corriente))?(?:\s+(?:ha\s+sido|fue|est[aá]|qued[oó]|ha\s+quedado|se\s+encuentra))\s+(?:cancelad[oa]|bloquead[oa]|cerrad[oa]|suspendid[oa]|restringid[oa]|inhabilitad[oa]|desactivad[oa])s?|(?:cuenta|tarjeta)s?(?:\s+(?:de\s+)?(?:cr[eé]dito|d[eé]bito|ahorros?|bancaria|corriente))?\s+(?:cancelad[oa]|bloquead[oa]|cerrad[oa]|suspendid[oa]|restringid[oa]|inhabilitad[oa]|desactivad[oa])s?|(?:cierre|bloqueo|suspensi[oó]n|cancelaci[oó]n|inhabilitaci[oó]n)\s+(?:de\s+(?:su|tu)\s+)?(?:cuenta|tarjeta)s?)\b",
        "flags": re.IGNORECASE,
        "flags_desc": "re.IGNORECASE (Ignora mayúsculas y minúsculas)",
        "explanation": "Detecta menciones sobre cuentas o tarjetas canceladas, bloqueadas, cerradas, suspendidas, restringidas o inhabilitadas, admitiendo variantes compuestas como 'tarjeta de crédito ha sido cancelada'.",
        "operators": [
            {
                "symbol": r"(?:cuenta|tarjeta)s?",
                "meaning": "Sustantivos fiduciarios con cuantificador opcional 's?' para singular y plural."
            },
            {
                "symbol": r"(?:\s+(?:de\s+)?(?:cr[eé]dito|...))?",
                "meaning": "Modificador nominal opcional que reconoce tipos de producto ('de crédito', 'de débito', 'bancaria')."
            },
            {
                "symbol": r"(?:\s+(?:ha\s+sido|fue|est[aá]...))",
                "meaning": "Sintagma verbal auxiliar que une el sujeto con el participio de estado."
            },
            {
                "symbol": r"(?:cancelad[oa]|bloquead[oa]...)s?",
                "meaning": "Clases de concordancia de género '[oa]' y número 's?' para adjetivos de estado comprometido."
            }
        ],
        "sample_match": "Su tarjeta de crédito ha sido cancelada por medidas de prevención.",
        "sample_nomatch": "Apertura de nueva tarjeta de débito en la agencia universitaria."
    },
    {
        "id": "amenaza_bloqueo",
        "name": "Amenazas de bloqueo, suspensión o pérdida de acceso",
        "category": "amenaza_bloqueo",
        "category_label": "Amenaza de bloqueo / Pérdida de acceso",
        "regex": r"\b(?:(?:tu|su)\s+(?:cuenta|tarjeta)s?(?:\s+(?:de\s+)?(?:cr[eé]dito|d[eé]bito|bancaria))?\s+(?:ser[aá]|quedar[aá])\s+(?:bloquead[oa]|suspendid[oa]|cancelad[oa]|inhabilitad[oa]|cerrad[oa]|restringid[oa])s?|(?:ser[aá]|quedar[aá]|procederemos\s+a)\s+(?:bloquead[oa]|suspendid[oa]|cancelad[oa]|inhabilitad[oa]|cerrad[oa]|restringid[oa])s?|p[eé]rdida\s+de\s+acceso|perder[aá]\s+(?:el\s+)?acceso|evit(?:e|ar)\s+(?:el\s+bloqueo|la\s+suspensi[oó]n|la\s+cancelaci[oó]n|la\s+inhabilitaci[oó]n))\b",
        "flags": re.IGNORECASE,
        "flags_desc": "re.IGNORECASE (Ignora mayúsculas y minúsculas)",
        "explanation": "Identifica amenazas condicionales futuras sobre consecuencias punitivas simuladas, tales como 'será bloqueada', 'perderá el acceso' o 'evite la suspensión'.",
        "operators": [
            {
                "symbol": r"(?:ser[aá]|quedar[aá])",
                "meaning": "Tiempo verbal futuro de consecuencia ('será', 'quedará')."
            },
            {
                "symbol": r"p[eé]rdida\s+de\s+acceso",
                "meaning": "Concatenación de términos que denotan revocación forzada del servicio."
            },
            {
                "symbol": r"evit(?:e|ar)",
                "meaning": "Construcción condicional típica de chantaje en ingeniería social ('para evitar el bloqueo')."
            }
        ],
        "sample_match": "Tu cuenta será bloqueada si no valida su clave en las próximas horas.",
        "sample_nomatch": "La conferencia universitaria será transmitida en vivo mañana."
    },
    {
        "id": "actividad_inusual",
        "name": "Actividad inusual, sospechosa o no autorizada",
        "category": "actividad_inusual",
        "category_label": "Alerta de seguridad / Acceso inusual",
        "regex": r"\b(?:actividad(?:es)?\s+(?:inusual(?:es)?|sospechosa?s?|no\s+reconocida?s?)|acceso(?:s)?\s+(?:sospechoso(?:s)?|no\s+autorizado(?:s)?|inusual(?:es)?)|movimiento(?:s)?\s+(?:inusual(?:es)?|sospechoso(?:s)?|no\s+autorizado(?:s)?)|intento\s+de\s+acceso)\b",
        "flags": re.IGNORECASE,
        "flags_desc": "re.IGNORECASE (Ignora mayúsculas y minúsculas)",
        "explanation": "Identifica advertencias sobre actividades inusuales, sospechosas, movimientos no reconocidos o accesos no autorizados.",
        "operators": [
            {
                "symbol": r"\b",
                "meaning": "Límites de palabra para aislar la frase sintáctica."
            },
            {
                "symbol": r"(?:actividad(?:es)?...)",
                "meaning": "Grupos de no captura con variantes morfológicas en singular y plural."
            },
            {
                "symbol": "|",
                "meaning": "Operador de alternancia para abarcar tanto actividades sospechosas como accesos o movimientos no autorizados."
            }
        ],
        "sample_match": "Notificación preventiva: detectamos una actividad inusual en su banca móvil.",
        "sample_nomatch": "La actividad académica presencial comenzará el próximo lunes."
    },
    {
        "id": "info_financiera",
        "name": "Solicitudes de datos financieros y personales sensibles",
        "category": "info_financiera",
        "category_label": "Datos bancarios / CVV / SSN / Claves",
        "regex": r"\b(?:n[uú]mero\s+de\s+tarjeta|fecha\s+de\s+vencimiento|c[oó]digo\s+de\s+seguridad|c[oó]digo\s+de\s+verificaci[oó]n|n[uú]mero\s+de\s+seguro\s+social|seguro\s+social|cvv|cvc|clave\s+(?:secreta|din[aá]mica|de\s+acceso)|pin\s+(?:de\s+seguridad)?|datos\s+personales|informaci[oó]n\s+financiera)\b",
        "flags": re.IGNORECASE,
        "flags_desc": "re.IGNORECASE (Ignora mayúsculas y minúsculas)",
        "explanation": "Detecta solicitudes de credenciales financieras y personales altamente confidenciales como número de tarjeta, fecha de vencimiento, CVV, PIN o seguro social.",
        "operators": [
            {
                "symbol": r"\b",
                "meaning": "Límite de palabra al inicio y término de cada expresión."
            },
            {
                "symbol": r"[uú] / [oó] / [aá]",
                "meaning": "Clases de caracteres que soportan ortografía con o sin tilde ('número'/'numero', 'código'/'codigo', 'dinámica'/'dinamica')."
            },
            {
                "symbol": "|",
                "meaning": "Operador de alternancia uniendo términos de credenciales sensibles."
            }
        ],
        "sample_match": "Para restablecer el servicio ingrese su número de tarjeta, fecha de vencimiento y código de seguridad.",
        "sample_nomatch": "Presente su carnet de identidad vigente en recepción para el trámite."
    },
    {
        "id": "correo_electronico",
        "name": "Direcciones de correo electrónico",
        "category": "correo_electronico",
        "category_label": "Correo electrónico (Informativo)",
        "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "flags": re.IGNORECASE,
        "flags_desc": "re.IGNORECASE (Reconoce formatos estándar RFC de email)",
        "explanation": "Localiza direcciones de correo electrónico. Categoría informativa: una dirección de correo por sí sola no debe considerarse prueba de estafa.",
        "operators": [
            {
                "symbol": r"\b",
                "meaning": "Límites de palabra para aislar la dirección de correo."
            },
            {
                "symbol": r"[A-Za-z0-9._%+-]+",
                "meaning": "Clase de caracteres permitidos en la parte local del usuario con cerradura positiva '+'."
            },
            {
                "symbol": "@",
                "meaning": "Carácter literal obligatorio '@' delimitador del host."
            },
            {
                "symbol": r"\.[A-Za-z]{2,}",
                "meaning": "Punto literal escapado seguido de TLD (extensión de dominio) de 2 o más letras."
            }
        ],
        "sample_match": "Envíe su documentación oficial a verificacion@banco-central.com para revisión.",
        "sample_nomatch": "Para comunicarse llame al número de teléfono 64-51234."
    }
]

# Compilar los patrones para mayor rendimiento
COMPILED_PATTERNS = {
    p["id"]: {
        **p,
        "compiled": re.compile(p["regex"], p["flags"])
    }
    for p in PATTERNS
}

# -----------------------------------------------------------------------------
# MENSAJES SIMULADOS PARA LA BANDEJA DE ENTRADA
# -----------------------------------------------------------------------------
INITIAL_MESSAGES = [
    {
        "id": "msg-1",
        "sender": "Biblioteca USFX",
        "avatar": "BU",
        "time": "10:15",
        "text": "Nos vemos en la biblioteca mañana para estudiar los ejercicios de autómatas.",
        "type_hint": "normal"
    },
    {
        "id": "msg-2",
        "sender": "Dirección de Carrera",
        "avatar": "DC",
        "time": "11:40",
        "text": "La reunión de hoy empieza a las 15:00 en la sala de conferencias.",
        "type_hint": "urgencia"
    },
    {
        "id": "msg-3",
        "sender": "Administración",
        "avatar": "AD",
        "time": "13:05",
        "text": "Recordatorio mensual: el arancel pendiente de laboratorio es de Bs 150 con fecha límite el 30 del presente mes.",
        "type_hint": "dinero"
    },
    {
        "id": "msg-4",
        "sender": "Portal Académico",
        "avatar": "PA",
        "time": "14:22",
        "text": "Estimado estudiante, actualiza tus datos en el sistema universitario antes del cierre de semestre.",
        "type_hint": "datos"
    },
    {
        "id": "msg-5",
        "sender": "Comité Docente",
        "avatar": "CD",
        "time": "16:00",
        "text": "Consulta el programa en https://ejemplo.test para descargar las guías prácticas.",
        "type_hint": "enlace"
    },
    {
        "id": "msg-6",
        "sender": "Alerta Móvil 24h",
        "avatar": "AM",
        "time": "17:35",
        "text": "URGENTE: ganaste Bs 5000. Verifica tus datos hoy!!",
        "type_hint": "sospechoso"
    }
]

SIMULATED_POOL = [
    {
        "sender": "Seguridad de Tarjetas",
        "avatar": "ST",
        "time": "Ahora",
        "text": "Su tarjeta de crédito ha sido cancelada, contáctese a este número 77747902 para reactivarla y siga los pasos",
        "type_hint": "sospechoso"
    },
    {
        "sender": "Alerta de Seguridad Bancaria",
        "avatar": "AS",
        "time": "Ahora",
        "text": "Aviso: su cuenta bancaria cerrada por actividad inusual. Envíe su número de tarjeta, fecha de vencimiento y número de seguro social a soporte@banco-alerta.com",
        "type_hint": "sospechoso"
    },
    {
        "sender": "Seguridad Bancaria",
        "avatar": "SB",
        "time": "Ahora",
        "text": "Tu cuenta será bloqueada; verifica tus datos inmediatamente en nuestro portal de validación.",
        "type_hint": "sospechoso"
    },
    {
        "sender": "Carlos Compañero",
        "avatar": "CC",
        "time": "Ahora",
        "text": "Hola amigo, ¿tienes los apuntes de la clase de ayer? Los necesito para repasar el examen.",
        "type_hint": "normal"
    },
    {
        "sender": "Sorteo Express",
        "avatar": "SE",
        "time": "Ahora",
        "text": "FELICITACIONES!! Fuiste seleccionado hoy para recibir un bono de Bs. 3200. Reclama en www.bono-bolivia.net ahora mismo!!",
        "type_hint": "sospechoso"
    },
    {
        "sender": "Soporte Universitario",
        "avatar": "SU",
        "time": "Ahora",
        "text": "Para consultas sobre la inscripción en el curso escribe a soporte.academico@usfx.bo durante días hábiles.",
        "type_hint": "enlace"
    }
]


# -----------------------------------------------------------------------------
# LÓGICA DE ANÁLISIS EN PYTHON (MOTOR REGEX)
# -----------------------------------------------------------------------------
def analyze_message_text(text: str) -> dict:
    """
    Ejecuta todos los patrones de expresiones regulares sobre el texto usando
    re.finditer() de la biblioteca estándar de Python.
    Calcula coincidencias exactas, posiciones y clasificación según las reglas del proyecto.
    """
    if not isinstance(text, str):
        text = str(text or "")

    # Limitar longitud para evitar sobrecargas
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]

    detected_categories = set()
    matches_list = []
    category_summary = {}

    for pattern_id, pattern_info in COMPILED_PATTERNS.items():
        compiled_regex = pattern_info["compiled"]
        pattern_matches = []

        # re.finditer() permite obtener cada coincidencia con su posición exacta
        for match in compiled_regex.finditer(text):
            matched_text = match.group(0)
            start_pos = match.start()
            end_pos = match.end()

            match_data = {
                "pattern_id": pattern_id,
                "pattern_name": pattern_info["name"],
                "category": pattern_info["category"],
                "category_label": pattern_info["category_label"],
                "matched_text": matched_text,
                "start": start_pos,
                "end": end_pos,
                "explanation": pattern_info["explanation"]
            }
            matches_list.append(match_data)
            pattern_matches.append(matched_text)

        if pattern_matches:
            detected_categories.add(pattern_info["category"])
            category_summary[pattern_info["category"]] = {
                "category_label": pattern_info["category_label"],
                "pattern_name": pattern_info["name"],
                "count": len(pattern_matches),
                "occurrences": pattern_matches
            }

    # Ordenar las coincidencias por posición de inicio en el texto
    matches_list.sort(key=lambda m: (m["start"], -(m["end"] - m["start"])))

    num_categories = len(detected_categories)

    # -------------------------------------------------------------------------
    # CLASIFICACIÓN ORIENTATIVA (Calculada en Python)
    # Cero categorías: «Sin indicadores detectados»
    # Una categoría: «Revisar con precaución»
    # Dos o más categorías distintas: «Mensaje sospechoso»
    # -------------------------------------------------------------------------
    if num_categories == 0:
        classification_title = "Sin indicadores detectados"
        severity = "safe"
        badge_class = "badge-safe"
        recommendation = (
            "No se detectaron los indicadores definidos en el sistema. "
            "Tenga en cuenta que la ausencia de coincidencias sintácticas NO garantiza "
            "que el mensaje sea seguro o legítimo; únicamente indica que no contiene los patrones preconfigurados."
        )
    elif num_categories == 1:
        classification_title = "Revisar con precaución"
        severity = "warning"
        badge_class = "badge-warning"

        # Tratamiento específico informativo para correos electrónicos solos
        if detected_categories == {"correo_electronico"}:
            recommendation = (
                "El mensaje contiene una dirección de correo electrónico detectada como categoría informativa. "
                "Una dirección de correo por sí sola no debe considerarse prueba de estafa. "
                "Verifique que el dominio del remitente corresponda a los canales oficiales de la entidad."
            )
        else:
            recommendation = (
                "El mensaje contiene 1 indicador sospechoso o contextual aislado. "
                "Se recomienda verificar la identidad del remitente por un canal seguro "
                "antes de interactuar o confiar plenamente en el contenido."
            )
    else:
        classification_title = "Mensaje sospechoso"
        severity = "danger"
        badge_class = "badge-danger"
        recommendation = (
            "Se detectaron 2 o más categorías distintas de indicadores concurrentes "
            "(como menciones de cuentas cerradas/canceladas, amenazas de bloqueo, "
            "solicitudes de información financiera sensible, urgencia, enlaces o montos monetarios). "
            "Este patrón es característico de ingeniería social o intentos de fraude. "
            "No proporcione información confidencial ni acceda a enlaces o números desconocidos."
        )

    academic_disclaimer = (
        "Nota académica SIS120: Esta clasificación se calcula exclusivamente a partir de "
        "coincidencias sintácticas mediante expresiones regulares en Python. No constituye "
        "una confirmación judicial de fraude, ni garantiza la seguridad de un mensaje sin coincidencias."
    )

    return {
        "text": text,
        "char_count": len(text),
        "total_matches": len(matches_list),
        "matches": matches_list,
        "categories_count": num_categories,
        "detected_categories": list(detected_categories),
        "category_summary": category_summary,
        "classification": {
            "title": classification_title,
            "severity": severity,
            "badge_class": badge_class,
            "recommendation": recommendation,
            "academic_disclaimer": academic_disclaimer
        }
    }


# -----------------------------------------------------------------------------
# RUTAS FLASK
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    """Sirve la interfaz web simuladora de aplicación móvil."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    Ruta que recibe el mensaje en formato JSON, ejecuta las expresiones regulares
    en Python y devuelve el análisis completo.
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "El campo 'text' debe ser una cadena de texto."}), 400

    if not text.strip():
        return jsonify({"error": "Por favor ingrese o seleccione un mensaje para analizar."}), 400

    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"El mensaje no debe superar los {MAX_TEXT_LENGTH} caracteres."}), 400

    result = analyze_message_text(text)
    return jsonify(result)


@app.route("/api/test-pattern", methods=["POST"])
def api_test_pattern():
    """
    Ruta didáctica para el Laboratorio Regex:
    Prueba un patrón específico contra una cadena de prueba en Python.
    """
    data = request.get_json(silent=True) or {}
    pattern_id = data.get("pattern_id")
    text = data.get("text", "")

    if pattern_id not in COMPILED_PATTERNS:
        return jsonify({"error": f"Patrón '{pattern_id}' no encontrado."}), 404

    if not isinstance(text, str):
        text = str(text or "")

    pattern_info = COMPILED_PATTERNS[pattern_id]
    compiled = pattern_info["compiled"]

    matches = []
    for match in compiled.finditer(text):
        matches.append({
            "matched_text": match.group(0),
            "start": match.start(),
            "end": match.end(),
            "groups": match.groups()
        })

    has_match = len(matches) > 0

    return jsonify({
        "pattern_id": pattern_id,
        "pattern_name": pattern_info["name"],
        "regex": pattern_info["regex"],
        "flags_desc": pattern_info["flags_desc"],
        "has_match": has_match,
        "matches_count": len(matches),
        "matches": matches,
        "explanation": pattern_info["explanation"],
        "sample_match": pattern_info["sample_match"],
        "sample_nomatch": pattern_info["sample_nomatch"],
        "operators": pattern_info["operators"]
    })


@app.route("/api/patterns", methods=["GET"])
def api_get_patterns():
    """Devuelve la lista didáctica completa de patrones para el laboratorio."""
    safe_list = []
    for p in PATTERNS:
        safe_list.append({
            "id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "category_label": p["category_label"],
            "regex": p["regex"],
            "flags_desc": p["flags_desc"],
            "explanation": p["explanation"],
            "operators": p["operators"],
            "sample_match": p["sample_match"],
            "sample_nomatch": p["sample_nomatch"]
        })
    return jsonify(safe_list)


@app.route("/api/mock-messages", methods=["GET"])
def api_mock_messages():
    """Devuelve los mensajes iniciales para la bandeja de entrada simulada."""
    return jsonify({
        "initial": INITIAL_MESSAGES,
        "simulated_pool": SIMULATED_POOL
    })


if __name__ == "__main__":
    print("=" * 65)
    print(" SMS SHIELD - SIS120 Lenguajes Formales y Autómatas")
    print(" Servidor Flask iniciado localmente en: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(debug=True, host="127.0.0.1", port=5000)
