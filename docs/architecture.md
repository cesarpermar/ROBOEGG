# Arquitectura del Sistema — ROBOEGG SCARA 2R

## Diagrama de Bloques

```
┌─────────────────────────────────────────────────────────────┐
│                        PC (Host)                             │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  studio_pro   │───▶│   safety     │───▶│     hal       │  │
│  │  (GUI Layer)  │    │  (E-STOP,    │    │  (Serial I/O) │  │
│  │              │    │  Checklist)  │    │              │  │
│  └──────┬───────┘    └──────────────┘    └──────┬────────┘  │
│         │                                        │           │
│  ┌──────▼───────┐    ┌──────────────┐           │           │
│  │  trajectory   │───▶│  kinematics  │           │           │
│  │  (Interpola-  │    │  (IK + D-H)  │           │           │
│  │   ción)       │    └──────────────┘           │           │
│  └──────┬───────┘                                │           │
│         │                                        │           │
│  ┌──────▼───────┐    ┌──────────────┐           │           │
│  │   figures     │    │   config     │◀──────────┘           │
│  │  (Geometría)  │    │  (Constantes)│                       │
│  └──────────────┘    └──────────────┘                       │
│                                                              │
└──────────────────────────────┬───────────────────────────────┘
                               │ USB Serial (115200 baud)
                               │ Protocolo: "q1,q2,z\n" → "OK\n"
┌──────────────────────────────▼───────────────────────────────┐
│                    Arduino UNO + CNC Shield V3                │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────┐   │
│  │ Serial Parser │───▶│ AccelStepper │───▶│  NEMA 17 (×2) │   │
│  │              │    │ (Dual axis)  │    │  + GT2 3:1    │   │
│  │              │    └──────────────┘    └───────────────┘   │
│  │              │                                            │
│  │              │    ┌──────────────┐    ┌───────────────┐   │
│  │              │───▶│ Servo Control │───▶│  SG90S (Z)    │   │
│  └──────────────┘    └──────────────┘    └───────────────┘   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

1. **Operador** selecciona una figura en la GUI
2. **Safety** ejecuta checklist pre-vuelo y verifica enlace de motores
3. **Figures** proporciona los vértices de la figura seleccionada
4. **Trajectory** interpola linealmente entre vértices a resolución de 1mm
5. **Kinematics** convierte cada punto (x,y) a ángulos articulares (q₁, q₂)
6. **HAL** formatea el comando serial y lo envía al Arduino
7. **Firmware** parsea el comando, mueve los steppers y responde "OK"

## Capas y Responsabilidades

| Capa | Módulo | Responsabilidad |
|------|--------|----------------|
| Presentación | `src/gui/studio_pro.py` | Interfaz de usuario, botones, status |
| Seguridad | `src/scara_control/safety.py` | E-STOP, checklist, validación |
| Trayectoria | `src/scara_control/trajectory.py` | Interpolación lineal, ejecución de paths |
| Cinemática | `src/scara_control/kinematics.py` | Cinemática inversa D-H |
| Figuras | `src/scara_control/figures.py` | Definiciones geométricas |
| HAL | `src/scara_control/hal.py` | Comunicación serial, protocolo OK-wait |
| Configuración | `src/scara_control/config.py` | Constantes centralizadas |
| Firmware | `firmware/scara_2r_controller/` | Control de motores y servo |
