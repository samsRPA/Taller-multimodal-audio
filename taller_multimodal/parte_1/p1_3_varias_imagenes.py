"""1.3 Varias imágenes en una solicitud.

Envía 3 imágenes relacionadas en un mismo mensaje (el límite de qwen/qwen3.8-27b
en Groq es 3 imágenes por solicitud) y pide al modelo un análisis conjunto.

Uso:
    python p1_3_varias_imagenes.py            # comparendo creado + señal + norma
    python p1_3_varias_imagenes.py --reales   # comparendo real + evidencia de la cámara + norma
"""

from comun import (MODELO_VISION, cargar_llm, conjunto_elegido, describir_imagen, guardar,
                   invocar, mensaje_con_imagenes, ruta_imagen, titulo)

CONFIG = {
    "creadas": {
        "imagenes": ["comparendo_01.png", "senal_velocidad_30.png", "norma_art131.png"],
        "pregunta": (
            "Te envío tres imágenes en este orden: (1) un comparendo de tránsito, (2) la señal "
            "que había en la vía donde se impuso y (3) un fragmento del artículo 131 de la "
            "Ley 769 de 2002. Analízalas en conjunto y responde:\n"
            "a) ¿Qué código de infracción registra el comparendo y qué conducta describe la norma "
            "para ese código?\n"
            "b) ¿Qué límite de velocidad indica la señal y qué velocidad dice el comparendo que "
            "se registró? ¿Son coherentes con la infracción?\n"
            "c) Según la norma de la imagen, ¿a cuántos smldv equivale la multa?\n"
            "d) Menciona dos datos del comparendo que el conductor debería verificar para "
            "comprobar que el procedimiento quedó completo.\n"
            "Responde en máximo 12 líneas y no inventes datos que no estén en las imágenes."
        ),
    },
    "reales": {
        "imagenes": ["comparendo_real_la_dorada.png", "evidencia_fotomulta_la_dorada.png",
                     "norma_ley769_pag91.png"],
        "pregunta": (
            "Te envío tres imágenes reales en este orden: (1) una orden de comparendo único "
            "nacional, (2) la hoja de evidencia de la cámara para ese mismo comparendo y (3) una "
            "página del Código Nacional de Tránsito (Ley 769 de 2002). Los recuadros negros son "
            "datos personales tapados. Analízalas en conjunto y responde:\n"
            "a) ¿Qué código de infracción registra el comparendo? ¿Coincide con la evidencia y "
            "qué conducta describe la norma para ese código?\n"
            "b) Compara la fecha, la hora y la placa entre el comparendo y la evidencia. "
            "¿Hay alguna diferencia?\n"
            "c) ¿Qué velocidad registró la cámara y cuál era el límite?\n"
            "d) ¿La página de la norma muestra el valor de la multa para ese código?\n"
            "e) Según la casilla 17, ¿cómo se impuso el comparendo?\n"
            "Responde en máximo 14 líneas y no inventes datos que no estén en las imágenes."
        ),
    },
}


def main():
    conjunto = conjunto_elegido()
    config = CONFIG[conjunto]
    rutas = [ruta_imagen(n, conjunto) for n in config["imagenes"]]

    titulo(f"1.3 VARIAS IMÁGENES EN UNA SOLICITUD (imágenes {conjunto})")
    print(f"Modelo : {MODELO_VISION}")
    for i, ruta in enumerate(rutas, start=1):
        print(f"Imagen {i}: {describir_imagen(ruta)}")
    print(f"\nPregunta:\n{config['pregunta']}")

    llm = cargar_llm()
    respuesta, segundos, tok_in, tok_out = invocar(llm, mensaje_con_imagenes(config["pregunta"], rutas))

    titulo("RESPUESTA DEL MODELO")
    print(respuesta)
    print(f"\n[{segundos:.1f} s | tokens entrada: {tok_in} | tokens salida: {tok_out}]")

    lista = "\n".join(f"{i}. {describir_imagen(r)}" for i, r in enumerate(rutas, start=1))
    salida = guardar(
        "1_3_varias_imagenes.md",
        f"# 1.3 Varias imágenes en una solicitud (imágenes {conjunto})\n\n- Modelo: {MODELO_VISION}\n\n"
        f"## Imágenes\n\n{lista}\n\n## Pregunta\n\n{config['pregunta']}\n\n## Respuesta\n\n{respuesta}\n\n"
        f"_Tiempo: {segundos:.1f} s · tokens entrada: {tok_in} · tokens salida: {tok_out}_\n",
        conjunto,
    )
    print(f"Resultado guardado en {salida.relative_to(salida.parents[2])}")


if __name__ == "__main__":
    main()
