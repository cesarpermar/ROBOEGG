# ROBOEGG — Project Constitution

> This document defines the governing principles for the ROBOEGG SCARA robot project.
> All development decisions, code changes, and architectural choices must align with these principles.

---

## 1. Safety First (Seguridad Primero)

Every function that commands hardware motion **must** validate the target position against the robot's safe workspace before execution. No motor command shall be sent without passing safety checks.

- **Zone validation**: All Cartesian points must be checked against radial limits (min/max reach)
- **Emergency stop**: The E-STOP mechanism must be responsive and immediate — it lifts the pen and halts all motion
- **Timeout protection**: Serial communication must enforce timeouts to prevent indefinite blocking
- **Pre-flight checklist**: Before any figure execution, the operator must confirm physical readiness

## 2. Deterministic Kinematics (Cinemática Determinista)

All kinematic calculations must be:
- **Reproducible**: Same input coordinates must always produce the same joint angles
- **Documented**: The Denavit-Hartenberg parameters, gamma correction, and scale factors must be formally documented
- **Validated**: Any change to the kinematic model requires verification against known reference points

## 3. Modular Architecture (Arquitectura Modular)

The system is organized in **decoupled layers**:

```
┌─────────────┐
│     GUI     │  ← User interaction only
├─────────────┤
│  Trajectory │  ← Path planning & interpolation
├─────────────┤
│ Kinematics  │  ← Inverse kinematics (IK)
├─────────────┤
│     HAL     │  ← Hardware Abstraction Layer
├─────────────┤
│  Firmware   │  ← Arduino motor control
└─────────────┘
```

- Each layer communicates only with its immediate neighbors
- The GUI must never compute kinematics directly
- The HAL must never know about figure geometry

## 4. Persistent Calibration (Calibración Persistente)

All physical calibration parameters are stored in a versioned JSON profile:
- Scale factors (X, Y)
- Workspace offsets
- Angular corrections (gamma)
- Servo limits

The calibration profile must be loaded at startup and never hardcoded in multiple places.

## 5. Communication Protocol Integrity (Integridad del Protocolo)

The serial protocol between Python and Arduino follows a strict request-response pattern:
- **Command format**: `q1,q2,z\n` (joint angles in degrees, pen state)
- **Response**: `OK` on completion, `ERR` on invalid input
- Every command must wait for acknowledgment before sending the next one
- No fire-and-forget commands are allowed

## 6. Code Quality Standards (Estándares de Calidad)

- All Python files must include module-level docstrings
- Functions must have type hints and brief docstrings
- Constants must be named in UPPER_SNAKE_CASE
- No magic numbers — all values must be named constants
- Commits follow Conventional Commits format: `type(scope): description`

## 7. Documentation as Code (Documentación como Código)

- The README must be the entry point for any new contributor
- D-H parameters must be documented as a formal table, not just in code comments
- Architecture diagrams must be maintained alongside the code
- The CHANGELOG must be updated with every significant change
