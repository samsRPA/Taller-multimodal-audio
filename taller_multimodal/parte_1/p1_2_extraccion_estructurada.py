"""1.2 Extracción estructurada.

1. Define un esquema (Pydantic) con 7 campos útiles para verificar un comparendo.
2. Pide al modelo que extraiga esos campos de 3 imágenes de comparendos, en JSON.
3. Valida el JSON en el código: si no es JSON o no cumple el esquema, el programa
   lo informa y sigue con la siguiente imagen (no se detiene con una excepción).
4. Compara campo por campo con los valores reales (imagenes/<conjunto>/valores_reales.json,
   lo que una persona lee en la imagen) y reporta el porcentaje de aciertos.

Uso:
    python p1_2_extraccion_estructurada.py            # 3 comparendos creados
    python p1_2_extraccion_estructurada.py --reales   # comparendo real + evidencia de la cámara
"""

import json
import re
import unicodedata
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from comun import (CARPETA_IMAGENES, MODELO_VISION, cargar_llm, conjunto_elegido,
                   describir_imagen, guardar, invocar, mensaje_con_imagenes, ruta_imagen, titulo)

IMAGENES = {
    "creadas": ["comparendo_01.png", "comparendo_02.png", "comparendo_03_foto.jpg"],
    # Solo se encontraron 2 documentos reales públicos del mismo comparendo (ver FUENTES.md)
    "reales": ["comparendo_real_la_dorada.png", "evidencia_fotomulta_la_dorada.png"],
}


# ---------------------------------------------------------------------------
# Esquema
# ---------------------------------------------------------------------------
class Comparendo(BaseModel):
    """Datos mínimos para verificar una orden de comparendo.

    Todas las claves son obligatorias, pero pueden valer null si el dato no aparece.
    """

    model_config = ConfigDict(extra="forbid")

    numero_comparendo: str | None = Field(
        pattern=r"^\d{20}$",
        description="Número de la orden de comparendo: 20 dígitos, sin espacios.")
    fecha_infraccion: date | None = Field(
        description="Fecha de la infracción en formato YYYY-MM-DD.")
    hora_infraccion: str | None = Field(
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Hora de la infracción en formato HH:MM (24 horas).")
    placa_vehiculo: str | None = Field(
        pattern=r"^[A-Z]{3}\d{2}[A-Z0-9]$",
        description="Placa del vehículo: 3 letras y 3 caracteres (ej. ABC123 o ABC12D), sin espacios.")
    tipo_vehiculo: Literal["automovil", "motocicleta", "camioneta", "bus", "camion", "otro"] | None = Field(
        description="Tipo de vehículo marcado con X, en minúsculas y sin tildes.")
    codigo_infraccion: str | None = Field(
        pattern=r"^[A-I]\d{2}$",
        description="Código de la infracción: una letra y dos dígitos, sin punto (ej. C29).")
    placa_agente: str | None = Field(
        pattern=r"^\d{3,7}$",
        description="Número de placa del agente de tránsito, como texto (conserva ceros a la izquierda).")


CAMPOS = list(Comparendo.model_fields)


def describir_esquema():
    lineas = []
    for nombre, campo in Comparendo.model_fields.items():
        tipo = "string (fecha)" if nombre == "fecha_infraccion" else "string"
        if nombre == "tipo_vehiculo":
            tipo = "string (uno de: automovil, motocicleta, camioneta, bus, camion, otro)"
        lineas.append(f'- "{nombre}" ({tipo} o null): {campo.description}')
    return "\n".join(lineas)


PROMPT = (
    "Eres un sistema de extracción de datos de órdenes de comparendo de tránsito de Colombia.\n"
    "Lee la imagen y devuelve ÚNICAMENTE un objeto JSON (sin texto adicional y sin bloques "
    "de código) con exactamente estas claves:\n"
    f"{describir_esquema()}\n"
    "Si un dato no aparece o no se puede leer, usa null. No inventes valores."
)


# ---------------------------------------------------------------------------
# Validación: nunca lanza excepción, devuelve los problemas encontrados
# ---------------------------------------------------------------------------
def parsear_json(texto):
    """Devuelve (dict, None) si el texto contiene un objeto JSON, o (None, error)."""
    limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip())
    inicio, fin = limpio.find("{"), limpio.rfind("}")
    if inicio == -1 or fin == -1:
        return None, "La respuesta no contiene un objeto JSON."
    try:
        datos = json.loads(limpio[inicio:fin + 1])
    except json.JSONDecodeError as e:
        return None, f"JSON mal formado: {e}"
    if not isinstance(datos, dict):
        return None, "El JSON no es un objeto."
    return datos, None


def validar_esquema(datos):
    """Devuelve (Comparendo, []) si cumple el esquema, o (None, [errores])."""
    try:
        return Comparendo.model_validate(datos), []
    except ValidationError as e:
        errores = []
        for err in e.errors():
            campo = ".".join(str(p) for p in err["loc"]) or "(objeto)"
            if err["type"] == "missing":
                errores.append(f"{campo}: falta el campo")
            else:
                errores.append(f"{campo}: {err['msg']} (valor recibido: {err.get('input')!r})")
        return None, errores


# ---------------------------------------------------------------------------
# Comparación con los valores reales
# ---------------------------------------------------------------------------
def normalizar(campo, valor):
    """Normaliza solo la presentación (mayúsculas, tildes, espacios); no corrige dígitos."""
    if valor is None:
        return ""
    v = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode()
    v = v.strip().upper()
    if campo in ("placa_vehiculo", "codigo_infraccion"):
        v = re.sub(r"[\s.\-]", "", v)
    return re.sub(r"\s+", " ", v)


def comparar(extraido, real):
    filas = []
    for campo in CAMPOS:
        valor = extraido.get(campo) if extraido else None
        filas.append({
            "campo": campo,
            "real": real[campo],
            "extraido": valor,
            "correcto": normalizar(campo, valor) == normalizar(campo, real[campo]),
        })
    return filas


def procesar_respuesta(texto):
    """Parsea y valida una respuesta. Devuelve (datos, valido, problemas)."""
    datos, error = parsear_json(texto)
    if error:
        return None, False, [error]
    _, errores = validar_esquema(datos)
    return datos, not errores, errores


def demo_validador():
    """Muestra que el validador informa (sin fallar) cuando un JSON no cumple el esquema."""
    titulo("PRUEBA DEL VALIDADOR CON RESPUESTAS INVÁLIDAS (simuladas, no vienen del modelo)")
    ejemplos = {
        "texto que no es JSON": "Lo siento, no puedo leer la imagen.",
        "JSON incompleto y con formatos erróneos": json.dumps({
            "numero_comparendo": 11001000000045872310,
            "fecha_infraccion": "14/10/2026",
            "hora_infraccion": "7:42 am",
            "placa_vehiculo": "KTR-482",
            "tipo_vehiculo": "Automóvil",
            "codigo_infraccion": "C.29",
        }, ensure_ascii=False),
    }
    for nombre, texto in ejemplos.items():
        _, valido, problemas = procesar_respuesta(texto)
        print(f"\n> {nombre}: {texto[:90]}")
        print(f"  ¿Cumple el esquema? {'Sí' if valido else 'No'}")
        for p in problemas:
            print(f"   - {p}")


def main():
    conjunto = conjunto_elegido()
    reales = json.loads((CARPETA_IMAGENES / conjunto / "valores_reales.json").read_text(encoding="utf-8"))
    llm = cargar_llm()

    titulo(f"1.2 EXTRACCIÓN ESTRUCTURADA (imágenes {conjunto})")
    print(f"Modelo : {MODELO_VISION}")
    print(f"\nPrompt enviado con cada imagen:\n{PROMPT}")

    resultados, todas_filas = [], []
    for nombre in IMAGENES[conjunto]:
        ruta = ruta_imagen(nombre, conjunto)
        titulo(f"Imagen: {describir_imagen(ruta)}")
        try:
            texto, segundos, tok_in, tok_out = invocar(llm, mensaje_con_imagenes(PROMPT, [ruta]))
        except Exception as e:  # error de red o de la API: se informa y se sigue
            print(f"ERROR al llamar a la API: {type(e).__name__}: {e}")
            texto, segundos, tok_in, tok_out = "", 0.0, None, None

        print(f"Respuesta cruda ({segundos:.1f} s):\n{texto}")
        datos, valido, problemas = procesar_respuesta(texto)
        if valido:
            print("\nValidación: el JSON CUMPLE el esquema.")
        else:
            print("\nValidación: el JSON NO cumple el esquema:")
            for p in problemas:
                print(f"   - {p}")

        filas = comparar(datos, reales[nombre])
        aciertos = sum(f["correcto"] for f in filas)
        print(f"\n{'Campo':<20} {'Valor real':<24} {'Valor extraído':<24} ¿Correcto?")
        for f in filas:
            print(f"{f['campo']:<20} {str(f['real']):<24} {str(f['extraido']):<24} "
                  f"{'Sí' if f['correcto'] else 'No'}")
        print(f"Aciertos en esta imagen: {aciertos}/{len(filas)}")

        for f in filas:
            todas_filas.append({"imagen": nombre, **f})
        resultados.append({
            "imagen": nombre, "respuesta_cruda": texto, "json": datos,
            "cumple_esquema": valido, "problemas_validacion": problemas,
            "aciertos": aciertos, "total": len(filas),
            "segundos": round(segundos, 2), "tokens_entrada": tok_in, "tokens_salida": tok_out,
        })

    total = len(todas_filas)
    aciertos = sum(f["correcto"] for f in todas_filas)
    porcentaje = 100 * aciertos / total if total else 0.0
    titulo(f"PORCENTAJE DE ACIERTOS: {aciertos} de {total} campos = {porcentaje:.1f} %")
    for r in resultados:
        print(f"{r['imagen']:<26} {r['aciertos']}/{r['total']}  "
              f"esquema: {'OK' if r['cumple_esquema'] else 'NO CUMPLE'}")

    demo_validador()

    guardar("1_2_extraccion.json", json.dumps({
        "conjunto": conjunto, "modelo": MODELO_VISION, "prompt": PROMPT,
        "esquema": Comparendo.model_json_schema(),
        "resultados": resultados, "comparacion": todas_filas,
        "aciertos": aciertos, "total": total, "porcentaje": round(porcentaje, 1),
    }, ensure_ascii=False, indent=2, default=str), conjunto)

    tabla = ["| Imagen | Campo | Valor real | Valor extraído | ¿Correcto? |",
             "|---|---|---|---|---|"]
    tabla += [f"| {f['imagen']} | {f['campo']} | {f['real']} | {f['extraido']} | "
              f"{'Sí' if f['correcto'] else 'No'} |" for f in todas_filas]
    salida = guardar("1_2_tabla_aciertos.md",
                     f"# 1.2 Tabla de aciertos (imágenes {conjunto})\n\n" + "\n".join(tabla) +
                     f"\n\n**Porcentaje de aciertos:** {aciertos} de {total} campos = "
                     f"{porcentaje:.1f} %\n", conjunto)
    print(f"\nResultados guardados en {salida.relative_to(salida.parents[2]).parent}/")


if __name__ == "__main__":
    main()
