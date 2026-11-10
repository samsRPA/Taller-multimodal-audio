# Guion para grabar los audios

El enunciado pide al menos 4 audios de 10 a 30 segundos, con al menos dos hablantes y un audio con ruido de fondo. Cada integrante lee en voz natural, a ritmo normal. Si cambian alguna palabra al hablar, actualicen el campo `lo_que_se_dijo` de `audios.json` con lo que realmente se dijo, porque con eso se calcula el porcentaje de error.

Guarden los archivos en esta carpeta con estos nombres (el formato puede ser wav, mp3, m4a, ogg o webm; si usan otra extensión, cámbienla también en `audios.json`).

| Archivo | Quién habla | Condición |
|---|---|---|
| `audio_01.ogg` | Samuel | Sin ruido |
| `audio_02.ogg` | Carlos | Sin ruido |
| `audio_03.ogg` | Samuel | Con ruido de fondo (tele, calle, música baja, cafetería) |
| `audio_04.ogg` | Carlos | Sin ruido |

## Textos

1. Buenas, me llegó un comparendo con el código C29 por una fotodetección en Bogotá. ¿Cuántos días hábiles tengo para pagar con el descuento del cincuenta por ciento y qué pasa si no hago el curso pedagógico?
2. Quiero saber si me pueden inmovilizar la motocicleta por no tener el SOAT vigente, y cómo consulto en el SIMIT si tengo una multa pendiente asociada a mi placa.
3. Estoy en la calle y me pusieron un comparendo por no portar la licencia de conducción. ¿Es una infracción tipo B o tipo C según el artículo ciento treinta y uno del Código Nacional de Tránsito?
4. Si el comparendo es por exceso de velocidad y la cámara no muestra bien la placa, ¿puedo pedir la nulidad y cuántos días tiene la autoridad para notificarme la fotomulta?

Cada texto dura entre 12 y 20 segundos leído de forma normal. Tienen términos técnicos del dominio (SIMIT, SOAT, fotodetección, inmovilizar, comparendo, nulidad, fotomulta, curso pedagógico, C29, Código Nacional de Tránsito) para ver cómo los maneja Whisper.
