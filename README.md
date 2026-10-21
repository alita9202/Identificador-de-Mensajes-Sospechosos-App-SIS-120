# 🛡️ SMS Shield - SIS120 Lenguajes Formales y Autómatas

**Simulador Móvil de Detección de Mensajes Sospechosos con Expresiones Regulares en Python**  
*Universidad Mayor, Real y Pontificia de San Francisco Xavier de Chuquisaca (USFX)*  
*Materia: SIS120 – Lenguajes Formales y Autómatas*

---

## 📋 Descripción del Proyecto

Aplicación web interactiva que simula la interfaz de un teléfono inteligente moderno de seguridad para mensajes SMS. La detección y el análisis sintáctico de los textos se ejecutan **realmente en el backend utilizando el módulo estándar `re` de Python**, comunicándose con la interfaz web mediante el microframework **Flask**.

El motor no utiliza inteligencia artificial, modelos de caja negra ni servicios de pago: todo el procesamiento es determinista, formal y local, modelando familias lingüísticas mediante **Expresiones Regulares y Lenguajes Regulares (Tipo 3 en la Jerarquía de Chomsky)**.

---

## 🗂️ Estructura Limpia del Proyecto

```text
detector-mensajes/
├── app.py              # Servidor Flask, expresiones regulares y motor de análisis
├── requirements.txt    # Dependencias mínimas del proyecto (Flask)
├── templates/
│   └── index.html      # Estructura visual de la app móvil y vistas didácticas
├── static/
│   ├── style.css       # Estilos simuladores de celular, componentes y animaciones
│   └── script.js       # Control de navegación móvil, llamadas fetch() y resaltado seguro
└── README.md           # Guía completa de instalación, teoría formal y exposición
```

---

## ⚙️ Requisitos e Instalación

### 1. Requisitos Previos
* **Python 3.10 o superior** instalado.

### 2. Abrir la Carpeta del Proyecto
```bash
cd "Proyecto App de Reconocimiento"
```

### 3. (Opcional) Entorno Virtual
```bash
# En Windows:
python -m venv venv
venv\Scripts\activate

# En Linux / macOS:
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

---

## 🚀 Ejecución de la Aplicación

1. Inicia el servidor Flask ejecutando:
   ```bash
   python app.py
   ```
2. Abre tu navegador web e ingresa a:  
   **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧩 Las 10 Familias de Expresiones Regulares Implementadas en Python

En lugar de memorizar oraciones fijas o listas rígidas, cada patrón modela una **familia de estructuras sintácticas** mediante operaciones formales:

| N° | Categoría (`id`) | Familia Lingüística Modelada | Expresión Regular en Python | Conceptos Teóricos SIS120 |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `urgencia` | Lenguaje de urgencia y presión para actuar | `r'\b(?:urgente(?:s)?\|urgencia\|inmediat[oa](?:mente)?\|de\s+inmediato\|hoy\|cuanto\s+antes\|a\s+la\s+brevedad\|act[uú](?:a\|e)\s+(?:ya\|ahora)\|[uú]ltimo\s+(?:aviso\|recordatorio\|plazo)\|plazo\s+l[ií]mite\|tiempo\s+l[ií]mite\|(?:vence\|expira)\s+(?:hoy\|pronto\|en\s+\d+\s*(?:horas?\|minutos?)))\b'` | **Unión formal ($L_1 \cup L_2$)** de adjetivos, adverbios y perífrasis de apremio; **clases de caracteres** con tildes (`[uú]`, `[ií]`). |
| **2** | `dinero` | Cantidades monetarias (Bolivianos / Bs) | `r'\b(?:(?:Bs\.?\|BOB)\s*[0-9]+(?:[.,][0-9]+)*\|[0-9]+(?:[.,][0-9]+)*\s*(?:Bs\.?\|BOB\|bolivianos?))\b'` | **Concatenación** de símbolo prefijo/sufijo y cadena numérica; **cerradura de Kleene (`*`)** sobre agrupaciones de miles y decimales. |
| **3** | `solicitud_datos` | Verificación o actualización de cuentas y datos | `r'\b(?:(?:confirm(?:a\|e\|ar)\|verific(?:a\|e\|ar)\|actualiz(?:a\|e\|ar)\|valid(?:a\|e\|ar)\|proporcion(?:a\|e\|ar)\|ingres(?:a\|e\|ar)\s+a\s+verificar\|reactiv(?:a\|e\|ar))\s+(?:de\s+nuevo\s+)?(?:(?:tu\|tus\|su\|sus\|el\|la)\s+)?(?:cuenta\|datos(?:\s+personales)?\|informaci[oó]n(?:\s+personal)?\|identidad\|credenciales\|perfil))\b'` | **Concatenación** de verbos de acción (imperativos/infinitivos) con sintagmas nominales y pronombres determinantes opcionales (`?`). |
| **4** | `enlaces` | Enlaces web y URLs | `r'https?://\S+\|www\.\S+'` | **Alternancia** de protocolos y prefijo www; cerradura positiva `\S+` sobre el alfabeto de la URL. |
| **5** | `exclamacion` | Exceso de signos de exclamación | `r'!{2,}\|¡{2,}'` | **Cuantificación acotada inferiormente (`{2,}`)** que exige dos o más repeticiones consecutivas sin cota superior. |
| **6** | `cuenta_bloqueada` | Cuentas o tarjetas canceladas, bloqueadas, cerradas, suspendidas, etc. | `r'\b(?:(?:cuenta\|tarjeta)s?(?:\s+(?:de\s+)?(?:cr[eé]dito\|d[eé]bito\|ahorros?\|bancaria\|corriente))?(?:\s+(?:ha\s+sido\|fue\|est[aá]\|qued[oó]\|ha\s+quedado\|se\s+encuentra))\s+(?:cancelad[oa]\|bloquead[oa]\|cerrad[oa]\|suspendid[oa]\|restringid[oa]\|inhabilitad[oa]\|desactivad[oa])s?\|(?:cuenta\|tarjeta)s?(?:\s+(?:de\s+)?(?:cr[eé]dito\|d[eé]bito\|ahorros?\|bancaria\|corriente))?\s+(?:cancelad[oa]\|bloquead[oa]\|cerrad[oa]\|suspendid[oa]\|restringid[oa]\|inhabilitad[oa]\|desactivad[oa])s?\|(?:cierre\|bloqueo\|suspensi[oó]n\|cancelaci[oó]n\|inhabilitaci[oó]n)\s+(?:de\s+(?:su\|tu)\s+)?(?:cuenta\|tarjeta)s?)\b'` | **Concatenación no rígida** que admite modificadores de producto ('tarjeta de crédito') y sintagmas verbales compuestos ('ha sido cancelada'). |
| **7** | `amenaza_bloqueo` | Amenazas de bloqueo, suspensión o pérdida de acceso | `r'\b(?:(?:tu\|su)\s+(?:cuenta\|tarjeta)s?(?:\s+(?:de\s+)?(?:cr[eé]dito\|d[eé]bito\|bancaria))?\s+(?:ser[aá]\|quedar[aá])\s+(?:bloquead[oa]\|suspendid[oa]\|cancelad[oa]\|inhabilitad[oa]\|cerrad[oa]\|restringid[oa])s?\|(?:ser[aá]\|quedar[aá]\|procederemos\s+a)\s+(?:bloquead[oa]\|suspendid[oa]\|cancelad[oa]\|inhabilitad[oa]\|cerrad[oa]\|restringid[oa])s?\|p[eé]rdida\s+de\s+acceso\|perder[aá]\s+(?:el\s+)?acceso\|evit(?:e\|ar)\s+(?:el\s+bloqueo\|la\s+suspensi[oó]n\|la\s+cancelaci[oó]n\|la\s+inhabilitaci[oó]n))\b'` | Modelado de **modalidad temporal futura** ('será bloqueada') y construcciones condicionales de coerción ('evite la suspensión'). |
| **8** | `actividad_inusual` | Actividad inusual, sospechosa o acceso no autorizado | `r'\b(?:actividad(?:es)?\s+(?:inusual(?:es)?\|sospechosa?s?\|no\s+reconocida?s?)\|acceso(?:s)?\s+(?:sospechoso(?:s)?\|no\s+autorizado(?:s)?\|inusual(?:es)?)\|movimiento(?:s)?\s+(?:inusual(?:es)?\|sospechoso(?:s)?\|no\s+autorizado(?:s)?)\|intento\s+de\s+acceso)\b'` | **Grupos de no captura anidados** para concordancia de número en sustantivos y adjetivos calificativos de seguridad. |
| **9** | `info_financiera` | Solicitudes de información financiera y datos personales | `r'\b(?:n[uú]mero\s+de\s+tarjeta\|fecha\s+de\s+vencimiento\|c[oó]digo\s+de\s+seguridad\|c[oó]digo\s+de\s+verificaci[oó]n\|n[uú]mero\s+de\s+seguro\s+social\|seguro\s+social\|cvv\|cvc\|clave\s+(?:secreta\|din[aá]mica\|de\s+acceso)\|pin\s+(?:de\s+seguridad)?\|datos\s+personales\|informaci[oó]n\s+financiera)\b'` | Unión de términos que denotan credenciales confidenciales de acceso fiduciario. |
| **10** | `correo_electronico` | Direcciones de correo electrónico (Informativo) | `r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'` | Expresión regular estándar de email; se define como **categoría informativa** que por sí sola no se considera prueba de estafa. |

---

## ⚖️ Regla de Clasificación Orientativa

Calculada en Python a partir del número de **categorías diferentes** detectadas:

- **0 categorías detectadas:**  
  🏷️ **«Sin indicadores detectados»**  
  *Recomendación:* No se detectaron los indicadores sintácticos definidos. La ausencia de coincidencias **no garantiza** que el mensaje sea seguro o legítimo; únicamente señala que no contiene los patrones sintácticos preconfigurados.

- **1 categoría detectada:**  
  🏷️ **«Revisar con precaución»**  
  *Recomendación:* El mensaje presenta un indicador aislado (ej. la palabra cotidiana "hoy", un enlace, una tarjeta cancelada en conversación normal o una dirección de correo informativa). Una categoría aislada no demuestra fraude. Se recomienda verificar el contexto y el remitente.

- **2 o más categorías distintas:**  
  🏷️ **«Mensaje sospechoso»**  
  *Recomendación:* El mensaje combina múltiples categorías concurrentes (ej. amenaza de bloqueo + solicitud de datos + urgencia). Este patrón compuesto es característico de ingeniería social.

> **Nota académica:** La clasificación es una demostración académica para la materia SIS120, basada en gramáticas regulares y autómatas finitos, no una prueba judicial de fraude.

---

## 🧪 Pruebas Verificadas en Consola

1. **«Su tarjeta de crédito ha sido cancelada, contáctese a este número 77747902 para reactivarla y siga los pasos»**  
   - Coincide: `cuenta_bloqueada` (`'tarjeta de crédito ha sido cancelada'`).  
   - Total categorías: **1** $\rightarrow$ **«Revisar con precaución»** (No se marca indiscriminadamente como estafa confirmada).
2. **«Mi tarjeta de crédito está cancelada desde hace meses y ya fui al banco»**  
   - Coincide: `cuenta_bloqueada` (`'tarjeta de crédito está cancelada'`).  
   - Total categorías: **1** $\rightarrow$ **«Revisar con precaución»**.
3. **«Mañana tengo una reunión normal en la universidad»**  
   - Coincide: Ninguna.  
   - Total categorías: **0** $\rightarrow$ **«Sin indicadores detectados»**.
4. **«Tu cuenta será bloqueada; verifica tus datos inmediatamente»**  
   - Coinciden: `amenaza_bloqueo` (`'Tu cuenta será bloqueada'`), `solicitud_datos` (`'verifica tus datos'`), `urgencia` (`'inmediatamente'`).  
   - Total categorías: **3** $\rightarrow$ 🚨 **«Mensaje sospechoso»**.
5. **«Aviso: su cuenta bancaria cerrada por actividad inusual. Envíe su número de tarjeta, fecha de vencimiento y número de seguro social a soporte@banco-alerta.com»**  
   - Coinciden: `cuenta_bloqueada`, `actividad_inusual`, `info_financiera`, `correo_electronico`.  
   - Total categorías: **4** $\rightarrow$ 🚨 **«Mensaje sospechoso»**.
6. **«URGENTE: ganaste Bs 5000. Verifica tus datos hoy!!»**  
   - Coinciden: `urgencia`, `dinero`, `solicitud_datos`, `exclamacion`.  
   - Total categorías: **4** $\rightarrow$ 🚨 **«Mensaje sospechoso»**.

---

## 🎓 Fundamento Teórico SIS120

- **Operaciones Regulares:** Toda expresión regular en el motor se construye recursivamente a partir del alfabeto $\Sigma$ mediante tres operaciones fundamentales cerradas:
  1. **Unión ($L_1 \cup L_2$):** Representada por el operador `|` en grupos `(?:...)`.
  2. **Concatenación ($L_1 \cdot L_2$):** Secuencia directa de subexpresiones (ej. verbo + pronombre + sustantivo).
  3. **Cerradura de Kleene ($L^*$ y $L^+$):** Repetición de cero o más (`*`), o una o más (`+`) instancias (ej. espacios `\s+`, dígitos `[0-9]+`).
- **Teorema de Kleene y Autómatas Equivalentes:** Por el Teorema de Kleene, para cada una de estas 10 expresiones regulares existe un **Autómata Finito No Determinista con transiciones épsilon (AFND-$\epsilon$)** construible mediante el algoritmo de Thompson, el cual puede transformarse en un **Autómata Finito Determinista (AFD)** mínimo por el método de construcción de subconjuntos. Python compila estas expresiones internamente a un autómata que procesa las cadenas en tiempo lineal $O(n)$ respecto a la longitud del texto.
