from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de la base de datos SQLite (archivo local)
DATABASE_URL = "sqlite:///./simulacion.db"

# Motor de conexión
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Sesión de conexión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para los modelos
Base = declarative_base()


# Modelo de tabla para almacenar las simulaciones
class RegistroSimulacion(Base):
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True, index=True)
    caudal_lps = Column(Float)
    presion_bar = Column(Float)
    potencia_hidraulica_w = Column(Float)
    potencia_electrica_w = Column(Float)


def init_db():
    # Crear las tablas si no existen
    Base.metadata.create_all(bind=engine)
