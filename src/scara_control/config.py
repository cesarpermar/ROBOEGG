"""
SCARA Control — Configuration Module
=====================================
Centralized constants, calibration parameters, and UI theme colors
for the ROBOEGG SCARA 2R robotic system.
"""

import math

# ============================================================================
# ROBOT GEOMETRY — Denavit-Hartenberg Parameters
# ============================================================================

L1: float = 150.0
"""Length of link 1 (shoulder to elbow) in mm."""

L2: float = 159.94
"""Effective length of link 2 (elbow to end-effector) in mm.
Computed as sqrt(150² + 55.5²) to account for the end-effector offset."""

GAMMA: float = -5
"""Angular offset correction (degrees) for the elbow joint.
Compensates geometric misalignment between the motor axis and the link."""

CODO_DERECHO: bool = True
"""Elbow configuration. True = right elbow (signo_codo = -1)."""

# ============================================================================
# WORKSPACE CALIBRATION
# ============================================================================

RESOLUCION_MM: float = 1.0
"""Interpolation resolution in mm. Smaller = smoother but slower."""

ESCALA_X: float = 60.0 / 70.0
"""X-axis scale correction factor. Ratio of desired/actual dimension."""

ESCALA_Y: float = 60.0 / 50.0
"""Y-axis scale correction factor. Ratio of desired/actual dimension."""

K_TRAPEZOID: float = 0.0008
"""Trapezoidal correction coefficient to compensate for X scale variation with Y.
A positive value expands X coordinates at higher Y values.
Formula: scale_x_dynamic = escala_x * (1.0 + K_TRAPEZOID * (y - 170.0))"""

CENTRO_X: float = 0.0
"""Workspace center X coordinate in mm."""

CENTRO_Y: float = 200.0
"""Workspace center Y coordinate in mm."""

# ============================================================================
# SERIAL COMMUNICATION
# ============================================================================

BAUDRATE: int = 115200
"""Serial baud rate for Arduino communication."""

SERIAL_TIMEOUT: float = 0.5
"""Serial port read timeout in seconds."""

MOVEMENT_TIMEOUT: float = 15.0
"""Maximum wait time for an 'OK' response from Arduino in seconds."""

# ============================================================================
# UI THEME — Professional CNC Dark Mode
# ============================================================================

BG_COLOR: str = "#1E1E1E"
"""Main background color (dark gray)."""

PANEL_COLOR: str = "#2D2D30"
"""Panel/frame background color."""

TEXT_COLOR: str = "#FFFFFF"
"""Primary text color (white)."""

ACCENT_COLOR: str = "#007ACC"
"""Accent color for highlights and active states (VS Code blue)."""

SUCCESS_COLOR: str = "#28A745"
"""Success/online indicator color (green)."""

DANGER_COLOR: str = "#DC3545"
"""Emergency/danger indicator color (red)."""

FONT_FAMILY: str = "Segoe UI"
"""Primary font family for the GUI."""
