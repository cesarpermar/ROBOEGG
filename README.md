<div align="center">

# 🤖 ROBOEGG — SCARA 2R Robot

**Sistema de control para brazo robótico SCARA de 2 grados de libertad**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab.svg)](https://python.org)
[![Arduino](https://img.shields.io/badge/Arduino-UNO-00979D.svg)](https://arduino.cc)
[![Spec-Driven](https://img.shields.io/badge/Methodology-Spec--Driven-purple.svg)](specs/001-scara-control-system/spec.md)

</div>

---

## 📋 Descripción

ROBOEGG es un brazo robótico **SCARA** (Selective Compliance Articulated Robot Arm) de 2R construido con impresión 3D, motores NEMA 17 con reducción GT2 (3:1), y controlado desde una interfaz profesional en Python. El sistema es capaz de trazar figuras geométricas sobre papel con precisión de ±2mm.

> Proyecto desarrollado siguiendo la metodología **Spec-Driven Development (SDD)** inspirada en [GitHub Spec Kit](https://github.com/github/spec-kit).

> ### 👉 [QUICKSTART.md — Guía Paso a Paso (empieza aquí)](QUICKSTART.md)
> Firmware → Hardware → Calibración → Dibujar. Todo explicado de cero.

## 🏗️ Arquitectura del Sistema

```
┌──────────────────────────────────────────────────┐
│              OPERADOR (Humano)                    │
└─────────────────────┬────────────────────────────┘
                      │ Click / E-STOP
┌─────────────────────▼────────────────────────────┐
│          GUI Layer (Tkinter Dark Mode)             │
│          src/gui/studio_pro.py                     │
└─────────────────────┬────────────────────────────┘
                      │ Solicitud de figura
┌─────────────────────▼────────────────────────────┐
│          Trajectory Layer                          │
│  figures.py → trajectory.py (interpolación)        │
└─────────────────────┬────────────────────────────┘
                      │ Coordenadas (x, y)
┌─────────────────────▼────────────────────────────┐
│          Kinematics Layer                          │
│  kinematics.py — IK con D-H + γ + escala          │
└─────────────────────┬────────────────────────────┘
                      │ Ángulos (q₁, q₂)
┌─────────────────────▼────────────────────────────┐
│          HAL Layer (Abstracción de Hardware)        │
│  hal.py — Serial I/O + timeout + E-STOP           │
└─────────────────────┬────────────────────────────┘
                      │ "q1,q2,z\n" vía USB Serial
┌─────────────────────▼────────────────────────────┐
│          Firmware Layer (Arduino UNO)               │
│  AccelStepper + Servo (CNC Shield V3)              │
└──────────────────────────────────────────────────┘
```

## ⚙️ Parámetros Denavit-Hartenberg

| Eslabón | θᵢ | dᵢ (mm) | aᵢ (mm) | αᵢ (°) |
|:-------:|:--:|:-------:|:-------:|:------:|
| 1 | q₁ | 0 | 150.0 | 0 |
| 2 | q₂ | 0 | 159.94 | 0 |

- **L₂ efectivo** = √(150² + 55.5²) = 159.94 mm
- **Corrección γ** = 2.0° (offset angular calibrado)
- **Configuración**: Codo derecho

> Documentación completa: [docs/dh_parameters.md](docs/dh_parameters.md)

## 📐 Figuras Soportadas

| Figura | Dimensiones | Segmentos |
|--------|------------|-----------|
| ⬛ Cuadrado | 60 × 60 mm | 4 vértices |
| ▭ Rectángulo | 80 × 40 mm | 4 vértices |
| ▲ Triángulo | Base 60 mm | 3 vértices |
| ⬠ Pentágono | r = 35 mm | 5 vértices |
| ◯ Círculo | r = 30 mm | 48 segmentos |
| A Letra 'A' | 40 × 60 mm | 2 trazos |
| 🏎️ Pista F1 | ~85 × 80 mm | 90+ puntos |

## 🚀 Instalación

### Requisitos Previos

- Python 3.11+
- Arduino IDE (para firmware)
- Hardware: Arduino UNO + CNC Shield V3 + 2× NEMA 17 + SG90S servo

### Configuración

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/ROBOEGG.git
cd ROBOEGG

# 2. Instalar dependencias Python
pip install -r requirements.txt

# 3. Subir firmware al Arduino
# Abrir firmware/scara_2r_controller/scara_2r_controller.ino en Arduino IDE
# Seleccionar: Board → Arduino UNO, Port → tu puerto
# Click: Upload

# 4. Ejecutar la aplicación
python run.py
```

## 🎮 Uso

1. **Conectar**: Selecciona el puerto serial y haz clic en "CONECTAR SISTEMA"
2. **Seleccionar figura**: Haz clic en cualquier botón de figura
3. **Checklist**: Confirma la orientación del brazo y el estado de la fuente
4. **Ejecutar**: El robot traza la figura automáticamente
5. **E-STOP**: En caso de emergencia, presiona el botón rojo

## 📁 Estructura del Proyecto

```
ROBOEGG/
├── .specify/memory/         ← Constitución del proyecto (SDD)
├── specs/                   ← Especificaciones formales
├── src/
│   ├── scara_control/       ← Módulos de control (config, IK, HAL, trayectoria)
│   ├── gui/                 ← Interfaz gráfica Tkinter
│   └── calibration/         ← Herramientas de calibración
├── firmware/                ← Código Arduino
├── docs/                    ← Documentación técnica
├── config/                  ← Perfiles de calibración
├── report/                  ← Reporte LaTeX
├── run.py                   ← Entry point principal
├── pyproject.toml           ← Configuración del proyecto
└── requirements.txt         ← Dependencias Python
```

## 📖 Documentación

| Documento | Descripción |
|-----------|-------------|
| **[🚀 QUICKSTART](QUICKSTART.md)** | **Guía paso a paso: de cero a dibujar** |
| [Especificación del Sistema](specs/001-scara-control-system/spec.md) | Requisitos funcionales y user stories |
| [Plan Técnico](specs/001-scara-control-system/plan.md) | Arquitectura, stack y modelo cinemático |
| [Parámetros D-H](docs/dh_parameters.md) | Tabla formal y derivación cinemática |
| [Guía de Cableado](docs/wiring_guide.md) | Conexiones de hardware |
| [Guía de Calibración](docs/calibration_guide.md) | Procedimiento de alineación |
| [Arquitectura](docs/architecture.md) | Diagrama de bloques del sistema |

## 🛡️ Seguridad

Este proyecto controla hardware robótico real. Lee [SECURITY.md](SECURITY.md) para conocer los mecanismos de seguridad implementados.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Lee [CONTRIBUTING.md](CONTRIBUTING.md) para conocer las convenciones y el proceso.

## 📄 Licencia

Este proyecto está licenciado bajo los términos de la [Licencia MIT](LICENSE).
