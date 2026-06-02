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
    K_TRAPEZOID,
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
    k_trapezoid: float = K_TRAPEZOID,
) -> Tuple[Optional[float], Optional[float]]:
    """Compute inverse kinematics for a 2R planar SCARA arm.

    Transforms Cartesian coordinates (x, y) into machine joint angles
    (q1_machine, q2_machine) using the Denavit-Hartenberg model with
    scale compensation, gamma correction, and dynamic trapezoidal skew adjustment.

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
        k_trapezoid: Trapezoidal correction coefficient.

    Returns:
        Tuple of (q1_machine, q2_machine) in degrees, or (None, None)
        if the target point is unreachable.
    """
    # Step 1: Apply scale and trapezoidal compensation
    dx = x - centro_x
    dy = y - centro_y
    scale_x_dynamic = escala_x * (1.0 + k_trapezoid * (y - 170.0))
    x_esc = (dx * scale_x_dynamic) + centro_x
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


import numpy as np

def matriz_dh(theta_deg: float, d: float, a: float, alpha_deg: float) -> np.ndarray:
    """Compute standard Denavit-Hartenberg transformation matrix (4x4)."""
    th = math.radians(theta_deg)
    al = math.radians(alpha_deg)
    return np.array([
        [math.cos(th), -math.sin(th) * math.cos(al), math.sin(th) * math.sin(al), a * math.cos(th)],
        [math.sin(th),  math.cos(th) * math.cos(al), -math.cos(th) * math.sin(al), a * math.sin(th)],
        [0,             math.sin(al),                math.cos(al),               d],
        [0,             0,                           0,                          1]
    ])


def analizar_punto_dh(
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
    k_trapezoid: float = K_TRAPEZOID,
) -> Optional[dict]:
    """Perform a complete Denavit-Hartenberg analytical study of a target point.

    Computes inverse kinematics, converts to ideal angles theta1/theta2,
    builds the local T01/T12 and total transformation matrices, and
    performs forward kinematics verification (Xfk, Yfk).
    """
    # 1. Apply scale and trapezoidal compensation
    dx = x - centro_x
    dy = y - centro_y
    scale_x_dynamic = escala_x * (1.0 + k_trapezoid * (y - 170.0))
    x_esc = (dx * scale_x_dynamic) + centro_x
    y_esc = (dy * escala_y) + centro_y

    # 2. Inverse kinematics for theta1/theta2 (ideal coordinate frame)
    d_cos = (x_esc**2 + y_esc**2 - l1**2 - l2**2) / (2 * l1 * l2)
    if not (-1 <= d_cos <= 1):
        return None

    signo = -1 if codo_derecho else 1
    theta2_rad = math.atan2(signo * math.sqrt(1 - d_cos**2), d_cos)
    theta1_rad = math.atan2(y_esc, x_esc) - math.atan2(
        l2 * math.sin(theta2_rad),
        l1 + l2 * math.cos(theta2_rad)
    )

    theta1_deg = math.degrees(theta1_rad)
    theta2_deg = math.degrees(theta2_rad)

    # 3. Compute machine angles (what we actually send over serial)
    q1_maquina = 90.0 - theta1_deg
    q2_maquina = -q1_maquina + theta2_deg + gamma

    # 4. Denavit-Hartenberg Matrices
    T01 = matriz_dh(theta1_deg, 0.0, l1, 0.0)
    T12 = matriz_dh(theta2_deg, 0.0, l2, 0.0)
    T_total = np.dot(T01, T12)

    # 5. Forward Kinematics verification (from T_total translation components)
    x_fk = T_total[0, 3]
    y_fk = T_total[1, 3]

    return {
        "x_obj": x,
        "y_obj": y,
        "x_esc": x_esc,
        "y_esc": y_esc,
        "theta1": theta1_deg,
        "theta2": theta2_deg,
        "q1": q1_maquina,
        "q2": q2_maquina,
        "x_fk": x_fk,
        "y_fk": y_fk,
        "T01": T01,
        "T12": T12,
        "T": T_total,
    }

