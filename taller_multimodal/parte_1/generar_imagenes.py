"""Genera las imágenes del dominio (comparendos de tránsito) usadas en la Parte 1.

Todas las imágenes son FICTICIAS y llevan una marca de agua que lo indica:
no se usan comparendos reales para no exponer datos personales.

Se generan 5 imágenes en la carpeta imagenes/creadas/:

    comparendo_01.png       comparendo impreso, limpio (Bogotá, C29)
    comparendo_02.png       comparendo diligenciado "a mano" (Medellín, C02)
    comparendo_03_foto.jpg  foto de un comparendo: girada, borrosa y con sombra (Cali, D02)
    norma_art131.png        fragmento escaneado del art. 131 de la Ley 769 de 2002
    senal_velocidad_30.png  señal de velocidad máxima 30 km/h en zona escolar

Además se escribe imagenes/creadas/valores_reales.json con los valores que una persona lee en cada
comparendo; es la referencia para medir los aciertos de la extracción (punto 1.2).

Uso:
    python generar_imagenes.py
"""

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

CARPETA = Path(__file__).parent
CARPETA_IMAGENES = CARPETA / "imagenes" / "creadas"

# Fuentes del sistema (Linux). Si no existen, se usa la fuente por defecto de Pillow.
FUENTES = {
    "sans": "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "sans_b": "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "serif": "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
    "serif_b": "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
    "mono": "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    "mano": "/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf",
}


def fuente(nombre, tamano):
    try:
        return ImageFont.truetype(FUENTES[nombre], tamano)
    except OSError:
        return ImageFont.load_default(tamano)


# ---------------------------------------------------------------------------
# Datos de los tres comparendos ficticios
# ---------------------------------------------------------------------------
COMPARENDOS = [
    {
        "archivo": "comparendo_01.png",
        "estilo": "impreso",
        "numero": "11001000000045872310",
        "fecha": "14/10/2026",
        "hora": "07:42",
        "direccion": "Av. Boyacá con Calle 80",
        "ciudad": "Bogotá D.C.",
        "entidad_emisora": "Secretaría Distrital de Movilidad de Bogotá",
        "placa": "KTR482",
        "tipo": "Automóvil",
        "servicio": "Particular",
        "licencia_transito": "10012345678",
        "conductor": "Andrés Felipe Rojas Quintero",
        "documento": "C.C. 1.020.456.789",
        "licencia_conduccion": "1020456789",
        "codigo": "C29",
        "descripcion": "Conducir un vehículo a velocidad superior a la máxima permitida.",
        "agente": "Luis Hernán Cárdenas Mora",
        "placa_agente": "087654",
        "entidad_agente": "Policía Nacional - Seccional de Tránsito",
        "observaciones": [
            "Zona escolar señalizada a 30 km/h. Velocidad registrada: 52 km/h",
            "con cinemómetro serie VC-2231. Se informa al conductor el motivo.",
        ],
    },
    {
        "archivo": "comparendo_02.png",
        "estilo": "manuscrito",
        "numero": "05001000000039917446",
        "fecha": "03/09/2026",
        "hora": "18:15",
        "direccion": "Cra. 43A con Calle 10",
        "ciudad": "Medellín",
        "entidad_emisora": "Secretaría de Movilidad de Medellín",
        "placa": "MNL37E",
        "tipo": "Motocicleta",
        "servicio": "Particular",
        "licencia_transito": "10098765432",
        "conductor": "Valentina Ospina Restrepo",
        "documento": "C.C. 1.152.334.871",
        "licencia_conduccion": "1152334871",
        "codigo": "C02",
        "descripcion": "Estacionar un vehículo en sitios prohibidos.",
        "agente": "Jhon Fredy Zapata Gil",
        "placa_agente": "112093",
        "entidad_agente": "Secretaría de Movilidad de Medellín",
        "observaciones": [
            "Motocicleta estacionada sobre el andén frente a hidrante.",
            "Se toma registro fotográfico.",
        ],
    },
    {
        "archivo": "comparendo_03_foto.jpg",
        "estilo": "foto",
        "numero": "76001000000051236089",
        "fecha": "27/08/2026",
        "hora": "11:05",
        "direccion": "Calle 5 con Carrera 66",
        "ciudad": "Santiago de Cali",
        "entidad_emisora": "Secretaría de Movilidad de Santiago de Cali",
        "placa": "HJW905",
        "tipo": "Camioneta",
        "servicio": "Particular",
        "licencia_transito": "10055501234",
        "conductor": "Carlos Mario Viveros Lenis",
        "documento": "C.C. 94.385.120",
        "licencia_conduccion": "94385120",
        "codigo": "D02",
        "descripcion": "Conducir sin portar los seguros ordenados por la ley.",
        "agente": "Diana Marcela Lozano Paz",
        "placa_agente": "064218",
        "entidad_agente": "Secretaría de Movilidad de Santiago de Cali",
        "observaciones": [
            "SOAT vencido el 15/07/2026 según consulta en el RUNT.",
            "Vehículo inmovilizado y trasladado a patios.",
        ],
    },
]

TIPOS_VEHICULO = ["Automóvil", "Motocicleta", "Camioneta", "Bus", "Camión", "Otro"]


def _sin_tildes(texto):
    reemplazos = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")
    return texto.translate(reemplazos)


def valores_reales(c):
    """Valores que una persona lee en el comparendo, en el formato del esquema."""
    dia, mes, anio = c["fecha"].split("/")
    return {
        "numero_comparendo": c["numero"],
        "fecha_infraccion": f"{anio}-{mes}-{dia}",
        "hora_infraccion": c["hora"],
        "placa_vehiculo": c["placa"],
        "tipo_vehiculo": _sin_tildes(c["tipo"]).lower(),
        "codigo_infraccion": c["codigo"],
        "placa_agente": c["placa_agente"],
    }


# ---------------------------------------------------------------------------
# Dibujo del comparendo
# ---------------------------------------------------------------------------
ANCHO, ALTO = 1240, 1754
MARGEN = 60
TINTA_FORM = (25, 45, 95)  # azul oscuro del formato impreso
TINTA_MANO = (20, 40, 160)  # azul de bolígrafo


def _marca_agua(img, texto="EJEMPLO FICTICIO"):
    capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    f = fuente("sans_b", 150)
    w = d.textlength(texto, font=f)
    temp = Image.new("RGBA", (int(w) + 40, 200), (0, 0, 0, 0))
    ImageDraw.Draw(temp).text((20, 10), texto, font=f, fill=(200, 30, 30, 50))
    temp = temp.rotate(35, expand=True)
    capa.paste(temp, ((img.width - temp.width) // 2, (img.height - temp.height) // 2), temp)
    return Image.alpha_composite(img.convert("RGBA"), capa).convert("RGB")


def dibujar_comparendo(c):
    img = Image.new("RGB", (ANCHO, ALTO), "white")
    d = ImageDraw.Draw(img)
    manuscrito = c["estilo"] == "manuscrito"
    rnd = random.Random(c["numero"])

    f_tit = fuente("sans_b", 34)
    f_sub = fuente("sans", 24)
    f_sec = fuente("sans_b", 24)
    f_eti = fuente("sans", 19)
    f_val = fuente("mano", 40) if manuscrito else fuente("mono", 27)
    f_num = fuente("mono", 30)
    color_val = TINTA_MANO if manuscrito else (10, 10, 10)

    def valor(x, y, texto):
        """Escribe un valor del formulario (impreso o a mano)."""
        if manuscrito:
            dx, dy = rnd.randint(-4, 6), rnd.randint(-8, -2)
            d.text((x + dx, y + dy), texto, font=f_val, fill=color_val)
        else:
            d.text((x, y), texto, font=f_val, fill=color_val)

    def casilla(x, y, w, h, etiqueta, texto=None):
        d.rectangle([x, y, x + w, y + h], outline=TINTA_FORM, width=2)
        d.text((x + 8, y + 5), etiqueta, font=f_eti, fill=TINTA_FORM)
        if texto is not None:
            valor(x + 12, y + 32, texto)

    def seccion(y, titulo):
        d.rectangle([MARGEN, y, ANCHO - MARGEN, y + 36], fill=TINTA_FORM)
        d.text((MARGEN + 12, y + 5), titulo, font=f_sec, fill="white")
        return y + 36

    # Marco y encabezado
    d.rectangle([30, 30, ANCHO - 30, ALTO - 30], outline=TINTA_FORM, width=4)
    d.text((MARGEN, 55), "ORDEN DE COMPARENDO NACIONAL", font=f_tit, fill=TINTA_FORM)
    d.text((MARGEN, 105), c["entidad_emisora"], font=f_sub, fill=TINTA_FORM)
    d.text((MARGEN, 137), "Formato de ejemplo - Código Nacional de Tránsito (Ley 769 de 2002)",
           font=f_eti, fill=TINTA_FORM)
    d.rectangle([ANCHO - 500, 55, ANCHO - MARGEN, 160], outline=TINTA_FORM, width=2)
    d.text((ANCHO - 485, 62), "No. de comparendo", font=f_eti, fill=TINTA_FORM)
    d.text((ANCHO - 485, 102), c["numero"], font=f_num, fill=(190, 20, 20))

    ancho_util = ANCHO - 2 * MARGEN
    y = 185

    # 1. Fecha y hora
    y = seccion(y, "1. FECHA Y HORA DE LA INFRACCIÓN")
    casilla(MARGEN, y, ancho_util // 2, 85, "Fecha (DD/MM/AAAA)", c["fecha"])
    casilla(MARGEN + ancho_util // 2, y, ancho_util // 2, 85, "Hora (HH:MM, 24 h)", c["hora"])
    y += 85 + 18

    # 2. Lugar
    y = seccion(y, "2. LUGAR DE LA INFRACCIÓN")
    casilla(MARGEN, y, int(ancho_util * 0.6), 85, "Dirección / vía", c["direccion"])
    casilla(MARGEN + int(ancho_util * 0.6), y, ancho_util - int(ancho_util * 0.6), 85,
            "Municipio", c["ciudad"])
    y += 85 + 18

    # 3. Vehículo
    y = seccion(y, "3. DATOS DEL VEHÍCULO")
    casilla(MARGEN, y, 300, 85, "Placa", c["placa"])
    casilla(MARGEN + 300, y, 360, 85, "Licencia de tránsito No.", c["licencia_transito"])
    casilla(MARGEN + 660, y, ancho_util - 660, 85, "Servicio", c["servicio"])
    y += 85
    d.rectangle([MARGEN, y, ANCHO - MARGEN, y + 85], outline=TINTA_FORM, width=2)
    d.text((MARGEN + 8, y + 5), "Tipo de vehículo (marque con X)", font=f_eti, fill=TINTA_FORM)
    x = MARGEN + 20
    for tipo in TIPOS_VEHICULO:
        d.rectangle([x, y + 40, x + 28, y + 68], outline=TINTA_FORM, width=2)
        if tipo == c["tipo"]:
            if manuscrito:
                d.line([x + 2, y + 38, x + 30, y + 70], fill=TINTA_MANO, width=4)
                d.line([x + 30, y + 40, x + 2, y + 66], fill=TINTA_MANO, width=4)
            else:
                d.text((x + 4, y + 38), "X", font=fuente("sans_b", 28), fill="black")
        d.text((x + 38, y + 42), tipo, font=f_eti, fill=TINTA_FORM)
        x += 185
    y += 85 + 18

    # 4. Conductor
    y = seccion(y, "4. DATOS DEL CONDUCTOR")
    casilla(MARGEN, y, ancho_util, 85, "Nombres y apellidos", c["conductor"])
    y += 85
    casilla(MARGEN, y, ancho_util // 2, 85, "Documento de identidad", c["documento"])
    casilla(MARGEN + ancho_util // 2, y, ancho_util // 2, 85, "Licencia de conducción No.",
            c["licencia_conduccion"])
    y += 85 + 18

    # 5. Infracción
    y = seccion(y, "5. INFRACCIÓN")
    casilla(MARGEN, y, 220, 110, "Código", c["codigo"])
    d.rectangle([MARGEN + 220, y, ANCHO - MARGEN, y + 110], outline=TINTA_FORM, width=2)
    d.text((MARGEN + 228, y + 5), "Descripción de la infracción", font=f_eti, fill=TINTA_FORM)
    f_desc = fuente("mano", 30) if manuscrito else fuente("sans", 22)
    d.text((MARGEN + 236, y + 45), c["descripcion"], font=f_desc, fill=color_val)
    y += 110 + 18

    # 6. Agente
    y = seccion(y, "6. AGENTE DE TRÁNSITO QUE IMPONE LA ORDEN")
    casilla(MARGEN, y, int(ancho_util * 0.62), 85, "Nombre del agente", c["agente"])
    casilla(MARGEN + int(ancho_util * 0.62), y, ancho_util - int(ancho_util * 0.62), 85,
            "Placa del agente No.", c["placa_agente"])
    y += 85
    casilla(MARGEN, y, ancho_util, 85, "Entidad", c["entidad_agente"])
    y += 85 + 18

    # 7. Observaciones
    y = seccion(y, "7. OBSERVACIONES Y PRUEBAS")
    d.rectangle([MARGEN, y, ANCHO - MARGEN, y + 120], outline=TINTA_FORM, width=2)
    f_obs = fuente("mano", 30) if manuscrito else fuente("sans", 22)
    for i, linea in enumerate(c["observaciones"]):
        d.text((MARGEN + 14, y + 14 + i * 42), linea, font=f_obs, fill=color_val)
    y += 120 + 40

    # Firmas
    for i, rotulo in enumerate(["Firma del agente", "Firma del conductor"]):
        x0 = MARGEN + 40 + i * 560
        puntos = [(x0 + 30 + k * 18, y + 40 + rnd.randint(-22, 22)) for k in range(18)]
        d.line(puntos, fill=TINTA_MANO, width=3)
        d.line([x0, y + 75, x0 + 460, y + 75], fill=TINTA_FORM, width=2)
        d.text((x0, y + 82), rotulo, font=f_eti, fill=TINTA_FORM)

    d.text((MARGEN, ALTO - 80),
           "DOCUMENTO FICTICIO elaborado para fines académicos (Taller multimodal). "
           "No corresponde a una persona ni a un trámite real.",
           font=fuente("sans", 17), fill=(120, 120, 120))
    return _marca_agua(img)


def efecto_foto(img):
    """Simula una foto tomada con el celular: giro, perspectiva, sombra, desenfoque."""
    rnd = random.Random(7)
    # Fondo de mesa
    fondo = Image.new("RGB", (img.width + 260, img.height + 260), (120, 86, 60))
    df = ImageDraw.Draw(fondo)
    for yy in range(0, fondo.height, 9):
        tono = 110 + rnd.randint(-12, 12)
        df.line([0, yy, fondo.width, yy + rnd.randint(-6, 6)], fill=(tono, int(tono * 0.72), 52), width=5)

    girada = img.convert("RGBA").rotate(-3.2, resample=Image.BICUBIC, expand=True)
    fondo.paste(girada, (110, 95), girada)

    # Leve perspectiva (la parte superior queda un poco más estrecha)
    w, h = fondo.size
    coef = _coeficientes_perspectiva(
        [(0, 0), (w, 0), (w, h), (0, h)],
        [(-28, 0), (w + 28, 0), (w, h), (0, h)],
    )
    fondo = fondo.transform((w, h), Image.PERSPECTIVE, coef, Image.BICUBIC)

    # Sombra/gradiente de luz de izquierda a derecha
    sombra = Image.new("L", fondo.size, 0)
    ds = ImageDraw.Draw(sombra)
    for xx in range(fondo.width):
        ds.line([xx, 0, xx, fondo.height], fill=int(95 * (xx / fondo.width) ** 1.6))
    oscuro = Image.new("RGB", fondo.size, (0, 0, 0))
    fondo = Image.composite(oscuro, fondo, sombra)

    fondo = fondo.filter(ImageFilter.GaussianBlur(1.3))
    fondo = ImageEnhance.Contrast(fondo).enhance(0.82)
    fondo = ImageEnhance.Color(fondo).enhance(0.85)
    fondo = fondo.resize((int(fondo.width * 0.72), int(fondo.height * 0.72)), Image.LANCZOS)
    return fondo


def _coeficientes_perspectiva(destino, origen):
    """Coeficientes para Image.transform(PERSPECTIVE) (resuelve el sistema 8x8)."""
    filas, b = [], []
    for (x, y), (u, v) in zip(destino, origen):
        filas.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        filas.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b += [u, v]
    # Eliminación de Gauss (sin dependencias externas)
    n = 8
    m = [fila + [bi] for fila, bi in zip(filas, b)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(m[r][i]))
        m[i], m[piv] = m[piv], m[i]
        for r in range(n):
            if r != i:
                f = m[r][i] / m[i][i]
                m[r] = [a - f * c for a, c in zip(m[r], m[i])]
    return [m[i][n] / m[i][i] for i in range(n)]


# ---------------------------------------------------------------------------
# Fragmento escaneado de la norma
# ---------------------------------------------------------------------------
NORMA = [
    ("titulo", "LEY 769 DE 2002"),
    ("subtitulo", "(agosto 6)"),
    ("subtitulo", "Por la cual se expide el Código Nacional de Tránsito Terrestre"),
    ("subtitulo", "y se dictan otras disposiciones."),
    ("espacio", ""),
    ("negrita", "ARTÍCULO 131. MULTAS."),
    ("nota", "<Artículo modificado por el artículo 21 de la Ley 1383 de 2010>"),
    ("parrafo", "Los infractores de las normas de tránsito serán sancionados con la imposición "
                "de multas, de acuerdo con el tipo de infracción así:"),
    ("nota", "[...]"),
    ("parrafo", "C. Será sancionado con multa equivalente a quince (15) salarios mínimos legales "
                "diarios vigentes (smldv) el conductor y/o propietario de un vehículo automotor "
                "que incurra en cualquiera de las siguientes infracciones:"),
    ("parrafo", "C.02. Estacionar un vehículo en sitios prohibidos."),
    ("nota", "[...]"),
    ("parrafo", "C.29. Conducir un vehículo a velocidad superior a la máxima permitida."),
    ("nota", "[...]"),
    ("parrafo", "C.38. Usar sistemas móviles de comunicación o teléfonos instalados en los "
                "vehículos al momento de conducir, exceptuando si éstos son utilizados con "
                "accesorios o equipos auxiliares que permitan tener las manos libres."),
    ("nota", "[...]"),
    ("parrafo", "D. Será sancionado con multa equivalente a treinta (30) salarios mínimos legales "
                "diarios vigentes (smldv) el conductor y/o propietario de un vehículo automotor "
                "que incurra en cualquiera de las siguientes infracciones:"),
    ("nota", "[...]"),
    ("parrafo", "D.02. Conducir sin portar los seguros ordenados por la ley. Además, el "
                "vehículo será inmovilizado."),
    ("espacio", ""),
    ("pie", "Transcripción parcial con fines académicos. Se omiten literales y numerales no "
            "citados ([...])."),
]


def _envolver(d, texto, f, ancho_max):
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = f"{actual} {p}".strip()
        if d.textlength(prueba, font=f) <= ancho_max:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def dibujar_norma():
    img = Image.new("L", (1240, 1754), 250)
    d = ImageDraw.Draw(img)
    estilos = {
        "titulo": (fuente("serif_b", 40), True),
        "subtitulo": (fuente("serif", 28), True),
        "negrita": (fuente("serif_b", 30), False),
        "nota": (fuente("serif", 24), False),
        "parrafo": (fuente("serif", 29), False),
        "pie": (fuente("serif", 21), False),
    }
    y, x0, ancho_max = 110, 120, 1000
    for tipo, texto in NORMA:
        if tipo == "espacio":
            y += 30
            continue
        f, centrado = estilos[tipo]
        for linea in _envolver(d, texto, f, ancho_max):
            x = (img.width - d.textlength(linea, font=f)) / 2 if centrado else x0
            d.text((x, y), linea, font=f, fill=25 if tipo != "pie" else 90)
            y += int(f.size * 1.45)
        y += 14
    d.text((img.width - 230, img.height - 90), "Pág. 1 de 1", font=fuente("serif", 22), fill=90)

    # Efecto de escaneo: ruido, leve giro y desenfoque
    rnd = random.Random(131)
    px = img.load()
    for _ in range(26000):
        xx, yy = rnd.randrange(img.width), rnd.randrange(img.height)
        px[xx, yy] = max(0, px[xx, yy] - rnd.randint(30, 110))
    img = img.rotate(0.7, resample=Image.BICUBIC, fillcolor=235)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    return img


# ---------------------------------------------------------------------------
# Señal de tránsito
# ---------------------------------------------------------------------------
def dibujar_senal():
    w, h = 900, 1200
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for yy in range(h):  # cielo y andén
        if yy < 900:
            t = yy / 900
            d.line([0, yy, w, yy], fill=(int(120 + 90 * t), int(170 + 60 * t), 235))
        else:
            d.line([0, yy, w, yy], fill=(150, 150, 145))
    d.rectangle([0, 1000, w, h], fill=(70, 70, 72))
    for xx in range(40, w, 220):
        d.rectangle([xx, 1090, xx + 120, 1105], fill=(235, 235, 235))

    # Poste
    d.rectangle([435, 330, 465, 1010], fill=(160, 160, 165), outline=(110, 110, 115))

    # Señal SR-30 (velocidad máxima)
    cx, cy, r = 450, 300, 230
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="white", outline=(60, 60, 60), width=3)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], outline=(200, 20, 30), width=42)
    f30 = fuente("sans_b", 210)
    tw = d.textlength("30", font=f30)
    d.text((cx - tw / 2, cy - 125), "30", font=f30, fill="black")

    # Placa complementaria "ZONA ESCOLAR" (amarillo verdoso fluorescente)
    d.rectangle([255, 560, 645, 720], fill=(200, 235, 30), outline=(40, 40, 40), width=6)
    fz = fuente("sans_b", 62)
    for i, palabra in enumerate(["ZONA", "ESCOLAR"]):
        tw = d.textlength(palabra, font=fz)
        d.text((450 - tw / 2, 572 + i * 70), palabra, font=fz, fill="black")

    d.text((20, h - 40), "Imagen ilustrativa generada para el taller", font=fuente("sans", 20),
           fill=(230, 230, 230))
    return img.filter(ImageFilter.GaussianBlur(0.4))


def main():
    CARPETA_IMAGENES.mkdir(parents=True, exist_ok=True)
    reales = {}
    for c in COMPARENDOS:
        img = dibujar_comparendo(c)
        destino = CARPETA_IMAGENES / c["archivo"]
        if c["estilo"] == "foto":
            efecto_foto(img).save(destino, "JPEG", quality=58)
        else:
            img.save(destino, optimize=True)
        reales[c["archivo"]] = valores_reales(c)
        print(f"OK {destino.name}")

    dibujar_norma().save(CARPETA_IMAGENES / "norma_art131.png", optimize=True)
    print("OK norma_art131.png")
    dibujar_senal().save(CARPETA_IMAGENES / "senal_velocidad_30.png", optimize=True)
    print("OK senal_velocidad_30.png")

    ruta_reales = CARPETA_IMAGENES / "valores_reales.json"
    ruta_reales.write_text(json.dumps(reales, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {ruta_reales.name}")


if __name__ == "__main__":
    main()
