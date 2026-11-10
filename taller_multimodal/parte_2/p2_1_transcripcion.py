"""2.1 Transcripción desde archivo.

Transcribe con Whisper cada audio de audios/audios.json, muestra el texto y lo compara
con lo que realmente se dijo (tasa de error de palabras, WER).

Uso:
    python p2_1_transcripcion.py
"""

import json

from comun import (ARCHIVO_TRANSCRIPCIONES, CARPETA_AUDIOS, MODELO_AUDIO, cargar_audios,
                   cliente_groq, guardar, tasa_error_palabras, titulo, transcribir)


def main():
    audios = cargar_audios()
    cliente = cliente_groq()

    titulo(f"2.1 TRANSCRIPCIÓN DESDE ARCHIVO (modelo {MODELO_AUDIO})")
    resultados = []
    for a in audios:
        ruta = CARPETA_AUDIOS / a["archivo"]
        print(f"\n--- {a['archivo']} | hablante: {a['hablante']} | {a['condicion']} ---")
        texto, duracion = transcribir(cliente, ruta)
        wer = tasa_error_palabras(a["lo_que_se_dijo"], texto)
        print(f"Se dijo      : {a['lo_que_se_dijo']}")
        print(f"Transcripción: {texto}")
        print(f"Duración: {duracion:.1f} s | WER: {wer * 100:.1f} %" if duracion and wer is not None
              else "Duración o WER no disponibles")
        resultados.append({**a, "duracion_s": round(duracion, 1) if duracion else None,
                           "transcripcion": texto,
                           "wer": round(wer, 3) if wer is not None else None})

    ARCHIVO_TRANSCRIPCIONES.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO_TRANSCRIPCIONES.write_text(json.dumps(resultados, ensure_ascii=False, indent=2),
                                       encoding="utf-8")

    filas = ["| Audio | Hablante | Condición | Duración (s) | WER | Transcripción |",
             "|---|---|---|---|---|---|"]
    for r in resultados:
        wer = f"{r['wer'] * 100:.1f} %" if r["wer"] is not None else "n/d"
        filas.append(f"| {r['archivo']} | {r['hablante']} | {r['condicion']} | "
                     f"{r['duracion_s']} | {wer} | {r['transcripcion']} |")
    guardar("2_1_transcripciones.md",
            f"# 2.1 Transcripción desde archivo\n\n- Modelo: {MODELO_AUDIO}\n\n" + "\n".join(filas) + "\n")

    validos = [r["wer"] for r in resultados if r["wer"] is not None]
    if validos:
        print(f"\nWER promedio: {sum(validos) / len(validos) * 100:.1f} %")
    print(f"Resultados guardados en {ARCHIVO_TRANSCRIPCIONES.parent}")


if __name__ == "__main__":
    main()
