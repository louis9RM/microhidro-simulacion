# ⚡ Microhidro-Simulacion (Simulador Hidráulico–Eléctrico)

Un sistema de simulación académico que modela el comportamiento hidráulico y eléctrico de una microcentral hidroeléctrica. Permite experimentar con caudal, presión, altura hidráulica y eficiencia global para estimar potencia útil generada.

Este proyecto combina **FastAPI**, **SQLite**, y un **dashboard web moderno** con **Chart.js** para visualización en tiempo real.

---

## 🎯 Objetivos del proyecto

- Modelar la cadena energética: agua → turbina → generador → potencia eléctrica.
- Registrar todas las simulaciones en una base de datos.
- Visualizar datos en un dashboard moderno estilo industrial/IoT.
- Mostrar resultados numéricos y tendencias mediante gráficos.

---

## 🧩 Arquitectura del Sistema

| Módulo | Tecnología | Descripción |
|--------|------------|-------------|
| Backend | Python + FastAPI | Realiza cálculos hidráulicos/eléctricos y expone API REST |
| Base de datos | SQLite + SQLAlchemy | Guarda el historial de simulaciones |
| Frontend | HTML + CSS + JS + Chart.js | Interfaz gráfica moderna con visualización en tiempo real |

---

## 📌 Fórmulas aplicadas

### **1. Caudal**
\[
Q = \text{litros/segundo} / 1000
\]

### **2. Altura hidráulica equivalente**
\[
H = \frac{P \cdot 100000}{\rho g}
\]

### **3. Potencia hidráulica**
\[
P_h = \rho \cdot g \cdot Q \cdot H
\]

### **4. Potencia eléctrica generada**
\[
P_e = P_h \cdot \eta
\]

---

## 🚀 Cómo ejecutar

```bash
git clone https://github.com/<TU-USUARIO>/microhidro-simulacion
cd microhidro-simulacion

# Activar entorno
python -m venv venv
.\venv\Scripts\activate

# Iniciar backend
uvicorn main:app --reload
