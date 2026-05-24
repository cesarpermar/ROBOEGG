"""
SCARA - Analisis Denavit-Hartenberg (DH)
---------------------------------------------------------
Modulo reutilizable para enlazar la cinematica teorica con el trazado real.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import numpy as np
import serial
import time
import serial.tools.list_ports

# --- CONSTANTES FISICAS Y CALIBRACION ---
A1 = 150.0
A2 = 159.94
GAMMA = 2.0
CODO_DERECHO = True
ESCALA_X = 60.0 / 70.0
ESCALA_Y = 60.0 / 50.0
CENTRO_X = 0.0
CENTRO_Y = 200.0


def generar_puntos_circulo(cx, cy, radio, segmentos=36):
    return [
        (
            cx + radio * math.cos((2 * math.pi * i) / segmentos),
            cy + radio * math.sin((2 * math.pi * i) / segmentos),
        )
        for i in range(segmentos)
    ]


def obtener_figuras_base(centro_x=CENTRO_X, centro_y=CENTRO_Y):
    radio_pentagono = 35.0
    pentagono = [
        (
            centro_x + radio_pentagono * math.cos(math.radians(90 + i * 72)),
            centro_y + radio_pentagono * math.sin(math.radians(90 + i * 72)),
        )
        for i in range(5)
    ]

    return {
        "Cuadrado": {"puntos": [(-30, 170), (30, 170), (30, 230), (-30, 230)], "cerrado": True},
        "Rectangulo": {"puntos": [(-40, 180), (40, 180), (40, 220), (-40, 220)], "cerrado": True},
        "Triangulo": {"puntos": [(-30, 175), (30, 175), (0, 227)], "cerrado": True},
        "Pentagono": {"puntos": pentagono, "cerrado": True},
        "Circulo": {"puntos": generar_puntos_circulo(centro_x, centro_y, 30, 36), "cerrado": True},
    }


class DHAnalyzer:
    def __init__(
        self,
        a1=A1,
        a2=A2,
        gamma=GAMMA,
        codo_derecho=CODO_DERECHO,
        escala_x=ESCALA_X,
        escala_y=ESCALA_Y,
        centro_x=CENTRO_X,
        centro_y=CENTRO_Y,
    ):
        self.a1 = a1
        self.a2 = a2
        self.gamma = gamma
        self.codo_derecho = codo_derecho
        self.escala_x = escala_x
        self.escala_y = escala_y
        self.centro_x = centro_x
        self.centro_y = centro_y

    def aplicar_escala(self, x, y):
        dx = x - self.centro_x
        dy = y - self.centro_y
        return (dx * self.escala_x) + self.centro_x, (dy * self.escala_y) + self.centro_y

    def matriz_dh(self, theta_deg, d, a, alpha_deg):
        th = math.radians(theta_deg)
        al = math.radians(alpha_deg)
        return np.array(
            [
                [math.cos(th), -math.sin(th) * math.cos(al), math.sin(th) * math.sin(al), a * math.cos(th)],
                [math.sin(th), math.cos(th) * math.cos(al), -math.cos(th) * math.sin(al), a * math.sin(th)],
                [0, math.sin(al), math.cos(al), d],
                [0, 0, 0, 1],
            ]
        )

    def cinematica_inversa_dh(self, x, y):
        d = (x**2 + y**2 - self.a1**2 - self.a2**2) / (2 * self.a1 * self.a2)
        if not (-1 <= d <= 1):
            return None, None

        signo = -1 if self.codo_derecho else 1
        q2_rad = math.atan2(signo * math.sqrt(1 - d**2), d)
        q1_rad = math.atan2(y, x) - math.atan2(self.a2 * math.sin(q2_rad), self.a1 + self.a2 * math.cos(q2_rad))
        return math.degrees(q1_rad), math.degrees(q2_rad)

    def comprobacion_directa_dh(self, theta1, theta2):
        t01 = self.matriz_dh(theta1, 0, self.a1, 0)
        t12 = self.matriz_dh(theta2, 0, self.a2, 0)
        t_total = np.dot(t01, t12)
        return t_total[0, 3], t_total[1, 3], t01, t12, t_total

    def calcular_fisico(self, theta1, theta2):
        q1 = 90.0 - theta1
        q2 = -q1 + theta2 + self.gamma
        return q1, q2

    def analizar_punto(self, x_objetivo, y_objetivo):
        x_esc, y_esc = self.aplicar_escala(x_objetivo, y_objetivo)
        th1_ideal, th2_ideal = self.cinematica_inversa_dh(x_esc, y_esc)
        if th1_ideal is None:
            return None

        x_fk, y_fk, t01, t12, t_total = self.comprobacion_directa_dh(th1_ideal, th2_ideal)
        q1_fisico, q2_fisico = self.calcular_fisico(th1_ideal, th2_ideal)

        return {
            "x_obj": x_objetivo,
            "y_obj": y_objetivo,
            "x_esc": x_esc,
            "y_esc": y_esc,
            "theta1": th1_ideal,
            "theta2": th2_ideal,
            "q1": q1_fisico,
            "q2": q2_fisico,
            "x_fk": x_fk,
            "y_fk": y_fk,
            "T01": t01,
            "T12": t12,
            "T": t_total,
        }

    def imprimir_reporte_figura(self, nombre, puntos, cerrarlo=True, max_puntos=40):
        trayectoria = list(puntos)
        if cerrarlo and trayectoria and trayectoria[0] != trayectoria[-1]:
            trayectoria.append(trayectoria[0])

        if not trayectoria:
            return

        stride = max(1, math.ceil(len(trayectoria) / max_puntos))
        muestra = trayectoria[::stride]
        if muestra[-1] != trayectoria[-1]:
            muestra.append(trayectoria[-1])

        print("\n" + "=" * 90)
        print(f"REPORTE DH FIGURA: {nombre}")
        print("=" * 90)
        print("idx |   Xobj   Yobj |   Xesc   Yesc | Theta1  Theta2 |   Q1     Q2   |   Xfk    Yfk")
        print("-" * 90)

        for i, (x, y) in enumerate(muestra):
            r = self.analizar_punto(x, y)
            if r is None:
                print(f"{i:03d} | {x:6.2f} {y:6.2f} |   INALCANZABLE")
                continue

            print(
                f"{i:03d} | {r['x_obj']:6.2f} {r['y_obj']:6.2f} | "
                f"{r['x_esc']:6.2f} {r['y_esc']:6.2f} | "
                f"{r['theta1']:6.2f} {r['theta2']:7.2f} | "
                f"{r['q1']:6.2f} {r['q2']:7.2f} | "
                f"{r['x_fk']:6.2f} {r['y_fk']:6.2f}"
            )

            print("  T01 =")
            print(np.array2string(r["T01"], precision=3, suppress_small=True))
            print("  T12 =")
            print(np.array2string(r["T12"], precision=3, suppress_small=True))
            print("  T   =")
            print(np.array2string(r["T"], precision=3, suppress_small=True))
            print("-" * 90)

        if stride > 1:
            print(f"Nota: se muestrearon {len(muestra)} de {len(trayectoria)} puntos para mantener legible la salida.")
        print("=" * 90)


class ScaraDHController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCARA - Enlace DH")
        self.geometry("700x420")
        self.serial_port = None
        self.analyzer = DHAnalyzer()
        self.figuras = obtener_figuras_base()
        self._setup_ui()

    def _setup_ui(self):
        main = ttk.Frame(self, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        conn_frame = ttk.LabelFrame(main, text=" 1. Conexion Serial ", padding=10)
        conn_frame.pack(fill=tk.X, pady=5)
        self.cb_ports = ttk.Combobox(conn_frame, values=[p.device for p in serial.tools.list_ports.comports()])
        self.cb_ports.pack(side=tk.LEFT, padx=5)
        if self.cb_ports["values"]:
            self.cb_ports.current(0)
        ttk.Button(conn_frame, text="Conectar", command=self.conectar).pack(side=tk.LEFT)

        test_frame = ttk.LabelFrame(main, text=" 2. Probar puntos con DH ", padding=10)
        test_frame.pack(fill=tk.X, pady=10)
        btn_box = ttk.Frame(test_frame)
        btn_box.pack()
        ttk.Button(btn_box, text="Izquierda (-100,200)", command=lambda: self.ejecutar_movimiento(-100, 200)).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(btn_box, text="Centro (0,200)", command=lambda: self.ejecutar_movimiento(0, 200)).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(btn_box, text="Derecha (100,200)", command=lambda: self.ejecutar_movimiento(100, 200)).pack(
            side=tk.LEFT, padx=3
        )

        figura_frame = ttk.LabelFrame(main, text=" 3. Tabla DH por figura (consola) ", padding=10)
        figura_frame.pack(fill=tk.X, pady=10)
        self.cb_figuras = ttk.Combobox(figura_frame, values=list(self.figuras.keys()), state="readonly")
        self.cb_figuras.pack(side=tk.LEFT, padx=5)
        if self.cb_figuras["values"]:
            self.cb_figuras.current(0)
        ttk.Button(figura_frame, text="Analizar figura", command=self.analizar_figura_actual).pack(side=tk.LEFT, padx=5)

        self.lbl_log = ttk.Label(
            main,
            text="La tabla y matrices DH se imprimen en la consola de Python.",
            font=("Courier", 9),
        )
        self.lbl_log.pack(pady=15)

    def conectar(self):
        try:
            self.serial_port = serial.Serial(self.cb_ports.get(), 115200, timeout=0.5)
            time.sleep(2)
            self.ejecutar_movimiento(0, 200)
            self.lbl_log.config(text="Conectado y en home.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def analizar_figura_actual(self):
        nombre = self.cb_figuras.get()
        cfg = self.figuras.get(nombre)
        if not cfg:
            return
        self.analyzer.imprimir_reporte_figura(nombre, cfg["puntos"], cerrarlo=cfg["cerrado"], max_puntos=24)

    def ejecutar_movimiento(self, x_objetivo, y_objetivo):
        if not self.serial_port:
            return

        reporte = self.analyzer.analizar_punto(x_objetivo, y_objetivo)
        print("\n" + "=" * 50)
        print(f"NUEVO COMANDO: Ir a X={x_objetivo}, Y={y_objetivo}")
        if reporte is None:
            print("Punto inalcanzable.")
            return

        print(f"[TEORIA] Theta1={reporte['theta1']:.2f} deg, Theta2={reporte['theta2']:.2f} deg")
        print(f"[HAL] M1={reporte['q1']:.2f} deg, M2={reporte['q2']:.2f} deg")

        comando = f"{reporte['q1']:.2f},{reporte['q2']:.2f},0\n"
        self.serial_port.write(comando.encode("ascii"))

        while True:
            if self.serial_port.in_waiting:
                resp = self.serial_port.readline().decode("ascii").strip()
                if resp == "OK":
                    break

        print("[COMPROBACION DH]")
        print(f"Xfk={reporte['x_fk']:.2f}, Yfk={reporte['y_fk']:.2f}")
        print("T =")
        print(np.array2string(reporte["T"], precision=3, suppress_small=True))
        print("=" * 50)


if __name__ == "__main__":
    app = ScaraDHController()
    app.mainloop()