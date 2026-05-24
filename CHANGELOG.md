# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-24

### Added
- **Project restructuring** under Spec-Driven Development (SDD) philosophy
- Modular Python package `src/scara_control/` with decoupled layers:
  - `config.py` — Centralized constants and calibration parameters
  - `kinematics.py` — Inverse kinematics with D-H model and gamma correction
  - `hal.py` — Hardware Abstraction Layer for serial communication
  - `trajectory.py` — Linear interpolation engine for path planning
  - `safety.py` — Workspace validation, E-STOP, and pre-flight checklist
  - `figures.py` — Geometric figure definitions (square, rectangle, triangle, pentagon, circle, letter A, F1 track)
- GUI module `src/gui/studio_pro.py` — Tkinter professional dark-mode interface
- Calibration module `src/calibration/sweep_180.py` — Rigid arm sweep tool
- Formal specification documents in `specs/001-scara-control-system/`
- Project constitution in `.specify/memory/constitution.md`
- Technical documentation: D-H parameters, architecture, wiring guide, calibration guide
- Governance documents: LICENSE (MIT), CONTRIBUTING, CODE_OF_CONDUCT, SECURITY
- Professional README with badges, architecture diagram, and usage instructions

### Changed
- Reorganized flat file structure into layered modular architecture
- Renamed `arduino_scara_firmware/` → `firmware/scara_2r_controller/`
- Moved context documents to `docs/legacy/` for historical reference
- Moved report files to `report/`

### Deprecated
- Legacy monolithic `SCARA.py` (preserved in root for backward compatibility, use `run.py` instead)

## [0.1.0] — 2026-04-15

### Added
- Initial `SCARA.py` monolithic control application
- `180°.py` calibration sweep tool
- Arduino firmware for SCARA 2R + Servo Z
- Basic README with project requirements
- Context documents with electronics instructions and calibration notes
