# Taller: entrada multimodal y audio

**Asignatura:** Desarrollo de Aplicaciones con IA
**Dominio:** MultaClara, un asistente para verificar comparendos de tránsito en Colombia.
**Integrantes:** Samuel Alejandro Monsalve Sarmiento, Carlos Alberto Franco Hernández

Base: los ejemplos `multimodal.py` y `audio_input.py` de [lpajarof/tools_rags](https://github.com/lpajarof/tools_rags).

- **Parte 1 (visión):** un modelo con visión de Groq lee comparendos, normas y señales de tránsito.
- **Parte 2 (audio):** Whisper transcribe preguntas habladas y un modelo de lenguaje las responde.

El informe está en `Taller_multimodal_y_audio_informe.docx`.

## Estructura

```
taller_multimodal/
├── requirements.txt
├── parte_1/   # scripts p1_1 a p1_4, imagenes/ (creadas y reales) y resultados/
└── parte_2/   # scripts p2_1 y p2_2, audios/ (4 audios + audios.json) y resultados/
```

Las fuentes y licencias de las imágenes reales están en [`FUENTES.md`](taller_multimodal/parte_1/imagenes/reales/FUENTES.md). El texto que se leyó en cada audio está en `parte_2/audios/GUION.md`.

## Requisitos

Python 3.10 o superior y una clave de [Groq](https://console.groq.com).

```bash
python -m venv .venv
source .venv/bin/activate            # en Windows: .venv\Scripts\activate
pip install -r taller_multimodal/requirements.txt
```

## Variables de entorno

Copia `.env.example` como `.env` en la raíz y pon tu clave. El `.env` está en el `.gitignore`.

| Variable | Obligatoria | Valor por defecto | Uso |
|---|---|---|---|
| `GROQ_API_KEY` | Sí | Ninguno | Clave de la API de Groq |
| `VISION_MODEL` | No | `qwen/qwen3.8-27b` | Modelo con visión (Parte 1) |
| `LLM_MODEL` | No | `openai/gpt-oss-20b` | Modelo sin visión: provoca un error en 1.4 y responde en 2.2 |
| `AUDIO_MODEL` | No | `whisper-large-v3-turbo` | Transcripción de audio (Parte 2) |

## Cómo ejecutar

Todos los scripts corren de principio a fin, sin pedir datos, y guardan su salida en `resultados/`.

```bash
cd taller_multimodal/parte_1
python p1_1_pregunta_imagen.py        # 1.1 pregunta sobre una imagen
python p1_2_extraccion_estructurada.py # 1.2 extracción a JSON, validación y % de aciertos
python p1_3_varias_imagenes.py        # 1.3 tres imágenes en una solicitud
python p1_4_error_provocado.py        # 1.4 errores provocados de la API
```

Cada script de la Parte 1 usa las imágenes creadas por defecto y las reales con `--reales`. El 1.4 también acepta `--grande`, que sube una imagen de unos 27 MB.

```bash
cd taller_multimodal/parte_2
python p2_1_transcripcion.py          # 2.1 transcripción de los 4 audios y error de palabras (WER)
python p2_2_respuesta.py              # 2.2 audio, transcripción y respuesta del modelo
```

El plan gratuito de Groq limita los tokens por minuto. Si responde 429, los scripts esperan lo que indica la API y reintentan.
