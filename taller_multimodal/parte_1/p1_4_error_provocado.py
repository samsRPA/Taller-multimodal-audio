"""1.4 Error provocado.

Provoca a propósito errores de la API de visión y muestra el mensaje que devuelve:

    mas_imagenes        4 imágenes en una solicitud (el límite es 3)
    modelo_sin_vision   una imagen enviada a un modelo que solo recibe texto
    tipo_mal_declarado  una imagen JPEG declarada con un tipo MIME que no es de imagen
    imagen_grande       una imagen de más de 20 MB (solo con --grande; sube ~27 MB)

Cada caso se ejecuta dentro de try/except: el programa muestra el error y continúa.

Uso:
    python p1_4_error_provocado.py               # casos 1 a 3 con imágenes creadas
    python p1_4_error_provocado.py --reales      # casos 1 a 3 con imágenes reales
    python p1_4_error_provocado.py --grande      # incluye la imagen de más de 20 MB
"""

import base64
import io
import json
import os
import sys

from langchain_core.messages import HumanMessage

from comun import (MODELO_SIN_VISION, MODELO_VISION, bloque_imagen, cargar_llm,
                   conjunto_elegido, guardar, llamar_con_reintentos, mime_de, ruta_imagen, titulo,
                   texto_respuesta)

PREGUNTA = "¿Qué código de infracción aparece en este comparendo?"
CONJUNTO = conjunto_elegido()

IMAGENES = {
    "creadas": {
        "cuatro": ["comparendo_01.png", "comparendo_02.png", "comparendo_03_foto.jpg",
                   "senal_velocidad_30.png"],
        "comparendo": "comparendo_01.png",
        "mal_declarada": "comparendo_03_foto.jpg",
    },
    "reales": {
        "cuatro": ["senal_escolar_30_bogota.jpg", "senal_30_el_zulia.jpg",
                   "senal_20_nevado_ruiz.jpg", "senal_pico_y_placa_bogota.jpg"],
        "comparendo": "comparendo_real_la_dorada.png",
        "mal_declarada": "senal_escolar_30_bogota.jpg",
    },
}[CONJUNTO]


def caso_mas_imagenes():
    nombres = IMAGENES["cuatro"]
    mensaje = HumanMessage(content=[{"type": "text", "text": "Resume estas 4 imágenes."}]
                           + [bloque_imagen(ruta_imagen(n, CONJUNTO)) for n in nombres])
    return MODELO_VISION, mensaje, f"Se envían 4 imágenes en un mismo mensaje: {', '.join(nombres)}"


def caso_modelo_sin_vision():
    nombre = IMAGENES["comparendo"]
    mensaje = HumanMessage(content=[{"type": "text", "text": PREGUNTA},
                                    bloque_imagen(ruta_imagen(nombre, CONJUNTO))])
    return MODELO_SIN_VISION, mensaje, (f"Se envía {nombre} al modelo {MODELO_SIN_VISION}, "
                                        "que no tiene visión")


def caso_tipo_mal_declarado():
    ruta = ruta_imagen(IMAGENES["mal_declarada"], CONJUNTO)
    mensaje = HumanMessage(content=[{"type": "text", "text": "¿Qué muestra esta imagen?"},
                                    bloque_imagen(ruta, mime_type="application/pdf")])
    return MODELO_VISION, mensaje, (f"Se envía {ruta.name} ({mime_de(ruta)}) declarada como "
                                    "mime_type='application/pdf'")


def caso_imagen_grande():
    from PIL import Image

    lado = 2600  # ruido aleatorio: el PNG casi no se comprime (~20 MB, ~27 MB en base64)
    img = Image.frombytes("RGB", (lado, lado), os.urandom(lado * lado * 3))
    buf = io.BytesIO()
    img.save(buf, format="PNG", compress_level=1)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    mensaje = HumanMessage(content=[{"type": "text", "text": PREGUNTA},
                                    {"type": "image", "base64": b64, "mime_type": "image/png"}])
    return MODELO_VISION, mensaje, (f"Se envía un PNG de {lado}x{lado} px con ruido: "
                                    f"{len(buf.getvalue()) / 1e6:.1f} MB "
                                    f"({len(b64) / 1e6:.1f} MB en base64)")


def detalle_error(e):
    """Extrae código HTTP y cuerpo del error devuelto por la API de Groq."""
    detalle = {"excepcion": type(e).__name__,
               "status_code": getattr(e, "status_code", None)}
    cuerpo = getattr(e, "body", None)
    detalle["cuerpo"] = cuerpo if cuerpo is not None else str(e)
    return detalle


def ejecutar(nombre, constructor):
    modelo, mensaje, descripcion = constructor()
    titulo(f"CASO: {nombre}")
    print(f"Qué se hizo : {descripcion}")
    print(f"Modelo      : {modelo}")
    try:
        llm = cargar_llm(model_name=modelo, max_tokens=300)
        response = llamar_con_reintentos(llm, [mensaje])
    except SystemExit:
        raise
    except Exception as e:
        detalle = detalle_error(e)
        print(f"Resultado   : ERROR {detalle['status_code']} ({detalle['excepcion']})")
        print("Mensaje de la API:")
        print(json.dumps(detalle["cuerpo"], ensure_ascii=False, indent=2)
              if isinstance(detalle["cuerpo"], (dict, list)) else detalle["cuerpo"])
        return {"caso": nombre, "descripcion": descripcion, "modelo": modelo,
                "hubo_error": True, **detalle}

    texto = texto_respuesta(response)
    print("Resultado   : la API NO devolvió error. Respuesta del modelo:")
    print(texto[:600])
    return {"caso": nombre, "descripcion": descripcion, "modelo": modelo,
            "hubo_error": False, "respuesta": texto}


def main():
    casos = [("mas_imagenes", caso_mas_imagenes),
             ("modelo_sin_vision", caso_modelo_sin_vision),
             ("tipo_mal_declarado", caso_tipo_mal_declarado)]
    if "--grande" in sys.argv:
        casos.append(("imagen_grande", caso_imagen_grande))

    titulo(f"1.4 ERROR PROVOCADO (imágenes {CONJUNTO})")
    resultados = [ejecutar(nombre, constructor) for nombre, constructor in casos]

    salida = guardar("1_4_errores.json",
                     json.dumps(resultados, ensure_ascii=False, indent=2, default=str), CONJUNTO)
    print(f"\nResultados guardados en {salida.relative_to(salida.parents[2])}")


if __name__ == "__main__":
    main()
