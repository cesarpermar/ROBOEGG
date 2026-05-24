"""
SCARA Control — Safety Module
===============================
Emergency stop, pre-flight checklist, and motor link verification.
"""

import tkinter as tk
from tkinter import messagebox

from .config import (
    BG_COLOR, PANEL_COLOR, TEXT_COLOR, SUCCESS_COLOR,
    ACCENT_COLOR, DANGER_COLOR, FONT_FAMILY,
)
from .hal import HardwareInterface


def ejecutar_estop(hal: HardwareInterface, callback_estado=None) -> None:
    """Execute emergency stop: set flag, lift pen at last position."""
    if not hal.serial_port:
        return
    hal.detener_emergencia = True
    if callback_estado:
        callback_estado("¡PARADA DE EMERGENCIA ACTIVA!", DANGER_COLOR)
    hal.enviar_angulos_directos(hal.last_q1, hal.last_q2, z=0)


def solicitar_checklist(parent: tk.Tk, nombre_figura: str) -> bool:
    """Show pre-flight checklist. Returns True if operator confirms both items."""
    ventana = tk.Toplevel(parent)
    ventana.title("Checklist previo")
    ventana.configure(bg=PANEL_COLOR)
    ventana.resizable(False, False)
    ventana.transient(parent)
    ventana.grab_set()

    respuesta = {"ok": False}

    tk.Label(ventana, text=f"Antes de ejecutar: {nombre_figura}",
             bg=PANEL_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, 11, "bold"),
             ).pack(padx=16, pady=(12, 10), anchor="w")

    q1_var = tk.StringVar(value="NO")
    q2_var = tk.StringVar(value="NO")

    bloque1 = tk.Frame(ventana, bg=PANEL_COLOR)
    bloque1.pack(fill=tk.X, padx=16, pady=(4, 10))
    tk.Label(bloque1, text="1) Colocaste el brazo recto y en la orientación correcta?",
             bg=PANEL_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, 10)).pack(anchor="w")
    tk.Radiobutton(bloque1, text="Sí", variable=q1_var, value="SI",
                   bg=PANEL_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(side=tk.LEFT, padx=(0, 10))
    tk.Radiobutton(bloque1, text="No", variable=q1_var, value="NO",
                   bg=PANEL_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(side=tk.LEFT)

    bloque2 = tk.Frame(ventana, bg=PANEL_COLOR)
    bloque2.pack(fill=tk.X, padx=16, pady=(0, 12))
    tk.Label(bloque2, text="2) Conectaste motores/enciende el LED verde de la fuente?",
             bg=PANEL_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, 10)).pack(anchor="w")
    tk.Radiobutton(bloque2, text="Sí", variable=q2_var, value="SI",
                   bg=PANEL_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(side=tk.LEFT, padx=(0, 10))
    tk.Radiobutton(bloque2, text="No", variable=q2_var, value="NO",
                   bg=PANEL_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(side=tk.LEFT)

    def aceptar():
        if q1_var.get() != "SI" or q2_var.get() != "SI":
            messagebox.showwarning("Checklist incompleto",
                                   "Debes responder 'Sí' a ambas preguntas.", parent=ventana)
            return
        respuesta["ok"] = True
        ventana.destroy()

    def cancelar():
        ventana.destroy()

    botones = tk.Frame(ventana, bg=PANEL_COLOR)
    botones.pack(fill=tk.X, padx=16, pady=(0, 14))
    tk.Button(botones, text="Cancelar", command=cancelar,
              bg=BG_COLOR, fg=TEXT_COLOR, relief=tk.FLAT, width=12).pack(side=tk.RIGHT, padx=(8, 0))
    tk.Button(botones, text="Continuar", command=aceptar,
              bg=SUCCESS_COLOR, fg="white", relief=tk.FLAT, width=12).pack(side=tk.RIGHT)

    ventana.protocol("WM_DELETE_WINDOW", cancelar)
    parent.wait_window(ventana)
    return respuesta["ok"]
