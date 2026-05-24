"""
SCARA Control — Core Package
==============================
Modular control system for the ROBOEGG SCARA 2R robot.
"""

from .config import L1, L2, GAMMA, CENTRO_X, CENTRO_Y
from .kinematics import calcular_ik, generar_puntos_circulo
from .hal import HardwareInterface
from .trajectory import TrajectoryEngine

__all__ = [
    "L1", "L2", "GAMMA", "CENTRO_X", "CENTRO_Y",
    "calcular_ik", "generar_puntos_circulo",
    "HardwareInterface", "TrajectoryEngine",
]
