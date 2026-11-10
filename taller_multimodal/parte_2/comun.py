"""Funciones comunes de la Parte 2 (audio y transcripción).

Sigue la idea de audio_input.py del repositorio de clase: el archivo de audio se
envía a Whisper (en Groq) y el texto transcrito se pasa a un modelo de lenguaje.

Los audios y sus datos (quién habla, con o sin ruido, qué se dijo) están en
audios/audios.json.
"""

import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq, RateLimitError
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

load_dotenv()  # busca el archivo .env en esta carpeta y en las carpetas superiores

CARPETA = Path(__file__).parent
CARPETA_AUDIOS = CARPETA / "audios"
CARPETA_RESULTADOS = CARPETA / "resultados"
ARCHIVO_AUDIOS = CARPETA_AUDIOS / "audios.json"
ARCHIVO_TRANSCRIPCIONES = CARPETA_RESULTADOS / "2_1_transcripciones.json"

MODELO_AUDIO = os.getenv("AUDIO_MODEL", "whisper-large-v3-turbo")
MODELO_LLM = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")

LIMITE_MB = 25  # límite de archivo en el plan gratuito de Groq


def exigir_clave():
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit(
            "Falta la variable GROQ_API_KEY. Créala en un archivo .env en la raíz del "
            "repositorio (ver .env.example)."
        )


def cargar_audios():
    """Lee audios/audios.json y comprueba que cada archivo exista y no pase el límite."""
    if not ARCHIVO_AUDIOS.exists():
        raise SystemExit(f"No existe {ARCHIVO_AUDIOS}.")
    audios = json.loads(ARCHIVO_AUDIOS.read_text(encoding="utf-8"))
    disponibles = []
    for a in audios:
        ruta = CARPETA_AUDIOS / a["archivo"]
        if not ruta.exists():
            print(f"[aviso] Todavía no está {ruta.name}; se omite (guion en audios/GUION.md).")
            continue
        mb = ruta.stat().st_size / (1024 * 1024)
        if mb > LIMITE_MB:
            raise SystemExit(f"{ruta.name} pesa {mb:.1f} MB y el límite es {LIMITE_MB} MB.")
        disponibles.append(a)
    if not disponibles:
        raise SystemExit(f"No hay audios en {CARPETA_AUDIOS}.")
    audios = disponibles
    return audios


def cliente_groq():
    exigir_clave()
    return Groq()


def transcribir(cliente, ruta, idioma="es", intentos=3):
    """Transcribe un archivo con Whisper. Devuelve (texto, duración en segundos)."""
    for intento in range(1, intentos + 1):
        try:
            with open(ruta, "rb") as f:
                r = cliente.audio.transcriptions.create(
                    file=(Path(ruta).name, f.read()),
                    model=MODELO_AUDIO,
                    language=idioma,
                    response_format="verbose_json",
                    temperature=0,
                )
            return r.text.strip(), getattr(r, "duration", None)
        except RateLimitError as e:
            if intento == intentos:
                raise
            espera = re.search(r"try again in ([\d.]+)s", str(e))
            segundos = float(espera.group(1)) + 1 if espera else 15.0
            print(f"   [429 límite de uso; reintento {intento} en {segundos:.0f} s]")
            time.sleep(segundos)


def normalizar(texto):
    """Minúsculas, sin signos ni tildes, para comparar lo dicho con lo transcrito."""
    texto = texto.lower()
    for a, b in zip("áéíóúü", "aeiouu"):
        texto = texto.replace(a, b)
    return re.sub(r"[^a-z0-9ñ ]+", " ", texto).split()


def tasa_error_palabras(referencia, hipotesis):
    """WER: (sustituciones + inserciones + borrados) / palabras de la referencia."""
    ref, hip = normalizar(referencia), normalizar(hipotesis)
    if not ref:
        return None
    previa = list(range(len(hip) + 1))
    for i, r in enumerate(ref, 1):
        actual = [i]
        for j, h in enumerate(hip, 1):
            actual.append(min(previa[j] + 1, actual[j - 1] + 1, previa[j - 1] + (r != h)))
        previa = actual
    return previa[-1] / len(ref)


def cargar_llm():
    exigir_clave()
    return ChatGroq(model=MODELO_LLM, temperature=0, max_tokens=2048, reasoning_effort="low")


def texto_respuesta(response):
    contenido = response.content
    if isinstance(contenido, list):
        contenido = "".join(b.get("text", "") for b in contenido if isinstance(b, dict))
    return re.sub(r"<think>.*?</think>", "", contenido, flags=re.DOTALL).strip()


def responder(llm, sistema, pregunta, intentos=3):
    for intento in range(1, intentos + 1):
        try:
            r = llm.invoke([SystemMessage(content=sistema), HumanMessage(content=pregunta)])
            return texto_respuesta(r)
        except RateLimitError as e:
            if intento == intentos:
                raise
            espera = re.search(r"try again in ([\d.]+)s", str(e))
            time.sleep(float(espera.group(1)) + 1 if espera else 15.0)


def titulo(texto):
    print("\n" + "=" * 78)
    print(texto)
    print("=" * 78)


def guardar(nombre, contenido):
    CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_RESULTADOS / nombre
    ruta.write_text(contenido, encoding="utf-8")
    return ruta
