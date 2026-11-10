# Taller: entrada multimodal y audio

**Asignatura:** Desarrollo de Aplicaciones con IA
**Dominio:** MultaClara, un asistente para verificar comparendos de tránsito en Colombia.
**Integrantes:** Samuel Alejandro Monsalve Sarmiento, Carlos Alberto Franco Hernández

Este repositorio contiene la carpeta `taller_multimodal/`. La **Parte 1 (visión)** usa un modelo con visión de Groq para leer imágenes del dominio (comparendos, normas y señales de tránsito). La **Parte 2 (audio)** transcribe con Whisper preguntas habladas sobre comparendos y se las pasa a un modelo de lenguaje para que responda.

Base: los ejemplos `multimodal.py` y `audio_input.py` del repositorio de clase [lpajarof/tools_rags](https://github.com/lpajarof/tools_rags).

## Estructura

```
taller_multimodal/
├── requirements.txt
├── parte_1/
│   ├── comun.py                         # carga del modelo, imagen → base64, reintentos, utilidades
│   ├── generar_imagenes.py              # crea las imágenes de imagenes/creadas/
│   ├── p1_1_pregunta_imagen.py          # 1.1 pregunta sobre una imagen
│   ├── p1_2_extraccion_estructurada.py  # 1.2 extracción a JSON + validación + % de aciertos
│   ├── p1_3_varias_imagenes.py          # 1.3 tres imágenes en una solicitud
│   ├── p1_4_error_provocado.py          # 1.4 errores provocados de la API
│   ├── imagenes/
│   │   ├── creadas/                     # imágenes ficticias + valores_reales.json
│   │   └── reales/                      # documentos y fotos reales + valores_reales.json + FUENTES.md
│   └── resultados/
│       ├── creadas/                     # salida de cada script con imágenes creadas
│       └── reales/                      # salida de cada script con imágenes reales
└── parte_2/
    ├── comun.py                         # cliente de Groq, transcripción, WER, reintentos
    ├── p2_1_transcripcion.py            # 2.1 transcripción de cada audio con Whisper
    ├── p2_2_respuesta.py                # 2.2 audio → transcripción → respuesta del modelo
    ├── audios/                          # los 4 audios + audios.json (hablante, ruido, texto dicho) + GUION.md
    └── resultados/                      # salida de 2.1 y 2.2
```

Cada script corre con las imágenes **creadas** por defecto y con las **reales** si se agrega `--reales`.

### Imágenes creadas (`imagenes/creadas/`)

Son ficticias: tienen marca de agua y no corresponden a personas reales. Se generan con `generar_imagenes.py`. Como los datos los inventamos nosotros, sabemos el valor exacto de cada campo.

| Imagen | Contenido | Dificultad |
|---|---|---|
| `comparendo_01.png` | Comparendo impreso (Bogotá, C29) | Baja: texto impreso y limpio |
| `comparendo_02.png` | Comparendo diligenciado a mano (Medellín, C02) | Media: letra manuscrita |
| `comparendo_03_foto.jpg` | Foto de un comparendo (Cali, D02) | Alta: girado, borroso, con sombra |
| `norma_art131.png` | Fragmento escaneado del art. 131 de la Ley 769 de 2002 | Texto escaneado con ruido |
| `senal_velocidad_30.png` | Señal de 30 km/h en zona escolar | Imagen gráfica |

### Imágenes reales (`imagenes/reales/`)

Fuentes, autores y licencias en [`FUENTES.md`](taller_multimodal/parte_1/imagenes/reales/FUENTES.md).

| Imagen | Contenido |
|---|---|
| `comparendo_real_la_dorada.png` | Orden de Comparendo Único Nacional real, en el formato oficial de casillas (fotodetección, La Dorada, 2021). Viene de un expediente judicial público y tiene los datos personales tapados |
| `evidencia_fotomulta_la_dorada.png` | Hoja de evidencia de la cámara del mismo comparendo, con los datos personales tapados |
| `norma_ley769_pag91.png` | Página 91 del PDF oficial de la Ley 769 de 2002 |
| `senal_*.jpg` (4) | Fotos de señales reales en Colombia (Wikimedia Commons, CC BY / CC BY-SA) |

## Requisitos

- Python 3.10 o superior.
- Una clave de [Groq](https://console.groq.com).

```bash
python -m venv .venv
source .venv/bin/activate            # en Windows: .venv\Scripts\activate
pip install -r taller_multimodal/requirements.txt
```

## Variables de entorno

Copia `.env.example` como `.env` en la raíz del repositorio y pon tu clave:

| Variable | Obligatoria | Valor por defecto | Uso |
|---|---|---|---|
| `GROQ_API_KEY` | Sí | — | Clave de la API de Groq |
| `VISION_MODEL` | No | `qwen/qwen3.8-27b` | Modelo con visión (1.1 a 1.4) |
| `LLM_MODEL` | No | `openai/gpt-oss-20b` | Modelo sin visión: provoca un error en 1.4 y responde en 2.2 |
| `AUDIO_MODEL` | No | `whisper-large-v3-turbo` | Modelo de transcripción (2.1 y 2.2) |

El `.env` está en el `.gitignore`. No hay claves en el código ni en el historial.

## Cómo ejecutar la Parte 1

```bash
cd taller_multimodal/parte_1

python p1_1_pregunta_imagen.py                   # 1.1 con imagen creada
python p1_1_pregunta_imagen.py --reales          # 1.1 con imagen real
python p1_2_extraccion_estructurada.py           # 1.2 con 3 comparendos creados
python p1_2_extraccion_estructurada.py --reales  # 1.2 con el comparendo real y su evidencia
python p1_3_varias_imagenes.py                   # 1.3 con imágenes creadas
python p1_3_varias_imagenes.py --reales          # 1.3 con imágenes reales
python p1_4_error_provocado.py                   # 1.4 errores con imágenes creadas
python p1_4_error_provocado.py --reales          # 1.4 errores con imágenes reales
python p1_4_error_provocado.py --grande          # 1.4 incluye una imagen de más de 20 MB (sube ~27 MB)

python generar_imagenes.py                       # (opcional) regenera las imágenes creadas
```

Todos los scripts corren de principio a fin sin pedir datos por consola. Cada uno imprime la pregunta, las imágenes enviadas y la respuesta, y guarda el resultado en `resultados/creadas/` o `resultados/reales/`.

El plan gratuito de Groq permite 7.000 tokens de entrada por minuto, y cada imagen cuenta como unos 2.000. Si una solicitud supera ese límite (error 429), `comun.py` espera el tiempo que indica la API y reintenta.

## Cómo ejecutar la Parte 2

```bash
cd taller_multimodal/parte_2

python p2_1_transcripcion.py   # 2.1 transcribe los 4 audios y calcula el error de palabras (WER)
python p2_2_respuesta.py       # 2.2 transcribe y pasa el texto al modelo para que responda
```

Los audios están en `parte_2/audios/` y los datos de cada uno (quién habla, si tiene ruido y el texto que se leyó) en `audios.json`. El texto de cada audio está en `audios/GUION.md`. Los resultados quedan en `parte_2/resultados/`.

### Qué hace cada punto

- **1.1 Pregunta sobre una imagen.** Envía la norma en base64 (como en `multimodal.py`). Pregunta qué sanciona el código C.38, cuánto vale la multa del literal C y si procede un C.38 cuando el conductor usaba manos libres. La página real no muestra el valor de la multa del literal C, así que sirve para ver si el modelo lo inventa.
- **1.2 Extracción estructurada.** El esquema `Comparendo` (Pydantic) tiene 7 campos: `numero_comparendo`, `fecha_infraccion`, `hora_infraccion`, `placa_vehiculo`, `tipo_vehiculo`, `codigo_infraccion` y `placa_agente`. Todos son obligatorios y aceptan `null`. El modelo responde en JSON. El código lo valida en dos pasos: primero que sea JSON (`json.loads`) y luego que cumpla el esquema (`Comparendo.model_validate`). Si falla, informa qué campo falla y sigue con la siguiente imagen. Después compara cada campo con `valores_reales.json` y calcula el porcentaje de aciertos. Al final hay una prueba del validador con respuestas inválidas simuladas.
- **1.3 Varias imágenes.** Envía 3 imágenes (el máximo permitido) y pide un análisis conjunto. Con las creadas: comparendo, señal y norma. Con las reales: comparendo, evidencia de la cámara y norma, para comparar los datos entre documentos.
- **1.4 Error provocado.** Prueba tres casos: 4 imágenes, modelo sin visión y tipo MIME mal declarado. Cada caso va en un `try/except` que muestra el código HTTP y el mensaje de la API.
- **2.1 Transcripción desde archivo.** Lee `audios.json`, envía cada archivo a `whisper-large-v3-turbo` en español y muestra lo que se dijo, la transcripción, la duración y el WER (porcentaje de palabras mal transcritas, sin contar tildes ni signos).
- **2.2 Respuesta a partir de la transcripción.** Repite la transcripción y envía el texto a `openai/gpt-oss-20b` con un mensaje de sistema que lo presenta como el asistente MultaClara. Guarda pregunta y respuesta de cada audio.

## Límites del modelo de visión (Groq, `qwen/qwen3.8-27b`)

- Máximo 3 imágenes por solicitud.
- Máximo 20 MB por solicitud.
- Cada imagen cuenta como 2.048 tokens de entrada.

## Límites del audio (Groq, Whisper)

- Archivos de hasta 25 MB en el plan gratuito (wav, mp3, m4a, ogg, webm, entre otros).
- Cada solicitud se cobra como mínimo por 10 segundos de audio.
