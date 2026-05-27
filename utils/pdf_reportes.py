from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime
from io import BytesIO
from db.conexion import obtener_conexion

def obtener_escuela_activa(conn):
    cur = conn.cursor()

    # 1. Obtener id desde configuracion
    cur.execute("""
        SELECT valor
        FROM configuracion
        WHERE clave = 'ultima_escuela'
        LIMIT 1
    """)
    row = cur.fetchone()

    if not row or not row[0]:
        return "Escuela no definida"

    escuela_id = row[0]

    # 2. Obtener nombre de la escuela
    cur.execute("""
        SELECT nombre
        FROM Escuela
        WHERE id = ?
    """, (escuela_id,))

    row = cur.fetchone()
    return row[0] if row else "Escuela no definida"

# ======================================================
# ENCABEZADO DEL PDF (se repite en todas las páginas)
# ======================================================
def encabezado_pdf(canvas, doc, titulo_reporte):
    conn = obtener_conexion()
    cur = conn.cursor()

    nombre_escuela = obtener_escuela_activa(conn)

    canvas.saveState()

    ancho, alto = landscape(A4)
    fecha = datetime.now().strftime("%d/%m/%Y")

    # Institución
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(
        ancho / 2,
        alto - 2 * cm,
        nombre_escuela
    )

    # Tipo de reporte
    canvas.setFont("Helvetica", 11)
    canvas.drawCentredString(
        ancho / 2,
        alto - 2.8 * cm,
        f"{titulo_reporte}"
    )

    # Fecha (derecha)
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(
        ancho - 2 * cm,
        alto - 2 * cm,
        f"Fecha: {fecha}"
    )

    # Línea divisoria
    canvas.line(
        2 * cm,
        alto - 3.3 * cm,
        ancho - 2 * cm,
        alto - 3.3 * cm
    )

    canvas.restoreState()


# ======================================================
# CONSTRUCCIÓN DEL PDF EN MEMORIA
# ======================================================
def construir_pdf_en_memoria(
    titulo,
    columnas,
    filas,
    ciclo_nombre
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=4 * cm,      # espacio para encabezado
        bottomMargin=2 * cm
    )

    elementos = []

    # Tabla
    data = [columnas] + filas

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
    ]))

    elementos.append(tabla)

    # Construir PDF con encabezado
    doc.build(
        elementos,
        onFirstPage=lambda c, d: encabezado_pdf(c, d, titulo),
        onLaterPages=lambda c, d: encabezado_pdf(c, d, titulo)
    )

    buffer.seek(0)
    return buffer
