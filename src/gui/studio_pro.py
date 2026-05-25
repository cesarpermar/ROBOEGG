"""
SCARA Studio Pro — Immersive & Professional UI
================================================
A fully-featured, high-tech dark-mode dashboard for the ROBOEGG SCARA robot.
Integrates live workspace simulation, Denavit-Hartenberg real-time matrix
analytics, responsive fullscreen grids, jog controls, and emergency tools.
"""

import math
import time
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple

from src.scara_control.config import (
    BG_COLOR, PANEL_COLOR, TEXT_COLOR, ACCENT_COLOR,
    SUCCESS_COLOR, DANGER_COLOR, FONT_FAMILY,
    CENTRO_X, CENTRO_Y, L1, L2,
)
from src.scara_control.hal import HardwareInterface
from src.scara_control.trajectory import TrajectoryEngine
from src.scara_control.safety import ejecutar_estop, solicitar_checklist
from src.scara_control.figures import (
    cuadrado, rectangulo, triangulo, pentagono, circulo,
    letra_a_trazos, pista_f1,
)
from src.scara_control.kinematics import analizar_punto_dh


class ScaraMasterPro(tk.Tk):
    """Futuristic high-performance cockpit dashboard for the SCARA 2R robot."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SCARA STUDIO PRO — Control & Metrology Terminal")
        
        # Try to launch maximized/zoomed for laptop screens
        try:
            self.state('zoomed')
        except Exception:
            self.geometry("1366x768")

        self.configure(bg=BG_COLOR)

        self.hal = HardwareInterface()
        self.traj = TrajectoryEngine(self.hal, gui=self)

        # Connect the real-time movement callback to our visualizer
        self.hal.on_move_callback = self.on_robot_moved

        # Workspace track states
        self.drawn_path: List[Tuple[float, float]] = []
        self.current_x: float = CENTRO_X
        self.current_y: float = CENTRO_Y - 40.0
        self.current_q1: float = 0.0
        self.current_q2: float = 0.0
        self.current_z: int = 0

        # Build responsive grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main Viewport

        self._construir_ui()
        
        # Initialize simulation canvas sizes
        self.update_idletasks()
        self.redibujar_simulador()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _construir_ui(self) -> None:
        """Create the futuristic responsive dashboard."""
        
        # ==========================================
        # 1. SIDEBAR (CONTROLS PANEL)
        # ==========================================
        sidebar = tk.Frame(self, bg=PANEL_COLOR, width=320, bd=1, relief=tk.FLAT)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        sidebar.grid_propagate(False)

        # Header Title
        lbl_head = tk.Label(
            sidebar, text="SCARA STUDIO PRO", bg=PANEL_COLOR, fg="white",
            font=(FONT_FAMILY, 15, "bold"), pady=15
        )
        lbl_head.pack(fill=tk.X)

        # Decorative separator
        tk.Frame(sidebar, height=2, bg=ACCENT_COLOR).pack(fill=tk.X, padx=15, pady=(0, 15))

        # Hardware connection panel
        conn_frame = tk.LabelFrame(
            sidebar, text=" COMUNICACIÓN SERIAL ", bg=PANEL_COLOR, fg=ACCENT_COLOR,
            font=(FONT_FAMILY, 9, "bold"), bd=1, padx=10, pady=10
        )
        conn_frame.pack(fill=tk.X, padx=15, pady=5)

        self.cb_ports = tk.StringVar()
        puertos = self.hal.listar_puertos()
        
        if puertos:
            menu_puertos = tk.OptionMenu(conn_frame, self.cb_ports, *puertos)
            self.cb_ports.set(puertos[0])
        else:
            menu_puertos = tk.Label(conn_frame, text="Sin puertos", bg=PANEL_COLOR, fg=DANGER_COLOR)
        
        menu_puertos.config(bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, 9), relief=tk.FLAT)
        menu_puertos.pack(fill=tk.X, pady=(0, 8))

        btn_connect = tk.Button(
            conn_frame, text="🔌 CONECTAR HARDWARE", command=self.conectar,
            bg=SUCCESS_COLOR, fg="white", font=(FONT_FAMILY, 9, "bold"),
            relief=tk.FLAT, activebackground="white", activeforeground=SUCCESS_COLOR
        )
        btn_connect.pack(fill=tk.X)

        # System controls (ESTOP, HOME, Reset Canvas)
        ctrl_frame = tk.LabelFrame(
            sidebar, text=" SISTEMA DE SEGURIDAD Y ORDENES ", bg=PANEL_COLOR, fg=ACCENT_COLOR,
            font=(FONT_FAMILY, 9, "bold"), bd=1, padx=10, pady=10
        )
        ctrl_frame.pack(fill=tk.X, padx=15, pady=10)

        # Emergency Stop (E-STOP)
        btn_estop = tk.Button(
            ctrl_frame, text="🛑 E-STOP (EMERGENCIA)", command=self._ejecutar_stop,
            bg=DANGER_COLOR, fg="white", font=(FONT_FAMILY, 10, "bold"),
            relief=tk.FLAT, height=2
        )
        btn_estop.pack(fill=tk.X, pady=4)

        # Home button
        btn_home = tk.Button(
            ctrl_frame, text="🏠 RETORNAR A HOME", command=self.ir_a_home,
            bg="#3E3E42", fg=TEXT_COLOR, font=(FONT_FAMILY, 9, "bold"),
            relief=tk.FLAT, height=1
        )
        btn_home.pack(fill=tk.X, pady=4)

        # Clear Canvas
        btn_clear = tk.Button(
            ctrl_frame, text="🧹 LIMPIAR TRAZO", command=self.limpiar_trazo,
            bg="#3E3E42", fg=TEXT_COLOR, font=(FONT_FAMILY, 9, "bold"),
            relief=tk.FLAT
        )
        btn_clear.pack(fill=tk.X, pady=4)

        # Figures section
        fig_frame = tk.LabelFrame(
            sidebar, text=" MATRIZ DE TRAZADOS ", bg=PANEL_COLOR, fg=ACCENT_COLOR,
            font=(FONT_FAMILY, 9, "bold"), bd=1, padx=10, pady=10
        )
        fig_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Scrollable layout inside figures frame
        grid_inner = tk.Frame(fig_frame, bg=PANEL_COLOR)
        grid_inner.pack(fill=tk.BOTH, expand=True)

        figuras = [
            ("⬛ Cuadrado", self.dibujar_cuadrado, 0, 0),
            ("▭ Rectángulo", self.dibujar_rectangulo, 0, 1),
            ("▲ Triángulo", self.dibujar_triangulo, 1, 0),
            ("⬠ Pentágono", self.dibujar_pentagono, 1, 1),
            ("◯ Círculo", self.dibujar_circulo, 2, 0),
            ("A Letra 'A'", self.dibujar_letra_a, 2, 1),
            ("🏎️ Red Bull Ring", self.dibujar_f1, 3, 0),
        ]

        grid_inner.grid_columnconfigure(0, weight=1)
        grid_inner.grid_columnconfigure(1, weight=1)

        for texto, cmd, row, col in figuras:
            nombre = texto.split(" ", 1)[-1]
            btn = tk.Button(
                grid_inner, text=texto, command=lambda f=cmd, n=nombre: self.iniciar_figura(f, n),
                bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, 9, "bold"), relief=tk.FLAT,
                activebackground=ACCENT_COLOR, activeforeground="white"
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        # Live Status bar in sidebar
        self.lbl_status = tk.Label(
            sidebar, text="DESCONECTADO — OFFLINE", bg="#111", fg="#888",
            font=(FONT_FAMILY, 9, "bold"), pady=10
        )
        self.lbl_status.pack(fill=tk.X, side=tk.BOTTOM)

        # ==========================================
        # 2. MAIN VIEWPORT (RIGHT SIDE)
        # ==========================================
        viewport = tk.Frame(self, bg=BG_COLOR)
        viewport.grid(row=0, column=1, sticky="nsew")

        # Responsive weights for viewport
        viewport.grid_rowconfigure(0, weight=7) # Holographic Canvas (70%)
        viewport.grid_rowconfigure(1, weight=3) # DH Analytics Panel (30%)
        viewport.grid_columnconfigure(0, weight=1)

        # ------------------------------------------
        # A. Top: Holographic Workspace Simulator
        # ------------------------------------------
        sim_parent = tk.LabelFrame(
            viewport, text=" VISUALIZADOR HOLOGRÁFICO DEL WORKSPACE ", bg=BG_COLOR, fg=ACCENT_COLOR,
            font=(FONT_FAMILY, 9, "bold"), bd=1
        )
        sim_parent.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Interactive Canvas
        self.canvas = tk.Canvas(sim_parent, bg="#0E0E10", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Redraw simulator when resized
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # ------------------------------------------
        # B. Bottom: Denavit-Hartenberg live analytics dashboard
        # ------------------------------------------
        dh_parent = tk.LabelFrame(
            viewport, text=" ANÁLISIS METROLÓGICO DENAVIT-HARTENBERG EN TIEMPO REAL ",
            bg=PANEL_COLOR, fg=ACCENT_COLOR, font=(FONT_FAMILY, 9, "bold"), bd=1
        )
        dh_parent.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Grid system for DH columns
        dh_parent.grid_rowconfigure(0, weight=1)
        for i in range(4):
            dh_parent.grid_columnconfigure(i, weight=1)

        # Col 1: Metrology Metrics
        metrology_frame = tk.Frame(dh_parent, bg=PANEL_COLOR)
        metrology_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.lbl_met_coords = tk.Label(
            metrology_frame, text="OBJETIVO: (0.00, 0.00) mm\nESCALA: (0.00, 0.00) mm",
            bg=PANEL_COLOR, fg=TEXT_COLOR, justify=tk.LEFT, anchor="w",
            font=("Courier", 10)
        )
        self.lbl_met_coords.pack(fill=tk.X, anchor="w", pady=2)

        self.lbl_met_angles = tk.Label(
            metrology_frame, text="IDEAL THETA:\n  θ1 = 0.00°\n  θ2 = 0.00°\n\nFÍSICO MOTORES:\n  q1 = 0.00°\n  q2 = 0.00°",
            bg=PANEL_COLOR, fg="#00FFC4", justify=tk.LEFT, anchor="w",
            font=("Courier", 10)
        )
        self.lbl_met_angles.pack(fill=tk.X, anchor="w", pady=5)

        self.lbl_met_error = tk.Label(
            metrology_frame, text="FK CHECK: (0.00, 0.00) mm\nFK ERR: 0.000 mm",
            bg=PANEL_COLOR, fg="#FFC400", justify=tk.LEFT, anchor="w",
            font=("Courier", 10)
        )
        self.lbl_met_error.pack(fill=tk.X, anchor="w", pady=2)

        # Col 2: Matrix T01 (Shoulder)
        t01_frame = tk.Frame(dh_parent, bg=PANEL_COLOR)
        t01_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        tk.Label(t01_frame, text="MATRIZ T01 (Hombro)", bg=PANEL_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, 8, "bold")).pack()
        self.txt_t01 = tk.Text(t01_frame, bg="#111", fg="#00FFC4", font=("Courier", 8), bd=0, highlightthickness=0)
        self.txt_t01.pack(fill=tk.BOTH, expand=True, pady=4)
        self.txt_t01.insert(tk.END, self._format_matrix_template())

        # Col 3: Matrix T12 (Codo)
        t12_frame = tk.Frame(dh_parent, bg=PANEL_COLOR)
        t12_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        tk.Label(t12_frame, text="MATRIZ T12 (Codo)", bg=PANEL_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, 8, "bold")).pack()
        self.txt_t12 = tk.Text(t12_frame, bg="#111", fg="#00FFC4", font=("Courier", 8), bd=0, highlightthickness=0)
        self.txt_t12.pack(fill=tk.BOTH, expand=True, pady=4)
        self.txt_t12.insert(tk.END, self._format_matrix_template())

        # Col 4: Matrix T (Total)
        t_frame = tk.Frame(dh_parent, bg=PANEL_COLOR)
        t_frame.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)
        tk.Label(t_frame, text="MATRIZ T_TOTAL (Final)", bg=PANEL_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, 8, "bold")).pack()
        self.txt_t = tk.Text(t_frame, bg="#111", fg="#00FFC4", font=("Courier", 8), bd=0, highlightthickness=0)
        self.txt_t.pack(fill=tk.BOTH, expand=True, pady=4)
        self.txt_t.insert(tk.END, self._format_matrix_template())

    # ------------------------------------------------------------------
    # Helper Templates
    # ------------------------------------------------------------------

    def _format_matrix_template(self) -> str:
        """Return a simple high-tech template for the matrix view."""
        return "\n".join([
            "  [  1.00   0.00   0.00   0.00 ]",
            "  [  0.00   1.00   0.00   0.00 ]",
            "  [  0.00   0.00   1.00   0.00 ]",
            "  [  0.00   0.00   0.00   1.00 ]"
        ])

    def format_matrix(self, matrix) -> str:
        """Format a 4x4 matrix block into highly readable clean text."""
        lines = []
        for row in matrix:
            lines.append("  [ " + " ".join(f"{val:6.2f}" for val in row) + " ]")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Holographic Workspace Simulator & Canvas mapping
    # ------------------------------------------------------------------

    def on_canvas_resize(self, event) -> None:
        """Recalculate visualization coordinates when resizing window."""
        self.redibujar_simulador()

    def redibujar_simulador(self) -> None:
        """Render grid layout, safe zone circle bounds, robot arm, and trail."""
        self.canvas.delete("all")
        
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        if W < 50 or H < 50:
            return

        # Base origin position (0, 0) in canvas space
        ox = W / 2
        oy = H - 50
        
        # Scaling factor: pixels per mm (adjusts to canvas size)
        scale = min(W / 420.0, H / 320.0) * 1.1

        # 1. Cartesian Grid lines
        for dx in range(-200, 201, 50):
            cx = ox + dx * scale
            self.canvas.create_line(cx, 0, cx, H, fill="#1B1B22", width=1)
            if dx != 0:
                self.canvas.create_text(cx, oy + 20, text=f"{dx}", fill="#555", font=("Courier", 8))

        for dy in range(50, 301, 50):
            cy = oy - dy * scale
            self.canvas.create_line(0, cy, W, cy, fill="#1B1B22", width=1)
            self.canvas.create_text(ox - 20, cy, text=f"{dy}", fill="#555", font=("Courier", 8))

        # Axis origin indicator
        self.canvas.create_line(ox, 0, ox, H, fill="#2F2F3D", width=1)
        self.canvas.create_line(0, oy, W, oy, fill="#2F2F3D", width=1)

        # 2. Concentric reach circles
        # Reach maximum: L1 + L2
        r_max = (L1 + L2) * scale
        self.canvas.create_oval(ox - r_max, oy - r_max, ox + r_max, oy + r_max, outline="#3A2222", width=1, dash=(2, 4))
        # Reach minimum: |L1 - L2|
        r_min = abs(L1 - L2) * scale
        self.canvas.create_oval(ox - r_min, oy - r_min, ox + r_min, oy + r_min, outline="#1A2233", width=1, dash=(2, 4))

        # Safe area bounds
        self.canvas.create_text(ox + (L1+L2)*scale - 40, oy - 20, text="MAX REACH", fill="#5A3A3A", font=(FONT_FAMILY, 7, "bold"))

        # 3. Draw trail path
        if len(self.drawn_path) > 1:
            points_canvas = []
            for px, py in self.drawn_path:
                points_canvas.append(ox + px * scale)
                points_canvas.append(oy - py * scale)
            self.canvas.create_line(points_canvas, fill="#00FF66", width=2, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        # 4. Render mechanical neon arm
        # Get joints from kinematics study
        res = analizar_punto_dh(self.current_x, self.current_y)
        if res:
            # Ideal shoulder joint angles
            th1 = math.radians(res["theta1"])
            
            # Elbow coordinates
            ex = L1 * math.cos(th1)
            ey = L1 * math.sin(th1)

            # End effector coordinates
            efx = res["x_fk"]
            efy = res["y_fk"]

            # Map to canvas
            ex_c = ox + ex * scale
            ey_c = oy - ey * scale
            efx_c = ox + efx * scale
            efy_c = oy - efy * scale

            # Draw Neon link 1 (Shoulder to Elbow)
            self.canvas.create_line(ox, oy, ex_c, ey_c, fill="#007ACC", width=6)
            self.canvas.create_line(ox, oy, ex_c, ey_c, fill="#00C4FF", width=2)

            # Draw Neon link 2 (Elbow to End Effector)
            self.canvas.create_line(ex_c, ey_c, efx_c, efy_c, fill="#E30066", width=6)
            self.canvas.create_line(ex_c, ey_c, efx_c, efy_c, fill="#FF6BAE", width=2)

            # Draw Joint Caps
            self.canvas.create_oval(ox-6, oy-6, ox+6, oy+6, fill="#1E1E1E", outline="#00C4FF", width=2)
            self.canvas.create_oval(ex_c-6, ey_c-6, ex_c+6, ey_c+6, fill="#1E1E1E", outline="#00C4FF", width=2)
            
            # Draw Pen cap (Green/Orange according to pen state)
            pen_color = "#00FF66" if self.current_z == 1 else "#FFC400"
            self.canvas.create_oval(efx_c-8, efy_c-8, efx_c+8, efy_c+8, fill="#1E1E1E", outline=pen_color, width=3)
            self.canvas.create_text(efx_c, efy_c - 16, text=f"({self.current_x:.1f}, {self.current_y:.1f})", fill="white", font=("Courier", 8, "bold"))

    # ------------------------------------------------------------------
    # Real-time Hardware Callback & DH updates
    # ------------------------------------------------------------------

    def on_robot_moved(self, x: float, y: float, q1: float, q2: float, z: int) -> None:
        """Callback triggered dynamically by HAL to update graphics and matrices in real-time."""
        self.current_x = x
        self.current_y = y
        self.current_q1 = q1
        self.current_q2 = q2
        self.current_z = z

        # Add point to trail if pen is down
        if z == 1:
            self.drawn_path.append((x, y))

        # 1. Update metrology dashboard with DH analysis
        res = analizar_punto_dh(x, y)
        if res:
            self.lbl_met_coords.config(
                text=f"OBJETIVO: ({x:.2f}, {y:.2f}) mm\nESCALA:   ({res['x_esc']:.2f}, {res['y_esc']:.2f}) mm"
            )
            self.lbl_met_angles.config(
                text=f"IDEAL THETA:\n  θ1 = {res['theta1']:.2f}°\n  θ2 = {res['theta2']:.2f}°\n\nFÍSICO MOTORES:\n  q1 = {q1:.2f}°\n  q2 = {q2:.2f}°"
            )
            
            # Forward Kinematics verification error
            fk_err = math.sqrt((res["x_fk"] - res["x_esc"])**2 + (res["y_fk"] - res["y_esc"])**2)
            self.lbl_met_error.config(
                text=f"FK CHECK: ({res['x_fk']:.2f}, {res['y_fk']:.2f}) mm\nFK ERR:   {fk_err:.4f} mm"
            )

            # 2. Update live matrices
            self._update_matrix_box(self.txt_t01, res["T01"])
            self._update_matrix_box(self.txt_t12, res["T12"])
            self._update_matrix_box(self.txt_t, res["T"])

        # 3. Redraw simulation frame
        self.redibujar_simulador()
        self.update_idletasks()

    def _update_matrix_box(self, text_widget: tk.Text, matrix) -> None:
        """Update a text box with formatted matrix values."""
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, self.format_matrix(matrix))

    # ------------------------------------------------------------------
    # Connection & Operation Actions
    # ------------------------------------------------------------------

    def actualizar_estado(self, texto: str, color: str = TEXT_COLOR) -> None:
        """Update status readout in the lower sidebar."""
        self.lbl_status.config(text=texto.upper(), fg=color)
        self.update()

    def conectar(self) -> None:
        """Open serial link to CNC shield and center the arm."""
        try:
            puerto = self.cb_ports.get()
            if not puerto:
                raise ValueError("No se seleccionó ningún puerto serial.")
            self.actualizar_estado("CONECTANDO...", ACCENT_COLOR)
            self.hal.conectar(puerto)
            
            # Reset visual track
            self.drawn_path.clear()
            
            # Center SCARA to initial offset
            self.hal.enviar_comando(CENTRO_X, CENTRO_Y - 40, z=0)
            self.actualizar_estado("SISTEMA ONLINE", SUCCESS_COLOR)
        except Exception as e:
            self.actualizar_estado("FALLO DE CONEXIÓN", DANGER_COLOR)
            messagebox.showerror("Error de Hardware", str(e))

    def ir_a_home(self) -> None:
        """Command the arm back to its safe home configuration."""
        if not self.hal.conectado:
            messagebox.showwarning("Sin conexión", "Primero conecta el sistema SCARA.")
            return
        
        self.actualizar_estado("RETORNANDO A HOME...", ACCENT_COLOR)
        self.hal.enviar_comando(CENTRO_X, CENTRO_Y - 40, z=0)
        self.actualizar_estado("EN HOME", SUCCESS_COLOR)

    def limpiar_trazo(self) -> None:
        """Clear the drawn neon trail from the simulator board."""
        self.drawn_path.clear()
        self.redibujar_simulador()

    def _ejecutar_stop(self) -> None:
        """Fire E-STOP sequence."""
        ejecutar_estop(self.hal, self.actualizar_estado)

    # ------------------------------------------------------------------
    # Figures Drawing Integration
    # ------------------------------------------------------------------

    def iniciar_figura(self, funcion_figura, nombre_figura: str) -> None:
        """Run standard metrology checks and pre-flight checklist, then draw."""
        if not self.hal.conectado:
            messagebox.showwarning("Sin conexión", "Primero conecta el sistema SCARA.")
            return

        if not solicitar_checklist(self, nombre_figura):
            self.actualizar_estado("Checklist cancelado", TEXT_COLOR)
            return

        self.actualizar_estado("Verificando motores...", ACCENT_COLOR)
        if not self.hal.verificar_enlace():
            self.actualizar_estado("Fallo de enlace con motores", DANGER_COLOR)
            messagebox.showerror(
                "Verificación fallida",
                "Los motores no respondieron al ping de enlace (OK).\n"
                "Verifica la alimentación de 12V y el cableado.",
            )
            return

        self.actualizar_estado("Checklist verificado", SUCCESS_COLOR)
        
        # Clear trail before each drawing to keep it clean
        self.drawn_path.clear()
        funcion_figura()

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
        """Draw capital 'A' (two distinct strokes)."""
        self.hal.detener_emergencia = False
        self.actualizar_estado("EJECUTANDO: Letra A...", ACCENT_COLOR)
        self.drawn_path.clear()

        externo, puente = letra_a_trazos()

        # Stroke 1: Outer shell
        self.hal.enviar_comando(-20, 170, z=0)
        time.sleep(0.3)
        self.hal.enviar_comando(-20, 170, z=1)
        self.traj.trazar_linea(-20, 170, 0, 230)
        self.traj.trazar_linea(0, 230, 20, 170)

        if not self.hal.detener_emergencia:
            # Stroke 2: Crossbar
            self.hal.enviar_comando(20, 170, z=0)
            self.hal.enviar_comando(-10, 200, z=0)
            time.sleep(0.3)
            self.hal.enviar_comando(-10, 200, z=1)
            self.traj.trazar_linea(-10, 200, 10, 200)

            # Finalize
            self.hal.enviar_comando(10, 200, z=0)
            self.hal.enviar_comando(CENTRO_X, CENTRO_Y - 40, z=0)
            self.actualizar_estado("TAREA COMPLETADA EXITOSAMENTE", SUCCESS_COLOR)

    def dibujar_f1(self) -> None:
        self.traj.ejecutar_trayectoria("Red Bull Ring", pista_f1(),
                                        callback_estado=self.actualizar_estado)


def main() -> None:
    """Launch the dashboard cock-pit app."""
    app = ScaraMasterPro()
    app.mainloop()


if __name__ == "__main__":
    main()
