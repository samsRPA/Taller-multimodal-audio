# Fuentes de las imágenes reales

## Comparendo real (documentos públicos, con datos personales tapados)

Los dos documentos son anexos de la contestación de la Inspección de Tránsito y Transporte Municipal de La Dorada (Caldas) a una acción judicial. El expediente lo publica la Rama Judicial: [018ContestaLaDorada.pdf](https://portalhistorico.ramajudicial.gov.co/documents/3014749/117038805/018ContestaLaDorada.pdf/607a152b-14bb-4a88-9a07-429f758c440e), páginas 29 y 30.

Antes de usarlos se taparon con recuadros negros el nombre, la cédula, la dirección, el teléfono y el municipio de residencia de la persona, la contraseña de consulta, el nombre del agente y su firma. Se dejaron visibles los datos que se extraen en el punto 1.2.

| Archivo | Qué muestra |
|---|---|
| `comparendo_real_la_dorada.png` | Orden de Comparendo Único Nacional (formato oficial con casillas encerradas en círculo). Fotodetección del 09/04/2021, código C29 |
| `evidencia_fotomulta_la_dorada.png` | Hoja "Evidencia de la infracción de tránsito" del mismo caso: foto de la cámara, placa, hora exacta y velocidad |

## Norma real

| Archivo | Qué muestra | Fuente |
|---|---|---|
| `norma_ley769_pag91.png` | Página 91 del PDF de la Ley 769 de 2002 (art. 131, códigos C.28 a D.2) | [bogota.gov.co: Ley-769-de-2002.pdf](https://bogota.gov.co/sites/default/files/tys/2017/11/Ley-769-de-2002.pdf) (texto oficial) |

## Fotos de señales (Wikimedia Commons, versión de 1280 px, sin modificar)

| Archivo | Qué muestra | Fuente | Autor | Licencia |
|---|---|---|---|---|
| `senal_escolar_30_bogota.jpg` | Señal preventiva de escolares sobre una señal de 30 km/h desgastada (Bogotá) | [Commons](https://commons.wikimedia.org/wiki/File:20230219_-_Bogot%C3%A1_-_Signalisation.jpg) | Fabricio Cardenas | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `senal_30_el_zulia.jpg` | Señal de 30 km/h en El Zulia (Norte de Santander) | [Commons](https://commons.wikimedia.org/wiki/File:Se%C3%B1ales_de_transito_en_El_Zulia.JPG) | EEIM | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0) |
| `senal_20_nevado_ruiz.jpg` | Señal de 20 km/h sobre placa cuadrada (Nevado del Ruiz, Caldas) | [Commons](https://commons.wikimedia.org/wiki/File:Nevado_del_Ruiz,_Caldas_19.JPG) | Ricohin | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `senal_pico_y_placa_bogota.jpg` | Señal "A 100 m circule mínimo 3 ocupantes en pico y placa" (Bogotá) | [Commons](https://commons.wikimedia.org/wiki/File:Bogot%C3%A1,_barrio_Armenia,_se%C3%B1al_de_tr%C3%A1nsito.JPG) | Felipe Restrepo Acosta | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |

## Valores reales

`valores_reales.json` tiene lo que una persona lee en los dos documentos del comparendo. `null` significa que el dato no aparece en ese documento (por ejemplo, la hoja de evidencia no trae el número del comparendo ni la placa del agente).
