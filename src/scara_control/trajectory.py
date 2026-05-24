"""
SCARA Control — Trajectory Module
===================================
Provides linear interpolation and trajectory execution for
multi-segment paths. Handles pen up/down transitions and
closed-path looping.
"""

import math
import time
import tkinter as tk
from typing import Optional

from .config import RESOLUCION_MM, CENTRO_X, CENTRO_Y, ACCENT_COLOR, SUCCESS_COLOR
from .hal import HardwareInterface


class TrajectoryEngine:
    """Executes multi-point trajectories on the SCARA robot.

    Manages linear interpolation between waypoints, pen state
    transitions, and provides status callbacks for the GUI.

    Args:
        hal: Hardware interface for sending commands.
        gui: Optional Tkinter root for UI updates during long operations.
    """

    def __init__(
        self, hal: HardwareInterface, gui: Optional[tk.Tk] = None
    ) -> None:
        self.hal = hal
        self.gui = gui

    def trazar_linea(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """Interpolate a straight line between two points.

        Generates intermediate points at RESOLUCION_MM spacing and
        sends each as a pen-down command to the HAL.

        Args:
            x1, y1: Start point coordinates in mm.
            x2, y2: End point coordinates in mm.
        """
        distancia = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        pasos = max(1, int(distancia / RESOLUCION_MM))

        for i in range(1, pasos + 1):
            if self.hal.detener_emergencia:
                break
            t = i / pasos
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            self.hal.enviar_comando(x, y, z=1)

            # Update GUI periodically to prevent freezing
            if self.gui and i % 3 == 0:
                self.gui.update()

    def ejecutar_trayectoria(
        self,
        nombre: str,
        puntos: list[tuple[float, float]],
        cerrarlo: bool = True,
        callback_estado: Optional[callable] = None,
    ) -> None:
        """Execute a complete trajectory from a list of waypoints.

        Sequence:
        1. Move to first point (pen up)
        2. Lower pen
        3. Trace lines between consecutive points
        4. Optionally close the path (last → first point)
        5. Lift pen and return to home position

        Args:
            nombre: Display name of the figure (for status updates).
            puntos: List of (x, y) waypoints in mm.
            cerrarlo: If True, trace a closing segment from last to first point.
            callback_estado: Optional function(text, color) for status updates.
        """
        if not self.hal.conectado:
            return

        self.hal.detener_emergencia = False

        if callback_estado:
            callback_estado(f"EJECUTANDO: {nombre}...", ACCENT_COLOR)

        # Move to start position (pen up)
        self.hal.enviar_comando(puntos[0][0], puntos[0][1], z=0)
        time.sleep(0.3)

        # Lower pen
        self.hal.enviar_comando(puntos[0][0], puntos[0][1], z=1)

        # Trace between consecutive points
        for i in range(len(puntos) - 1):
            if self.hal.detener_emergencia:
                break
            self.trazar_linea(
                puntos[i][0], puntos[i][1],
                puntos[i + 1][0], puntos[i + 1][1],
            )

        # Close path if requested
        if cerrarlo and not self.hal.detener_emergencia:
            self.trazar_linea(
                puntos[-1][0], puntos[-1][1],
                puntos[0][0], puntos[0][1],
            )

        # Return to home position
        if not self.hal.detener_emergencia:
            self.hal.enviar_comando(puntos[-1][0], puntos[-1][1], z=0)
            self.hal.enviar_comando(CENTRO_X, CENTRO_Y - 40, z=0)
            if callback_estado:
                callback_estado("TAREA COMPLETADA EXITOSAMENTE", SUCCESS_COLOR)
