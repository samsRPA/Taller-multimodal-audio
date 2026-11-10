"""2.2 Respuesta del modelo a partir de la transcripción.

Flujo completo: audio -> transcripción (Whisper) -> respuesta (modelo de lenguaje).
Cada audio se transcribe y su texto se envía al modelo como la pregunta del usuario.

Uso:
    python p2_2_respuesta.py
"""

import json

from comun import (CARPETA_AUDIOS, MODELO_AUDIO, MODELO_LLM, cargar_audios, cargar_llm,
                   cliente_groq, guardar, responder, titulo, transcribir)

SISTEMA = (
    "Eres MultaClara, un asistente que ayuda a conductores en Colombia a entender sus "
    "comparendos de tránsito (Ley 769 de 2002, Código Nacional de Tránsito). Responde en "
    "español, en máximo 6 líneas, de forma clara y sin inventar valores ni artículos: si no "
    "estás seguro de un dato, dilo y recomienda confirmarlo en el SIMIT o con el organismo "
    "de tránsito."
)


def main():
    audios = cargar_audios()
    cliente = cliente_groq()
    llm = cargar_llm()

    titulo(f"2.2 AUDIO -> TRANSCRIPCIÓN -> RESPUESTA ({MODELO_AUDIO} + {MODELO_LLM})")
    resultados = []
    for a in audios:
        print(f"\n--- {a['archivo']} | {a['hablante']} | {a['condicion']} ---")
        texto, _ = transcribir(cliente, CARPETA_AUDIOS / a["archivo"])
        print(f"Transcripción enviada al modelo:\n{texto}")
        respuesta = responder(llm, SISTEMA, texto)
        print(f"\nRespuesta del modelo:\n{respuesta}")
        resultados.append({"archivo": a["archivo"], "transcripcion": texto, "respuesta": respuesta})

    guardar("2_2_respuestas.json", json.dumps(resultados, ensure_ascii=False, indent=2))
    partes = [f"# 2.2 Respuesta a partir de la transcripción\n\n- Transcripción: {MODELO_AUDIO}\n"
              f"- Respuesta: {MODELO_LLM}\n"]
    for r in resultados:
        partes.append(f"## {r['archivo']}\n\n**Transcripción:** {r['transcripcion']}\n\n"
                      f"**Respuesta:**\n\n{r['respuesta']}\n")
    guardar("2_2_respuestas.md", "\n".join(partes))
    print("\nResultados guardados en resultados/")


if __name__ == "__main__":
    main()
