"""
SCARA - Sincronía Total de Calibración
--------------------------------------
Mueve ambos motores en conjunto para validar el barrido de 180°.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import time

class ScaraSyncApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCARA - Sincronía de Brazo Rígido")
        self.geometry("600x550")
        
        # Parámetros de Calibración
        self.gamma = 0.0  # Este es el valor que ajustaremos
        self.serial_port = None
        
        self._setup_ui()

    def _setup_ui(self):
        main = ttk.Frame(self, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        # 1. CONEXIÓN
        conn_frame = ttk.LabelFrame(main, text=" 1. Comunicación ", padding=10)
        conn_frame.pack(fill=tk.X, pady=5)
        
        self.cb_ports = ttk.Combobox(conn_frame, values=[p.device for p in serial.tools.list_ports.comports()])
        self.cb_ports.pack(side=tk.LEFT, padx=5)
        ttk.Button(conn_frame, text="Conectar", command=self.conectar).pack(side=tk.LEFT)

        # 2. AJUSTE DE GAMMA (El "Cero" del Codo)
        gamma_frame = ttk.LabelFrame(main, text=" 2. Calibración Gamma (Offset de M2) ", padding=10)
        gamma_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_gamma = ttk.Label(gamma_frame, text=f"Gamma Actual: {self.gamma:.2f}°", font=("Arial", 10, "bold"))
        self.lbl_gamma.pack()
        
        btn_box = ttk.Frame(gamma_frame)
        btn_box.pack()
        for val in [-5, -1, -0.1, 0.1, 1, 5]:
            ttk.Button(btn_box, text=f"{val:+}°", width=5, 
                       command=lambda v=val: self.update_gamma(v)).pack(side=tk.LEFT, padx=2)

        # 3. CONTROL SINCRONIZADO (El Barrido)
        sync_frame = ttk.LabelFrame(main, text=" 3. Barrido Sincronizado (Brazo Rígido) ", padding=10)
        sync_frame.pack(fill=tk.X, pady=10)
        
        self.arm_angle_var = tk.DoubleVar(value=90)
        self.slider = ttk.Scale(sync_frame, from_=0, to=180, variable=self.arm_angle_var, 
                                orient=tk.HORIZONTAL, command=self.on_slider_move)
        self.slider.pack(fill=tk.X, pady=10)
        
        self.lbl_pos = ttk.Label(sync_frame, text="Brazo en: 90.00° (Centro)", font=("Arial", 12, "bold"), foreground="#007AFF")
        self.lbl_pos.pack()
        
        quick_frame = ttk.Frame(sync_frame)
        quick_frame.pack(pady=10)
        ttk.Button(quick_frame, text="0° (IZQ)", command=lambda: self.set_arm_pos(0)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="90° (CEN)", command=lambda: self.set_arm_pos(90)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="180° (DER)", command=lambda: self.set_arm_pos(180)).pack(side=tk.LEFT, padx=5)

    def update_gamma(self, delta):
        self.gamma += delta
        self.lbl_gamma.config(text=f"Gamma Actual: {self.gamma:.2f}°")
        self.send_command()

    def set_arm_pos(self, val):
        self.arm_angle_var.set(val)
        self.send_command()

    def on_slider_move(self, event):
        self.send_command()

    def conectar(self):
        try:
            port = self.cb_ports.get()
            self.serial_port = serial.Serial(port, 115200, timeout=0.5)
            time.sleep(2)
            messagebox.showinfo("Listo", "Robot conectado y sincronizado.")
            self.send_command()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def send_command(self):
        if not self.serial_port: return
        
        # LOGICA DE SINCRONÍA CORREGIDA:
        angulo_brazo = self.arm_angle_var.get()
        
        # 1. El hombro (M1) se mueve a la posición deseada
        q1_maquina = angulo_brazo - 90.0
        
        # 2. El codo (M2) DEBE acompañar al hombro para no doblar la correa.
        # Le sumamos Gamma para mantener el offset de calibración en todo momento.
        q2_maquina = -q1_maquina + self.gamma 
        
        self.lbl_pos.config(text=f"Brazo en: {angulo_brazo:.2f}°")
        
        comando = f"{q1_maquina:.2f},{q2_maquina:.2f},0\n"
        try:
            self.serial_port.write(comando.encode('ascii'))
            self.serial_port.flush()
        except Exception as e:
            pass

if __name__ == "__main__":
    ScaraSyncApp().mainloop()


    