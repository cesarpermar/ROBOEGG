# Plan: SCARA 2R Control System — Technical Implementation

> **Feature ID**: 001-scara-control-system  
> **Status**: Implemented  
> **Created**: 2026-05-24

---

## 1. Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| GUI | Python + Tkinter | 3.11+ |
| Control Logic | Python | 3.11+ |
| Serial Communication | pyserial | ≥3.5 |
| Math | Python math (stdlib) | — |
| Firmware | Arduino C++ (AccelStepper + Servo) | — |
| Hardware | Arduino UNO + CNC Shield V3 + A4988 drivers | — |
| Motors | NEMA 17 × 2 (X-Y) + SG90S servo (Z) | — |
| Transmission | GT2 belt + 20T/60T pulleys (3:1 reduction) | — |

## 2. Kinematic Model

### 2.1 Denavit-Hartenberg Parameters

| Link | θᵢ | dᵢ (mm) | aᵢ (mm) | αᵢ (°) |
|------|----|---------|---------|--------|
| 1 | q₁ | 0 | 150.0 | 0 |
| 2 | q₂ | 0 | 159.94 | 0 |

### 2.2 Geometric Corrections

- **L₂ effective** = √(150² + 55.5²) = 159.94 mm (accounts for end-effector offset)
- **γ (gamma)** = atan2(55.5, 150) ≈ 20.30° (original) → 2.0° (calibrated in SCARA.py)
- **Scale factors**: X = 60/70 ≈ 0.857, Y = 60/50 = 1.200

### 2.3 Inverse Kinematics Algorithm

```
Input: (x, y) Cartesian coordinates
Output: (q1_machine, q2_machine) joint angles in degrees

1. Apply scale compensation:
   x_esc = (x - Cx) * ESCALA_X + Cx
   y_esc = (y - Cy) * ESCALA_Y + Cy

2. Compute cosine of q2:
   D = (x_esc² + y_esc² - L1² - L2²) / (2·L1·L2)

3. If |D| > 1 → point unreachable, return None

4. Compute q2 (right elbow):
   q2 = atan2(-√(1 - D²), D)

5. Compute q1:
   q1 = atan2(y_esc, x_esc) - atan2(L2·sin(q2), L1 + L2·cos(q2))

6. Convert to machine angles:
   q1_machine = 90° - q1
   q2_machine = -q1_machine + q2 + γ
```

## 3. Module Architecture

```
src/
├── scara_control/
│   ├── __init__.py          # Package exports
│   ├── config.py            # All constants, colors, parameters
│   ├── kinematics.py        # IK computation (calcular_hal)
│   ├── hal.py               # Serial I/O (enviar_comando)
│   ├── trajectory.py        # Interpolation engine (trazar_linea, ejecutar_trayectoria)
│   ├── safety.py            # Zone check, E-STOP, checklist, motor verify
│   └── figures.py           # Figure point definitions
├── gui/
│   ├── __init__.py
│   └── studio_pro.py        # Tkinter GUI class (ScaraMasterPro)
└── calibration/
    ├── __init__.py
    └── sweep_180.py          # Calibration sweep app (ScaraSyncApp)
```

### Dependency Graph

```
GUI ──depends──▶ safety ──depends──▶ hal ──depends──▶ config
  │                                    │
  └──depends──▶ trajectory             └──depends──▶ kinematics ──depends──▶ config
                    │
                    └──depends──▶ figures ──depends──▶ config
```

## 4. Firmware Architecture

### Communication Protocol

```
PC → Arduino:  "{q1:.2f},{q2:.2f},{z}\n"    (ASCII text)
Arduino → PC:  "OK\n" | "ERR\n" | "READY\n" (ASCII text)
```

### Motor Configuration

- Steps per revolution: 200 (1.8°/step)
- Microstepping: 1/16 (via jumpers M0, M1, M2)
- Gear reduction: 3:1 (20T → 60T)
- **Effective steps/revolution**: 200 × 16 × 3 = **9600**
- **Steps/degree**: 9600 / 360 = **26.667**

### Motion Parameters

| Parameter | Motor 1 (Shoulder) | Motor 2 (Elbow) |
|-----------|--------------------|------------------|
| Max Speed | 900 steps/s | 900 steps/s |
| Acceleration | 1200 steps/s² | 1200 steps/s² |

## 5. Research Notes

### Validated Design Decisions

1. **AccelStepper library**: Chosen for synchronized multi-axis motion with acceleration profiles
2. **GT2 belt + 3:1 reduction**: Provides sufficient torque for NEMA 17 with smooth motion
3. **CNC Shield V3**: Cost-effective stepper driver interface with built-in microstepping jumpers
4. **Tkinter over web UI**: Lower latency for real-time serial communication, no network overhead
5. **Right elbow configuration**: Maximizes reachable workspace for the paper surface placement
