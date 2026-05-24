# Spec: SCARA 2R Control System — ROBOEGG

> **Feature ID**: 001-scara-control-system  
> **Status**: Implemented  
> **Created**: 2026-04-15  
> **Last Updated**: 2026-05-24

---

## 1. Overview

ROBOEGG is a SCARA (Selective Compliance Articulated Robot Arm) 2R robotic system designed to trace geometric figures on paper with precision. The robot is built from 3D-printed components, NEMA 17 stepper motors with GT2 belt reduction (3:1), and controlled via an Arduino UNO with CNC Shield V3.

### 1.1 Problem Statement

The course requires building a non-commercial robotic arm capable of tracing specific geometric shapes on paper. The system must demonstrate proficiency in:
- Mechanical design and 3D printing
- Denavit-Hartenberg kinematic modeling
- Trajectory planning and interpolation
- Real-time motor control via serial communication

### 1.2 Objectives

- Trace 6 geometric figures with dimensional accuracy of ±2mm
- Provide a professional GUI for operator control
- Implement safety mechanisms for hardware protection
- Support persistent calibration for workspace alignment

---

## 2. User Stories

### US-01: Geometric Figure Tracing
**As** a robot operator,  
**I want** to select a geometric figure from the GUI and have the robot trace it on paper,  
**So that** I can demonstrate the robot's trajectory planning capabilities.

**Acceptance Criteria:**
- [x] Square (60×60mm) traces correctly
- [x] Rectangle (80×40mm) traces correctly
- [x] Equilateral triangle traces correctly
- [x] Regular pentagon traces correctly
- [x] Circle (r=30mm, 48 segments) traces correctly
- [x] Capital letter "A" with crossbar traces correctly

### US-02: F1 Circuit Tracing
**As** a robot operator,  
**I want** to trace an F1 racing circuit (Red Bull Ring),  
**So that** I can demonstrate complex parametric path capabilities.

**Acceptance Criteria:**
- [x] Circuit renders as continuous closed path
- [x] Spline-like curves at corners are smooth
- [x] Total footprint fits within workspace (~85×80mm)

### US-03: Emergency Stop
**As** a robot operator,  
**I want** to immediately halt all robot motion with a single button press,  
**So that** I can prevent damage in case of unexpected behavior.

**Acceptance Criteria:**
- [x] E-STOP button is prominently displayed in red
- [x] Pressing E-STOP lifts the pen immediately
- [x] All trajectory execution halts within <100ms of press
- [x] Robot holds last position (does not lose steps)

### US-04: Hardware Connection
**As** a robot operator,  
**I want** to select a serial port and connect to the Arduino,  
**So that** I can establish communication before operating the robot.

**Acceptance Criteria:**
- [x] Available COM ports are listed in a dropdown
- [x] Connection status is visually indicated (ONLINE/DISCONNECTED)
- [x] Connection failure shows a clear error message
- [x] On connection, robot moves to safe home position

### US-05: Pre-Flight Checklist
**As** a robot operator,  
**I want** to confirm physical readiness before each figure execution,  
**So that** the robot doesn't move unexpectedly with incorrect arm orientation.

**Acceptance Criteria:**
- [x] Modal dialog appears before each figure
- [x] Two mandatory confirmations: arm orientation + motor power
- [x] Execution is blocked until both are confirmed
- [x] Motor link verification ping is sent after checklist

### US-06: Calibration Sweep
**As** a robot technician,  
**I want** to sweep the arm through 0°–180° with a slider,  
**So that** I can verify joint alignment and adjust the gamma offset.

**Acceptance Criteria:**
- [x] Slider provides continuous angle control
- [x] Quick-position buttons for 0°, 90°, 180°
- [x] Gamma offset is adjustable in increments of ±0.1°, ±1°, ±5°
- [x] Real-time display of current arm angle

---

## 3. Functional Requirements

### FR-01: Inverse Kinematics Engine
- Input: Cartesian coordinates (x, y) in mm
- Output: Joint angles (q1, q2) in degrees for stepper motors
- Model: 2-link planar arm with L1=150mm, L2_eff=159.94mm, γ=2.0°
- Configuration: Right elbow (codo derecho)
- Scale compensation: ESCALA_X = 60/70, ESCALA_Y = 60/50

### FR-02: Linear Interpolation
- Resolution: 1.0 mm per interpolation step
- Method: Linear interpolation between vertices
- UI update: Every 3 steps to prevent GUI freezing

### FR-03: Serial Protocol
- Baud rate: 115200
- Format: `{q1:.2f},{q2:.2f},{z}\n`
- z values: 0=pen up, 1=pen down
- Response: `OK` on completion, `ERR` on parse failure
- Timeout: 15 seconds per command

### FR-04: Pen Control (Z-Axis)
- Actuator: SG90S servo motor
- Up position: 90° (pen lifted)
- Down position: 135° (pen on paper)
- Transition delay: 80ms (up), 90ms (down)

---

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | GUI response time | <50ms for button clicks |
| NFR-02 | Serial latency | <500ms per command round-trip |
| NFR-03 | E-STOP response | <100ms from button press to pen lift |
| NFR-04 | Dimensional accuracy | ±2mm on 60mm reference square |
| NFR-05 | Repeatability | <1mm deviation across 3 consecutive runs |

---

## 5. Data Model

### Calibration Profile Schema (`config/calibration_profile.json`)

```json
{
  "workspace": {
    "offset_x": 0.0,
    "offset_y": 0.0,
    "escala_x": 1.0,
    "escala_y": 1.0,
    "rotacion_grados": 0.0
  },
  "angulos": {
    "q1_gain": 1.0,
    "q2_gain": 1.0,
    "q1_offset": 0.0,
    "q2_offset": 0.0
  },
  "movimiento": {
    "pasos_dibujo": 20,
    "pasos_traslado": 2,
    "timeout_movimiento": 15.0
  }
}
```

---

## 6. System Architecture

```
┌──────────────────────────────────────────────────────┐
│                    OPERATOR (Human)                   │
└────────────────────────┬─────────────────────────────┘
                         │ Click / E-STOP
┌────────────────────────▼─────────────────────────────┐
│              GUI Layer (Tkinter)                      │
│  studio_pro.py — Dark mode, CNC aesthetic            │
└────────────────────────┬─────────────────────────────┘
                         │ Figure request
┌────────────────────────▼─────────────────────────────┐
│           Trajectory Layer                            │
│  figures.py → trajectory.py (interpolation)          │
└────────────────────────┬─────────────────────────────┘
                         │ Cartesian (x, y)
┌────────────────────────▼─────────────────────────────┐
│           Kinematics Layer                            │
│  kinematics.py — IK with D-H + gamma + scale         │
└────────────────────────┬─────────────────────────────┘
                         │ Joint angles (q1, q2)
┌────────────────────────▼─────────────────────────────┐
│           HAL Layer (Hardware Abstraction)            │
│  hal.py — Serial I/O + timeout + E-STOP check        │
└────────────────────────┬─────────────────────────────┘
                         │ "q1,q2,z\n" via USB Serial
┌────────────────────────▼─────────────────────────────┐
│           Firmware Layer (Arduino)                    │
│  scara_2r_controller.ino — AccelStepper + Servo      │
└──────────────────────────────────────────────────────┘
```

---

## 7. Review & Acceptance Checklist

- [x] All user stories have clear acceptance criteria
- [x] Functional requirements are complete and testable
- [x] Non-functional requirements have measurable targets
- [x] Data model is formally specified
- [x] Architecture is documented with layer boundaries
- [x] Safety requirements are explicitly defined
- [x] Serial protocol is fully specified
