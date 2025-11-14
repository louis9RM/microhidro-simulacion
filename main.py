from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import RegistroSimulacion, SessionLocal, init_db
from random import uniform

# Crear app
app = FastAPI(
    title="API Simulación Microhidráulica",
    description="Backend para simulación académica de microgeneración hidroeléctrica",
    version="1.0.0"
)

# ==== CORS: permitir que el frontend (HTML) llame a la API ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # para trabajo académico está bien abrir todo
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
    """
    Simula un punto de operación del sistema hidráulico-eléctrico,
    calcula potencias y guarda el resultado en la base de datos.
    """

    # --- Entradas simuladas (parte hidráulica) ---
    caudal_lps = round(uniform(1.7, 1.9), 2)   # Caudal en L/s
    presion_bar = round(uniform(3.2, 3.4), 2)  # Presión en bar

    # --- Constantes físicas ---
    rho = 1000      # densidad del agua (kg/m³)
    g = 9.81        # gravedad (m/s²)

    # Convertir caudal a m³/s
    caudal_m3s = caudal_lps / 1000.0

    # Convertir presión (bar) a altura hidráulica (m)
    # 1 bar = 100000 Pa  -> H = P / (ρ g)
    altura_m = (presion_bar * 100000) / (rho * g)

    # Potencia hidráulica disponible (W)
    potencia_hidraulica = rho * g * caudal_m3s * altura_m

    # --- Parte eléctrica ---
    eficiencia_global = 0.40   # eficiencia global turbina + generador + electrónica
    potencia_electrica = potencia_hidraulica * eficiencia_global

    # Redondear para salida
    potencia_hidraulica = round(potencia_hidraulica, 2)
    potencia_electrica = round(potencia_electrica, 2)

    # --- Guardar en base de datos ---
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

    # Respuesta
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
    """
    Devuelve todo el historial de simulaciones almacenadas.
    """
    db = SessionLocal()
    registros = db.query(RegistroSimulacion).all()

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
