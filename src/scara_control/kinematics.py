"""
SCARA Control — Inverse Kinematics Module
==========================================
Implements the 2-link planar inverse kinematics with Denavit-Hartenberg
parameters, gamma correction, and workspace scale compensation.
"""

import math
from typing import Optional, Tuple

from .config import (
    L1, L2, GAMMA, CODO_DERECHO,
    ESCALA_X, ESCALA_Y, CENTRO_X, CENTRO_Y,
)


def calcular_ik(
    x: float,
    y: float,
    l1: float = L1,
    l2: float = L2,
    gamma: float = GAMMA,
    codo_derecho: bool = CODO_DERECHO,
    escala_x: float = ESCALA_X,
    escala_y: float = ESCALA_Y,
    centro_x: float = CENTRO_X,
    centro_y: float = CENTRO_Y,
) -> Tuple[Optional[float], Optional[float]]:
    """Compute inverse kinematics for a 2R planar SCARA arm.

    Transforms Cartesian coordinates (x, y) into machine joint angles
    (q1_machine, q2_machine) using the Denavit-Hartenberg model with
    scale compensation and gamma correction.

    Args:
        x: Target X coordinate in mm (workspace frame).
        y: Target Y coordinate in mm (workspace frame).
        l1: Length of link 1 in mm.
        l2: Effective length of link 2 in mm.
        gamma: Angular offset correction in degrees.
        codo_derecho: If True, use right-elbow configuration.
        escala_x: X-axis scale correction factor.
        escala_y: Y-axis scale correction factor.
        centro_x: Workspace center X coordinate.
        centro_y: Workspace center Y coordinate.

    Returns:
        Tuple of (q1_machine, q2_machine) in degrees, or (None, None)
        if the target point is unreachable.
    """
    # Step 1: Apply scale compensation
    dx = x - centro_x
    dy = y - centro_y
    x_esc = (dx * escala_x) + centro_x
    y_esc = (dy * escala_y) + centro_y

    # Step 2: Compute cosine of q2 via the law of cosines
    d2 = x_esc ** 2 + y_esc ** 2
    D = (d2 - l1 ** 2 - l2 ** 2) / (2 * l1 * l2)

    # Step 3: Check reachability
    if not (-1 <= D <= 1):
        return None, None

    # Step 4: Compute q2 (elbow angle)
    signo_codo = -1 if codo_derecho else 1
    theta2_rad = math.atan2(signo_codo * math.sqrt(1 - D ** 2), D)

    # Step 5: Compute q1 (shoulder angle)
    theta1_rad = math.atan2(y_esc, x_esc) - math.atan2(
        l2 * math.sin(theta2_rad),
        l1 + l2 * math.cos(theta2_rad),
    )

    # Step 6: Convert to machine angles
    q1_maquina = 90.0 - math.degrees(theta1_rad)
    q2_maquina = -q1_maquina + math.degrees(theta2_rad) + gamma

    return q1_maquina, q2_maquina


def generar_puntos_circulo(
    cx: float,
    cy: float,
    radio: float = 30.0,
    segmentos: int = 48,
) -> list[Tuple[float, float]]:
    """Generate evenly-spaced points along a circle.

    Args:
        cx: Center X coordinate.
        cy: Center Y coordinate.
        radio: Circle radius in mm.
        segmentos: Number of points to generate.

    Returns:
        List of (x, y) tuples forming the circle perimeter.
    """
    return [
        (
            cx + radio * math.cos(2 * math.pi * i / segmentos),
            cy + radio * math.sin(2 * math.pi * i / segmentos),
        )
        for i in range(segmentos)
    ]
