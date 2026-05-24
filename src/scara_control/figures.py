"""
SCARA Control — Geometric Figures Module
==========================================
Defines all geometric figure point sets for the SCARA robot.
Each function returns a list of (x, y) waypoints.
"""

import math
from .config import CENTRO_X, CENTRO_Y
from .kinematics import generar_puntos_circulo


def cuadrado() -> list[tuple[float, float]]:
    """60×60mm square centered on workspace."""
    return [(-30, 170), (30, 170), (30, 230), (-30, 230)]


def rectangulo() -> list[tuple[float, float]]:
    """80×40mm rectangle centered on workspace."""
    return [(-40, 180), (40, 180), (40, 220), (-40, 220)]


def triangulo() -> list[tuple[float, float]]:
    """Equilateral triangle."""
    return [(-30, 175), (30, 175), (0, 227)]


def pentagono() -> list[tuple[float, float]]:
    """Regular pentagon with radius 35mm."""
    radio = 35
    return [
        (CENTRO_X + radio * math.cos(math.radians(90 + i * 72)),
         CENTRO_Y + radio * math.sin(math.radians(90 + i * 72)))
        for i in range(5)
    ]


def circulo() -> list[tuple[float, float]]:
    """Circle with radius 30mm, 48 segments."""
    return generar_puntos_circulo(CENTRO_X, CENTRO_Y, radio=30, segmentos=48)


def letra_a_trazos() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Capital letter 'A'. Returns (outer_stroke, crossbar_stroke)."""
    externo = [(-20, 170), (0, 230), (20, 170)]
    puente = [(-10, 200), (10, 200)]
    return externo, puente


def pista_f1() -> list[tuple[float, float]]:
    """Red Bull Ring (Spielberg) F1 circuit. ~85×80mm footprint."""
    return [
        (-25.0, 165.0), (-20.0, 165.0), (-15.0, 165.0), (-10.0, 165.0),
        (-5.0, 165.0), (0.0, 165.0), (5.0, 165.0), (10.0, 165.0),
        (15.0, 165.0), (20.0, 165.0), (25.0, 165.0), (30.0, 165.0), (35.0, 165.0),
        (38.0, 165.2), (40.5, 165.8), (42.5, 166.8), (44.0, 168.2),
        (44.8, 170.0), (44.5, 172.0), (43.5, 174.0), (42.0, 176.0), (40.5, 178.0),
        (38.0, 181.0), (35.0, 184.6), (32.0, 188.2), (29.0, 191.8),
        (26.0, 195.4), (23.0, 199.0), (20.0, 202.6), (17.0, 206.2),
        (14.0, 209.8), (11.0, 213.4), (8.0, 217.0), (5.0, 220.6),
        (2.0, 224.2), (-1.0, 227.8), (-4.0, 231.4), (-7.0, 235.0),
        (-10.0, 238.6), (-13.0, 242.2),
        (-14.5, 244.0), (-16.5, 245.2), (-18.8, 245.5), (-21.0, 244.8),
        (-22.5, 243.2), (-23.0, 241.0), (-22.2, 238.5), (-20.8, 236.0),
        (-18.5, 233.7), (-16.0, 231.2), (-13.5, 228.7), (-11.0, 226.2),
        (-8.5, 223.7), (-6.0, 221.2), (-3.5, 218.7), (-1.0, 216.2),
        (1.5, 213.7), (4.0, 211.2), (6.5, 208.7), (9.0, 206.2),
        (11.5, 203.7), (14.0, 201.2),
        (16.0, 199.0), (17.5, 196.5), (18.2, 193.5), (18.0, 190.5),
        (17.0, 187.8), (15.5, 185.5), (13.5, 183.5),
        (11.0, 182.0), (8.0, 181.0), (5.0, 180.3), (2.0, 180.0),
        (-1.0, 180.2), (-4.0, 180.8), (-7.0, 181.8),
        (-10.0, 183.0), (-13.0, 184.4), (-16.0, 185.8), (-19.0, 187.0), (-22.0, 187.8),
        (-25.0, 188.0), (-28.0, 187.5), (-31.0, 186.2), (-34.0, 184.0),
        (-36.5, 181.0), (-38.5, 177.5),
        (-39.8, 174.0), (-40.5, 170.5), (-40.0, 167.5), (-38.0, 165.8),
        (-35.0, 165.2), (-32.0, 165.0), (-28.5, 165.0),
        (-25.0, 165.0),
    ]


# Registry of available figures for easy iteration
FIGURAS_DISPONIBLES = {
    "Cuadrado": {"func": cuadrado, "emoji": "⬛", "cerrar": True},
    "Rectángulo": {"func": rectangulo, "emoji": "▭", "cerrar": True},
    "Triángulo": {"func": triangulo, "emoji": "▲", "cerrar": True},
    "Pentágono": {"func": pentagono, "emoji": "⬠", "cerrar": True},
    "Círculo": {"func": circulo, "emoji": "◯", "cerrar": True},
    "Pista F1": {"func": pista_f1, "emoji": "🏎️", "cerrar": True},
}
