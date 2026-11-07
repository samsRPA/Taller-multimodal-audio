"""1.1 Pregunta sobre una imagen.

Envía una imagen local en base64 junto con una pregunta del dominio (comparendos
de tránsito) y muestra la pregunta, la imagen usada y la respuesta del modelo.

Uso:
    python p1_1_pregunta_imagen.py             # imagen creada: fragmento de la norma
    python p1_1_pregunta_imagen.py --reales    # imagen real: página 91 de la Ley 769 de 2002
"""

from comun import (MODELO_VISION, cargar_llm, conjunto_elegido, describir_imagen, guardar,
                   invocar, mensaje_con_imagenes, ruta_imagen, titulo)

PREGUNTA = (
    "Eres un asistente que ayuda a conductores en Colombia a revisar sus comparendos. "
    "La imagen es {descripcion}. Responde usando solo lo que aparece en la imagen:\n"
    "1) ¿Qué conducta sanciona el código C.38?\n"
    "2) ¿Cuál es el valor de la multa, en smldv, para las infracciones del literal C?\n"
    "3) A un conductor le impusieron un comparendo C.38 mientras hablaba por celular "
    "usando un dispositivo de manos libres. Según el texto, ¿procede la infracción? "
    "Justifica citando la frase de la norma."
)

# La misma pregunta en los dos conjuntos. La página real NO muestra el encabezado del
# literal C (los 15 smldv están en la página 89): así se ve si el modelo lo admite o lo inventa.
CONFIG = {
    "creadas": {
        "imagen": "norma_art131.png",
        "descripcion": "un fragmento escaneado del artículo 131 de la Ley 769 de 2002",
    },
    "reales": {
        "imagen": "norma_ley769_pag91.png",
        "descripcion": "una página del Código Nacional de Tránsito (Ley 769 de 2002)",
    },
}


def main():
    conjunto = conjunto_elegido()
    config = CONFIG[conjunto]
    ruta = ruta_imagen(config["imagen"], conjunto)
    pregunta = PREGUNTA.format(descripcion=config["descripcion"])

    titulo(f"1.1 PREGUNTA SOBRE UNA IMAGEN (imágenes {conjunto})")
    print(f"Modelo : {MODELO_VISION}")
    print(f"Imagen : {describir_imagen(ruta)}")
    print(f"\nPregunta:\n{pregunta}")

    llm = cargar_llm()
    respuesta, segundos, tok_in, tok_out = invocar(llm, mensaje_con_imagenes(pregunta, [ruta]))

    titulo("RESPUESTA DEL MODELO")
    print(respuesta)
    print(f"\n[{segundos:.1f} s | tokens entrada: {tok_in} | tokens salida: {tok_out}]")

    salida = guardar(
        "1_1_pregunta_imagen.md",
        f"# 1.1 Pregunta sobre una imagen (imágenes {conjunto})\n\n- Modelo: {MODELO_VISION}\n"
        f"- Imagen: {describir_imagen(ruta)}\n\n## Pregunta\n\n{pregunta}\n\n"
        f"## Respuesta\n\n{respuesta}\n\n_Tiempo: {segundos:.1f} s · tokens entrada: {tok_in} · "
        f"tokens salida: {tok_out}_\n",
        conjunto,
    )
    print(f"Resultado guardado en {salida.relative_to(salida.parents[2])}")


if __name__ == "__main__":
    main()
