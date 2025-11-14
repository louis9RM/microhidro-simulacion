from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from database import RegistroSimulacion, SessionLocal, init_db
from random import uniform
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Crear app
app = FastAPI(
    title="API Simulación Microhidráulica",
    description="Backend para simulación académica de microgeneración hidroeléctrica",
    version="1.0.0"
)

# ==== CORS ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar base de datos
init_db()


@app.get("/")
def read_root():
    return {"message": "Backend listo con base de datos y simulación activa"}


@app.get("/simular")
def simular():
    """Simula un punto de operación y lo guarda en la base de datos"""

    # Entradas hidráulicas simuladas
    caudal_lps = round(uniform(1.7, 1.9), 2)   # L/s
    presion_bar = round(uniform(3.2, 3.4), 2)  # bar

    # Constantes físicas
    rho = 1000      # kg/m³
    g = 9.81        # m/s²

    # Caudal a m³/s
    caudal_m3s = caudal_lps / 1000.0

    # Presión (bar) → altura (m)
    altura_m = (presion_bar * 100000) / (rho * g)

    # Potencia hidráulica
    potencia_hidraulica = rho * g * caudal_m3s * altura_m

    # Parte eléctrica
    eficiencia_global = 0.40
    potencia_electrica = potencia_hidraulica * eficiencia_global

    potencia_hidraulica = round(potencia_hidraulica, 2)
    potencia_electrica = round(potencia_electrica, 2)

    # Guardar en BD
    db = SessionLocal()
    registro = RegistroSimulacion(
        caudal_lps=caudal_lps,
        presion_bar=presion_bar,
        potencia_hidraulica_w=potencia_hidraulica,
        potencia_electrica_w=potencia_electrica
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)

    return {
        "status": "OK",
        "mensaje": "Simulación profesional realizada",
        "datos": {
            "caudal_lps": caudal_lps,
            "presion_bar": presion_bar,
            "altura_hidraulica_m": round(altura_m, 2),
            "potencia_hidraulica_w": potencia_hidraulica,
            "potencia_electrica_w": potencia_electrica,
            "eficiencia_sistema": eficiencia_global
        }
    }


@app.get("/historial")
def historial():
    """Devuelve el historial de simulaciones."""
    db = SessionLocal()
    registros = db.query(RegistroSimulacion).order_by(RegistroSimulacion.id).all()

    salida = [
        {
            "id": r.id,
            "caudal_lps": r.caudal_lps,
            "presion_bar": r.presion_bar,
            "potencia_hidraulica_w": r.potencia_hidraulica_w,
            "potencia_electrica_w": r.potencia_electrica_w,
        }
        for r in registros
    ]

    return salida


@app.get("/reporte")
def generar_reporte():
    """Genera un reporte PDF profesional con resumen y tabla."""

    db = SessionLocal()
    registros = db.query(RegistroSimulacion).order_by(RegistroSimulacion.id).all()

    file_path = "ReporteSimulacion.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Encabezado
    titulo = "Reporte de Simulación de Microgeneración Hidroeléctrica"
    subtitulo = f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

    elements.append(Paragraph(titulo, styles["Title"]))
    elements.append(Paragraph(subtitulo, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Resumen
    if registros:
        total = len(registros)
        prom_pot = sum(r.potencia_electrica_w for r in registros) / total
        max_pot = max(r.potencia_electrica_w for r in registros)
        min_pot = min(r.potencia_electrica_w for r in registros)

        resumen_text = (
            f"<b>Número de simulaciones:</b> {total}<br/>"
            f"<b>Potencia eléctrica promedio:</b> {prom_pot:.2f} W<br/>"
            f"<b>Potencia eléctrica máxima:</b> {max_pot:.2f} W<br/>"
            f"<b>Potencia eléctrica mínima:</b> {min_pot:.2f} W<br/>"
        )
    else:
        resumen_text = "No se encontraron registros de simulación en la base de datos."

    elements.append(Paragraph("Resumen general", styles["Heading2"]))
    elements.append(Paragraph(resumen_text, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Tabla
    data = [["ID", "Caudal (L/s)", "Presión (bar)", "P. Hidráulica (W)", "P. Eléctrica (W)"]]

    for r in registros:
        data.append([
            r.id,
            f"{r.caudal_lps:.2f}",
            f"{r.presion_bar:.2f}",
            f"{r.potencia_hidraulica_w:.2f}",
            f"{r.potencia_electrica_w:.2f}",
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#1f2937")),
    ]))

    elements.append(Paragraph("Detalle de simulaciones", styles["Heading2"]))
    elements.append(table)

    # Construir PDF
    doc.build(elements)

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="ReporteSimulacion.pdf"
    )
