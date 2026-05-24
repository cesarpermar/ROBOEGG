"""
SCARA Studio Pro — Professional GUI
=====================================
Dark-mode Tkinter interface for the ROBOEGG SCARA robot.
Provides figure selection, hardware connection, and E-STOP controls.
"""

import time
import tkinter as tk
from tkinter import messagebox

from src.scara_control.config import (
    BG_COLOR, PANEL_COLOR, TEXT_COLOR, ACCENT_COLOR,
    SUCCESS_COLOR, DANGER_COLOR, FONT_FAMILY,
    CENTRO_X, CENTRO_Y,
)
from src.scara_control.hal import HardwareInterface
from src.scara_control.trajectory import TrajectoryEngine
from src.scara_control.safety import ejecutar_estop, solicitar_checklist
from src.scara_control.figures import (
    cuadrado, rectangulo, triangulo, pentagono, circulo,
    letra_a_trazos, pista_f1,
)


class ScaraMasterPro(tk.Tk):
    """Main application window for SCARA robot control.

    Integrates all control modules into a professional CNC-style
    dark-mode interface with figure selection, connection management,
    and emergency stop capabilities.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("SCARA STUDIO PRO — Control Master")
        self.geometry("650x550")
        self.configure(bg=BG_COLOR)

        self.hal = HardwareInterface()
        self.traj = TrajectoryEngine(self.hal, gui=self)

        self._construir_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _crear_panel(self, padre, titulo: str) -> tk.LabelFrame:
        """Create a styled panel frame."""
        marco = tk.LabelFrame(
            padre, text=titulo, bg=PANEL_COLOR, fg=ACCENT_COLOR,
            font=(FONT_FAMILY, 10, "bold"), bd=1, padx=15, pady=15,
        )
        marco.pack(fill=tk.X, padx=20, pady=10)
        return marco

    def _btn(self, padre, texto: str, comando, color=ACCENT_COLOR, ancho=20) -> tk.Button:
        """Create a styled button."""
        return tk.Button(
            padre, text=texto, command=comando, bg=color, fg="white",
            font=(FONT_FAMILY, 10, "bold"), relief=tk.FLAT,
            activebackground="white", activeforeground=color, width=ancho,
        )

    def _construir_ui(self) -> None:
        """Build the complete GUI layout."""
        # Header
        tk.Label(self, text="SCARA STUDIO PRO", bg=BG_COLOR, fg="white",
                 font=(FONT_FAMILY, 16, "bold"), pady=10).pack()

        # Connection panel
        panel_conn = self._crear_panel(self, " CONEXIÓN DE HARDWARE ")
        self.cb_ports = tk.StringVar()
        puertos = self.hal.listar_puertos()

        if puertos:
            menu_puertos = tk.OptionMenu(panel_conn, self.cb_ports, *puertos)
            self.cb_ports.set(puertos[0])
        else:
            menu_puertos = tk.Label(panel_conn, text="Sin puertos",
                                    bg=PANEL_COLOR, fg="red")

        menu_puertos.config(bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, 9))
        menu_puertos.pack(side=tk.LEFT, padx=10)

        self._btn(panel_conn, "CONECTAR SISTEMA", self.conectar,
                  color=SUCCESS_COLOR).pack(side=tk.LEFT, padx=10)

        self.lbl_status = tk.Label(
            panel_conn, text="DESCONECTADO", bg=PANEL_COLOR,
            fg=TEXT_COLOR, font=(FONT_FAMILY, 10, "bold"),
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=10)

        # Figure buttons panel
        panel_draw = self._crear_panel(self, " MATRIZ DE DIBUJO GEOMÉTRICO ")
        grid_frame = tk.Frame(panel_draw, bg=PANEL_COLOR)
        grid_frame.pack(pady=5)

        figuras = [
            ("⬛ Cuadrado", self.dibujar_cuadrado, 0, 0, ACCENT_COLOR),
            ("▭ Rectángulo", self.dibujar_rectangulo, 0, 1, ACCENT_COLOR),
            ("▲ Triángulo", self.dibujar_triangulo, 0, 2, ACCENT_COLOR),
            ("⬠ Pentágono", self.dibujar_pentagono, 1, 0, ACCENT_COLOR),
            ("A Letra 'A'", self.dibujar_letra_a, 1, 1, ACCENT_COLOR),
            ("◯ Círculo", self.dibujar_circulo, 1, 2, ACCENT_COLOR),
            ("🏎️ Pista F1", self.dibujar_f1, 2, 1, "#E3B200"),
        ]

        for texto, cmd, row, col, color in figuras:
            nombre = texto.split(" ", 1)[-1]
            self._btn(
                grid_frame, texto,
                lambda f=cmd, n=nombre: self.iniciar_figura(f, n),
                color=color,
            ).grid(row=row, column=col, padx=5, pady=5)

        # E-STOP panel
        panel_stop = tk.Frame(self, bg=BG_COLOR)
        panel_stop.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(
            panel_stop, text="🛑 PARADA DE EMERGENCIA (E-STOP)",
            command=self._ejecutar_stop,
            bg=DANGER_COLOR, fg="white", font=(FONT_FAMILY, 14, "bold"),
            relief=tk.FLAT, pady=10,
        ).pack(fill=tk.X)

    # ------------------------------------------------------------------
    # Status & Connection
    # ------------------------------------------------------------------

    def actualizar_estado(self, texto: str, color: str = TEXT_COLOR) -> None:
        """Update the status label text and color."""
        self.lbl_status.config(text=texto, fg=color)
        self.update()

    def conectar(self) -> None:
        """Connect to the selected serial port."""
        try:
            self.hal.conectar(self.cb_ports.get())
            self.hal.enviar_comando(CENTRO_X, CENTRO_Y - 40, z=0)
            self.actualizar_estado("SISTEMA ONLINE", SUCCESS_COLOR)
        except Exception as e:
            messagebox.showerror("Error de Hardware", str(e))

    # ------------------------------------------------------------------
    # Figure Execution
    # ------------------------------------------------------------------

    def iniciar_figura(self, funcion_figura, nombre_figura: str) -> None:
        """Pre-flight checks then execute a figure."""
        if not self.hal.conectado:
            messagebox.showwarning("Sin conexión", "Primero conecta el sistema SCARA.")
            return

        if not solicitar_checklist(self, nombre_figura):
            self.actualizar_estado("Checklist cancelado", TEXT_COLOR)
            return

        self.actualizar_estado("Verificando enlace de motores...", ACCENT_COLOR)
        if not self.hal.verificar_enlace():
            self.actualizar_estado("Fallo de enlace con motores", DANGER_COLOR)
            messagebox.showerror(
                "Verificación fallida",
                "No hubo respuesta de los motores (OK).\n"
                "Revisa fuente, cableado y puerto serial.",
            )
            return

        self.actualizar_estado("Checklist y verificación OK", SUCCESS_COLOR)
        funcion_figura()

    def _ejecutar_stop(self) -> None:
        """Trigger emergency stop."""
        ejecutar_estop(self.hal, self.actualizar_estado)

    # ------------------------------------------------------------------
    # Figure Drawing Methods
    # ------------------------------------------------------------------

    def dibujar_cuadrado(self) -> None:
        self.traj.ejecutar_trayectoria("Cuadrado 60×60", cuadrado(),
                                        callback_estado=self.actualizar_estado)

    def dibujar_rectangulo(self) -> None:
        self.traj.ejecutar_trayectoria("Rectángulo 80×40", rectangulo(),
                                        callback_estado=self.actualizar_estado)

    def dibujar_triangulo(self) -> None:
        self.traj.ejecutar_trayectoria("Triángulo", triangulo(),
                                        callback_estado=self.actualizar_estado)

    def dibujar_pentagono(self) -> None:
        self.traj.ejecutar_trayectoria("Pentágono", pentagono(),
                                        callback_estado=self.actualizar_estado)

    def dibujar_circulo(self) -> None:
        self.traj.ejecutar_trayectoria("Círculo", circulo(),
                                        callback_estado=self.actualizar_estado)

    def dibujar_letra_a(self) -> None:
        """Draw letter A (two separate strokes)."""
        self.hal.detener_emergencia = False
        self.actualizar_estado("EJECUTANDO: Letra A...", ACCENT_COLOR)

        externo, puente = letra_a_trazos()

        # Outer stroke
        self.hal.enviar_comando(-20, 170, z=0)
        time.sleep(0.3)
        self.hal.enviar_comando(-20, 170, z=1)
        self.traj.trazar_linea(-20, 170, 0, 230)
        self.traj.trazar_linea(0, 230, 20, 170)

        if not self.hal.detener_emergencia:
            # Crossbar stroke
            self.hal.enviar_comando(20, 170, z=0)
            self.hal.enviar_comando(-10, 200, z=0)
            time.sleep(0.3)
            self.hal.enviar_comando(-10, 200, z=1)
            self.traj.trazar_linea(-10, 200, 10, 200)

            self.hal.enviar_comando(10, 200, z=0)
            self.hal.enviar_comando(CENTRO_X, CENTRO_Y - 40, z=0)
            self.actualizar_estado("TAREA COMPLETADA EXITOSAMENTE", SUCCESS_COLOR)

    def dibujar_f1(self) -> None:
        self.traj.ejecutar_trayectoria("Red Bull Ring", pista_f1(),
                                        callback_estado=self.actualizar_estado)
