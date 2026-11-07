"""Funciones comunes de la Parte 1 (visión sobre imágenes del dominio).

Sigue el mismo patrón de multimodal.py del repositorio de clase:
la imagen local se lee, se codifica en base64 y se envía en un HumanMessage
cuyo contenido es una lista de bloques (texto + imagen).

Hay dos conjuntos de imágenes:
    imagenes/creadas/  imágenes ficticias generadas con generar_imagenes.py
    imagenes/reales/   fotos y documentos reales (ver imagenes/reales/FUENTES.md)
Cada script usa "creadas" por defecto y "reales" si se ejecuta con --reales.
"""

import base64
import mimetypes
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import RateLimitError
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

load_dotenv()  # busca el archivo .env en esta carpeta y en las carpetas superiores

CARPETA = Path(__file__).parent
CARPETA_IMAGENES = CARPETA / "imagenes"
CARPETA_RESULTADOS = CARPETA / "resultados"

MODELO_VISION = os.getenv("VISION_MODEL", "qwen/qwen3.8-27b")
MODELO_SIN_VISION = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")


def conjunto_elegido():
    """'reales' si el script se ejecutó con --reales; si no, 'creadas'."""
    return "reales" if "--reales" in sys.argv else "creadas"


def cargar_llm(model_name=None, temperature=0, **kwargs):
    """Crea el cliente de Groq (LangChain). Por defecto usa el modelo con visión."""
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit(
            "Falta la variable GROQ_API_KEY. Créala en un archivo .env en la raíz del "
            "repositorio (ver .env.example)."
        )
    kwargs.setdefault("max_tokens", 4096)
    if (model_name or MODELO_VISION) == MODELO_VISION:
        kwargs.setdefault("reasoning_effort", "low")
    return ChatGroq(model=model_name or MODELO_VISION, temperature=temperature, **kwargs)


def ruta_imagen(nombre, conjunto="creadas"):
    ruta = CARPETA_IMAGENES / conjunto / nombre
    if not ruta.exists():
        pista = "python generar_imagenes.py" if conjunto == "creadas" else "imagenes/reales/FUENTES.md"
        raise SystemExit(f"No existe {ruta}. Revisa: {pista}")
    return ruta


def mime_de(ruta):
    mime, _ = mimetypes.guess_type(str(ruta))
    return mime or "application/octet-stream"


def imagen_a_base64(ruta):
    return base64.b64encode(Path(ruta).read_bytes()).decode("utf-8")


def bloque_imagen(ruta, mime_type=None):
    """Bloque de imagen en base64, igual que en multimodal.py."""
    return {
        "type": "image",
        "base64": imagen_a_base64(ruta),
        "mime_type": mime_type or mime_de(ruta),
    }


def mensaje_con_imagenes(texto, rutas):
    """HumanMessage con un bloque de texto seguido de uno o varios bloques de imagen."""
    return HumanMessage(content=[{"type": "text", "text": texto}] + [bloque_imagen(r) for r in rutas])


def texto_respuesta(response):
    """Extrae el texto de la respuesta y quita el razonamiento <think>...</think> si viene."""
    contenido = response.content
    if isinstance(contenido, list):
        contenido = "".join(b.get("text", "") for b in contenido if isinstance(b, dict))
    return re.sub(r"<think>.*?</think>", "", contenido, flags=re.DOTALL).strip()


def llamar_con_reintentos(llm, mensajes, intentos=4):
    """llm.invoke con reintentos si Groq responde 429 (límite de tokens por minuto).

    El plan gratuito permite 7.000 tokens de entrada por minuto y cada imagen cuenta
    como ~2.000 tokens, así que dos solicitudes seguidas con 3 imágenes lo superan.
    """
    for intento in range(1, intentos + 1):
        try:
            return llm.invoke(mensajes)
        except RateLimitError as e:
            if intento == intentos:
                raise
            espera = re.search(r"try again in ([\d.]+)s", str(e))
            segundos = float(espera.group(1)) + 1 if espera else 20.0
            print(f"   [429 límite de tokens por minuto; reintento {intento} en {segundos:.0f} s]")
            time.sleep(segundos)


def invocar(llm, mensaje):
    """Envía el mensaje y devuelve (texto, segundos, tokens de entrada, tokens de salida)."""
    inicio = time.perf_counter()
    response = llamar_con_reintentos(llm, [mensaje])
    segundos = time.perf_counter() - inicio
    uso = response.usage_metadata or {}
    return texto_respuesta(response), segundos, uso.get("input_tokens"), uso.get("output_tokens")


def describir_imagen(ruta):
    """Datos de la imagen que se muestran en consola antes de enviarla."""
    from PIL import Image

    with Image.open(ruta) as img:
        ancho, alto = img.size
    tam_kb = Path(ruta).stat().st_size / 1024
    b64_kb = len(imagen_a_base64(ruta)) / 1024
    return (f"{Path(ruta).name} | {ancho}x{alto} px | {tam_kb:.0f} KB "
            f"({b64_kb:.0f} KB en base64) | {mime_de(ruta)}")


def titulo(texto):
    print("\n" + "=" * 78)
    print(texto)
    print("=" * 78)


def guardar(nombre, contenido, conjunto="creadas"):
    carpeta = CARPETA_RESULTADOS / conjunto
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / nombre
    ruta.write_text(contenido, encoding="utf-8")
    return ruta
