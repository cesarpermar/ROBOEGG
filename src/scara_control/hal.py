"""
SCARA Control — Hardware Abstraction Layer (HAL)
=================================================
Manages serial communication with the Arduino firmware.
Provides a clean interface for sending joint angle commands
and receiving acknowledgments.
"""

import time
from typing import Optional

import serial
import serial.tools.list_ports

from .config import BAUDRATE, SERIAL_TIMEOUT
from .kinematics import calcular_ik


class HardwareInterface:
    """Abstraction layer for the SCARA robot hardware.

    Handles serial port connection, command dispatch with OK-wait
    protocol, and emergency stop integration.

    Attributes:
        serial_port: Active serial connection (None if disconnected).
        last_q1: Last sent q1 angle (for E-STOP safe positioning).
        last_q2: Last sent q2 angle (for E-STOP safe positioning).
        detener_emergencia: Emergency stop flag.
    """

    def __init__(self) -> None:
        self.serial_port: Optional[serial.Serial] = None
        self.last_q1: float = 0.0
        self.last_q2: float = 0.0
        self.detener_emergencia: bool = False
        self.on_move_callback: Optional[callable] = None

    @staticmethod
    def listar_puertos() -> list[str]:
        """List all available serial ports.

        Returns:
            List of port device names (e.g., ['/dev/ttyUSB0', 'COM3']).
        """
        return [p.device for p in serial.tools.list_ports.comports()]

    def conectar(self, puerto: str) -> None:
        """Open a serial connection to the Arduino.

        Args:
            puerto: Serial port name (e.g., '/dev/ttyUSB0' or 'COM3').

        Raises:
            serial.SerialException: If the port cannot be opened.
        """
        self.serial_port = serial.Serial(
            puerto, BAUDRATE, timeout=SERIAL_TIMEOUT
        )
        time.sleep(2)  # Wait for Arduino reset

    def desconectar(self) -> None:
        """Close the serial connection if open."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_port = None

    @property
    def conectado(self) -> bool:
        """Check if the serial port is connected and open."""
        return self.serial_port is not None and self.serial_port.is_open

    def enviar_comando(self, x: float, y: float, z: int) -> bool:
        """Send a motion command to the robot.

        Computes inverse kinematics for the target (x, y) position,
        formats the command string, sends it over serial, and waits
        for the 'OK' acknowledgment.

        Args:
            x: Target X coordinate in mm.
            y: Target Y coordinate in mm.
            z: Pen state (0=up, 1=down).

        Returns:
            True if the command was sent and acknowledged, False otherwise.
        """
        if not self.serial_port or self.detener_emergencia:
            return False

        q1, q2 = calcular_ik(x, y)
        if q1 is None:
            return False

        # Store last position for safe E-STOP recovery
        self.last_q1 = q1
        self.last_q2 = q2

        if self.on_move_callback:
            try:
                self.on_move_callback(x, y, q1, q2, z)
            except Exception:
                pass

        comando = f"{q1:.2f},{q2:.2f},{z}\n"
        self.serial_port.write(comando.encode("ascii"))

        # Wait for acknowledgment
        while not self.detener_emergencia:
            if self.serial_port.in_waiting:
                resp = self.serial_port.readline().decode("ascii").strip()
                if resp == "OK":
                    break
        return True

    def enviar_angulos_directos(
        self, q1: float, q2: float, z: int
    ) -> None:
        """Send raw joint angles without computing IK.

        Used by the E-STOP to command the last known position
        and by calibration tools for direct joint control.

        Args:
            q1: Joint 1 angle in degrees.
            q2: Joint 2 angle in degrees.
            z: Pen state (0=up, 1=down).
        """
        if not self.serial_port:
            return
        comando = f"{q1:.2f},{q2:.2f},{z}\n"
        self.serial_port.write(comando.encode("ascii"))

    def verificar_enlace(self, timeout_s: float = 1.5) -> bool:
        """Verify that motors respond to commands.

        Sends a ping command (last position, pen up) and waits
        for an 'OK' response within the timeout.

        Args:
            timeout_s: Maximum wait time in seconds.

        Returns:
            True if motors responded, False otherwise.
        """
        if not self.serial_port:
            return False
        try:
            self.serial_port.reset_input_buffer()
            comando = f"{self.last_q1:.2f},{self.last_q2:.2f},0\n"
            self.serial_port.write(comando.encode("ascii"))

            inicio = time.time()
            while (time.time() - inicio) < timeout_s:
                if self.serial_port.in_waiting:
                    resp = (
                        self.serial_port.readline()
                        .decode("ascii", errors="ignore")
                        .strip()
                    )
                    if resp == "OK":
                        return True
            return False
        except Exception:
            return False
