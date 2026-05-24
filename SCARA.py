"""
SCARA - SUITE MAESTRA V2.0 PRO
---------------------------------------------------------
Incluye: Motor de interpolación, Calibración HAL, Interfaz Dark Mode,
Botón de Parada de Emergencia y Trazado de F1 (Gran Premio de México).
"""

import tkinter as tk
from tkinter import messagebox
import math
import serial
import time
import serial.tools.list_ports
from PruebaDH import DHAnalyzer, generar_puntos_circulo

# =========================================================
# 1. CONSTANTES DE CALIBRACIÓN (Tus valores de la victoria)
# =========================================================
L1 = 150.0
L2 = 159.94
GAMMA = 2.0           
CODO_DERECHO = True  
RESOLUCION_MM = 1.0   

# Matriz de Escala (Actualiza con tus últimas mediciones)
ESCALA_X = 60.0 / 70.0  
ESCALA_Y = 60.0 / 50.0  

CENTRO_X = 0.0
CENTRO_Y = 200.0  

# =========================================================
# 2. INTERFAZ GRÁFICA (Estética Profesional CNC)
# =========================================================
BG_COLOR = "#1E1E1E"        # Fondo oscuro
PANEL_COLOR = "#2D2D30"     # Paneles
TEXT_COLOR = "#FFFFFF"      # Texto blanco
ACCENT_COLOR = "#007ACC"    # Azul visual studio
SUCCESS_COLOR = "#28A745"   # Verde éxito
DANGER_COLOR = "#DC3545"    # Rojo emergencia

class ScaraMasterPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCARA STUDIO PRO - Control Master")
        self.geometry("650x550")
        self.configure(bg=BG_COLOR)
        
        self.serial_port = None
        self.detener_emergencia = False
        self.dh_analyzer = DHAnalyzer(
            a1=L1,
            a2=L2,
            gamma=GAMMA,
            codo_derecho=CODO_DERECHO,
            escala_x=ESCALA_X,
            escala_y=ESCALA_Y,
            centro_x=CENTRO_X,
            centro_y=CENTRO_Y,
        )
        
        # Memoria de última posición para el STOP
        self.last_q1 = 0.0
        self.last_q2 = 0.0

        self._construir_ui()

    def _crear_panel(self, padre, titulo):
        marco = tk.LabelFrame(padre, text=titulo, bg=PANEL_COLOR, fg=ACCENT_COLOR, 
                              font=("Segoe UI", 10, "bold"), bd=1, padx=15, pady=15)
        marco.pack(fill=tk.X, padx=20, pady=10)
        return marco

    def _btn(self, padre, texto, comando, color=ACCENT_COLOR, ancho=20):
        btn = tk.Button(padre, text=texto, command=comando, bg=color, fg="white",
                        font=("Segoe UI", 10, "bold"), relief=tk.FLAT, 
                        activebackground="white", activeforeground=color, width=ancho)
        return btn

    def _construir_ui(self):
        # CABECERA
        lbl_titulo = tk.Label(self, text="SCARA STUDIO PRO", bg=BG_COLOR, fg="white", 
                              font=("Segoe UI", 16, "bold"), pady=10)
        lbl_titulo.pack()

        # PANEL DE CONEXIÓN
        panel_conn = self._crear_panel(self, " CONEXIÓN DE HARDWARE ")
        
        self.cb_ports = tk.StringVar()
        puertos = [p.device for p in serial.tools.list_ports.comports()]
        menu_puertos = tk.OptionMenu(panel_conn, self.cb_ports, *puertos) if puertos else tk.Label(panel_conn, text="Sin puertos", bg=PANEL_COLOR, fg="red")
        if puertos: self.cb_ports.set(puertos[0])
        menu_puertos.config(bg=BG_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 9))
        menu_puertos.pack(side=tk.LEFT, padx=10)
        
        self._btn(panel_conn, "CONECTAR SISTEMA", self.conectar, color=SUCCESS_COLOR).pack(side=tk.LEFT, padx=10)
        
        self.lbl_status = tk.Label(panel_conn, text="DESCONECTADO", bg=PANEL_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 10, "bold"))
        self.lbl_status.pack(side=tk.RIGHT, padx=10)

        # PANEL DE PROYECTOS (BOTONES)
        panel_draw = self._crear_panel(self, " MATRIZ DE DIBUJO GEOMÉTRICO ")
        
        grid_frame = tk.Frame(panel_draw, bg=PANEL_COLOR)
        grid_frame.pack(pady=5)
        
        self._btn(grid_frame, "⬛ Cuadrado", lambda: self.iniciar_figura(self.dibujar_cuadrado, "Cuadrado")).grid(row=0, column=0, padx=5, pady=5)
        self._btn(grid_frame, "▭ Rectángulo", lambda: self.iniciar_figura(self.dibujar_rectangulo, "Rectángulo")).grid(row=0, column=1, padx=5, pady=5)
        self._btn(grid_frame, "▲ Triángulo", lambda: self.iniciar_figura(self.dibujar_triangulo, "Triángulo")).grid(row=0, column=2, padx=5, pady=5)
        self._btn(grid_frame, "⬠ Pentágono", lambda: self.iniciar_figura(self.dibujar_pentagono, "Pentágono")).grid(row=1, column=0, padx=5, pady=5)
        self._btn(grid_frame, "A Letra 'A'", lambda: self.iniciar_figura(self.dibujar_letra_A, "Letra A")).grid(row=1, column=1, padx=5, pady=5)
        self._btn(grid_frame, "◯ Círculo", lambda: self.iniciar_figura(self.dibujar_circulo, "Círculo")).grid(row=1, column=2, padx=5, pady=5)
        
        # EL BOTÓN ESTRELLA
        self._btn(grid_frame, "🏎️ Pista F1 México", lambda: self.iniciar_figura(self.dibujar_f1, "Pista F1 México"), color="#E3B200").grid(row=2, column=1, padx=5, pady=5)

        # PANEL DE SEGURIDAD
        panel_stop = tk.Frame(self, bg=BG_COLOR)
        panel_stop.pack(fill=tk.X, padx=20, pady=10)
        
        btn_stop = tk.Button(panel_stop, text="🛑 PARADA DE EMERGENCIA (E-STOP)", command=self.ejecutar_stop,
                             bg=DANGER_COLOR, fg="white", font=("Segoe UI", 14, "bold"), relief=tk.FLAT, pady=10)
        btn_stop.pack(fill=tk.X)

    # =========================================================
    # 3. LÓGICA DE CONTROL Y SEGURIDAD
    # =========================================================
    def actualizar_estado(self, texto, color=TEXT_COLOR):
        self.lbl_status.config(text=texto, fg=color)
        self.update()

    def conectar(self):
        try:
            self.serial_port = serial.Serial(self.cb_ports.get(), 115200, timeout=0.5)
            time.sleep(2)
            self.enviar_comando(CENTRO_X, CENTRO_Y - 40, z=0)
            self.actualizar_estado("SISTEMA ONLINE", SUCCESS_COLOR)
        except Exception as e:
            messagebox.showerror("Error de Hardware", str(e))

    def solicitar_checklist_pre_figura(self, nombre_figura):
        ventana = tk.Toplevel(self)
        ventana.title("Checklist previo")
        ventana.configure(bg=PANEL_COLOR)
        ventana.resizable(False, False)
        ventana.transient(self)
        ventana.grab_set()

        respuesta = {"ok": False}

        tk.Label(
            ventana,
            text=f"Antes de ejecutar: {nombre_figura}",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 11, "bold"),
        ).pack(padx=16, pady=(12, 10), anchor="w")

        q1_var = tk.StringVar(value="NO")
        q2_var = tk.StringVar(value="NO")

        bloque1 = tk.Frame(ventana, bg=PANEL_COLOR)
        bloque1.pack(fill=tk.X, padx=16, pady=(4, 10))
        tk.Label(
            bloque1,
            text="1) Colocaste el brazo recto y en la orientacion correcta?",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            anchor="w",
            justify=tk.LEFT,
            font=("Segoe UI", 10),
        ).pack(anchor="w")
        tk.Radiobutton(bloque1, text="Si", variable=q1_var, value="SI", bg=PANEL_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(bloque1, text="No", variable=q1_var, value="NO", bg=PANEL_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(side=tk.LEFT)

        bloque2 = tk.Frame(ventana, bg=PANEL_COLOR)
        bloque2.pack(fill=tk.X, padx=16, pady=(0, 12))
        tk.Label(
            bloque2,
            text="2) Conectaste motores/enciende el led verde de la fuente?",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            anchor="w",
            justify=tk.LEFT,
            font=("Segoe UI", 10),
        ).pack(anchor="w")
        tk.Radiobutton(bloque2, text="Si", variable=q2_var, value="SI", bg=PANEL_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(bloque2, text="No", variable=q2_var, value="NO", bg=PANEL_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(side=tk.LEFT)

        def aceptar():
            if q1_var.get() != "SI" or q2_var.get() != "SI":
                messagebox.showwarning("Checklist incompleto", "Debes responder 'Si' a ambas preguntas antes de ejecutar la figura.", parent=ventana)
                return
            respuesta["ok"] = True
            ventana.destroy()

        def cancelar():
            ventana.destroy()

        botones = tk.Frame(ventana, bg=PANEL_COLOR)
        botones.pack(fill=tk.X, padx=16, pady=(0, 14))
        tk.Button(botones, text="Cancelar", command=cancelar, bg=BG_COLOR, fg=TEXT_COLOR, relief=tk.FLAT, width=12).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(botones, text="Continuar", command=aceptar, bg=SUCCESS_COLOR, fg="white", relief=tk.FLAT, width=12).pack(side=tk.RIGHT)

        ventana.protocol("WM_DELETE_WINDOW", cancelar)
        self.wait_window(ventana)
        return respuesta["ok"]

    def verificar_enlace_motores(self, timeout_s=1.5):
        if not self.serial_port:
            return False
        try:
            self.serial_port.reset_input_buffer()
            comando_ping = f"{self.last_q1:.2f},{self.last_q2:.2f},0\n"
            self.serial_port.write(comando_ping.encode('ascii'))

            inicio = time.time()
            while (time.time() - inicio) < timeout_s:
                if self.serial_port.in_waiting:
                    resp = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                    if resp == "OK":
                        return True
            return False
        except Exception:
            return False

    def iniciar_figura(self, funcion_figura, nombre_figura):
        if not self.serial_port:
            messagebox.showwarning("Sin conexión", "Primero conecta el sistema SCARA.")
            return

        if not self.solicitar_checklist_pre_figura(nombre_figura):
            self.actualizar_estado("Checklist cancelado", TEXT_COLOR)
            return

        self.actualizar_estado("Verificando enlace de motores...", ACCENT_COLOR)
        if not self.verificar_enlace_motores():
            self.actualizar_estado("Fallo de enlace con motores", DANGER_COLOR)
            messagebox.showerror(
                "Verificación fallida",
                "No hubo respuesta de los motores (OK).\n"
                "Revisa fuente, cableado y puerto serial antes de dibujar.",
            )
            return

        self.actualizar_estado("Checklist y verificación OK", SUCCESS_COLOR)
        funcion_figura()

    def ejecutar_stop(self):
        """Interrumpe cualquier trayectoria y levanta el lápiz instantáneamente"""
        if not self.serial_port: return
        self.detener_emergencia = True
        self.actualizar_estado("¡PARADA DE EMERGENCIA ACTIVA!", DANGER_COLOR)
        # Enviar comando de levantar lápiz en la última posición conocida
        comando = f"{self.last_q1:.2f},{self.last_q2:.2f},0\n"
        self.serial_port.write(comando.encode('ascii'))

    # =========================================================
    # 4. CAPA DE ABSTRACCIÓN DE HARDWARE (HAL)
    # =========================================================
    def calcular_hal(self, x, y):
        dx = x - CENTRO_X
        dy = y - CENTRO_Y
        x_esc = (dx * ESCALA_X) + CENTRO_X
        y_esc = (dy * ESCALA_Y) + CENTRO_Y
        
        d2 = x_esc**2 + y_esc**2
        D = (d2 - L1**2 - L2**2) / (2 * L1 * L2)
        if not (-1 <= D <= 1): return None, None 
            
        signo_codo = -1 if CODO_DERECHO else 1
        theta2_rad = math.atan2(signo_codo * math.sqrt(1 - D**2), D)
        theta1_rad = math.atan2(y_esc, x_esc) - math.atan2(L2 * math.sin(theta2_rad), L1 + L2 * math.cos(theta2_rad))

        q1_maquina = 90.0 - math.degrees(theta1_rad)
        q2_maquina = -q1_maquina + math.degrees(theta2_rad) + GAMMA
        return q1_maquina, q2_maquina

    def enviar_comando(self, x, y, z):
        if not self.serial_port or self.detener_emergencia: return False
        
        q1, q2 = self.calcular_hal(x, y)
        if q1 is None: return False
            
        # Guardar última posición para el STOP seguro
        self.last_q1 = q1
        self.last_q2 = q2
        
        comando = f"{q1:.2f},{q2:.2f},{z}\n"
        self.serial_port.write(comando.encode('ascii'))
        
        while not self.detener_emergencia:
            if self.serial_port.in_waiting:
                resp = self.serial_port.readline().decode('ascii').strip()
                if resp == "OK": break
        return True

    def reportar_dh_trayectoria(self, nombre, puntos, cerrarlo=True, max_puntos=30):
        self.dh_analyzer.imprimir_reporte_figura(nombre, puntos, cerrarlo=cerrarlo, max_puntos=max_puntos)

    def trazar_linea(self, x1, y1, x2, y2):
        distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        pasos = max(1, int(distancia / RESOLUCION_MM))
        for i in range(1, pasos + 1):
            if self.detener_emergencia: break
            t = i / pasos
            self.enviar_comando(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, z=1) 
            if i % 3 == 0: self.update()

    def ejecutar_trayectoria(self, nombre, puntos, cerrarlo=True):
        if not self.serial_port: return
        self.detener_emergencia = False # Resetear bandera de emergencia
        self.actualizar_estado(f"EJECUTANDO: {nombre}...", ACCENT_COLOR)

        self.reportar_dh_trayectoria(nombre, puntos, cerrarlo=cerrarlo)
        
        self.enviar_comando(puntos[0][0], puntos[0][1], z=0)
        time.sleep(0.3)
        self.enviar_comando(puntos[0][0], puntos[0][1], z=1)
        
        for i in range(len(puntos) - 1):
            if self.detener_emergencia: break
            self.trazar_linea(puntos[i][0], puntos[i][1], puntos[i+1][0], puntos[i+1][1])
            
        if cerrarlo and not self.detener_emergencia:
            self.trazar_linea(puntos[-1][0], puntos[-1][1], puntos[0][0], puntos[0][1])
            
        # Volver al reposo si no hubo emergencia
        if not self.detener_emergencia:
            self.enviar_comando(puntos[-1][0], puntos[-1][1], z=0)
            self.enviar_comando(CENTRO_X, CENTRO_Y - 40, z=0)
            self.actualizar_estado("TAREA COMPLETADA EXITOSAMENTE", SUCCESS_COLOR)

    # =========================================================
    # 5. DICCIONARIO DE TRAZOS (Incluye la pista de F1)
    # =========================================================
    def dibujar_cuadrado(self):
        pts = [(-30, 170), (30, 170), (30, 230), (-30, 230)]
        self.ejecutar_trayectoria("Cuadrado 60x60", pts)

    def dibujar_rectangulo(self):
        pts = [(-40, 180), (40, 180), (40, 220), (-40, 220)]
        self.ejecutar_trayectoria("Rectángulo 80x40", pts)

    def dibujar_triangulo(self):
        pts = [(-30, 175), (30, 175), (0, 227)]
        self.ejecutar_trayectoria("Triángulo", pts)

    def dibujar_pentagono(self):
        radio = 35
        pts = [(CENTRO_X + radio * math.cos(math.radians(90 + i * 72)), 
                CENTRO_Y + radio * math.sin(math.radians(90 + i * 72))) for i in range(5)]
        self.ejecutar_trayectoria("Pentágono", pts)

    def dibujar_circulo(self):
        pts = generar_puntos_circulo(CENTRO_X, CENTRO_Y, radio=30, segmentos=48)
        self.ejecutar_trayectoria("Círculo", pts, cerrarlo=True)

    def dibujar_letra_A(self):
        self.detener_emergencia = False
        if not self.serial_port: return
        self.actualizar_estado("EJECUTANDO: Letra A...", ACCENT_COLOR)

        trazo_externo = [(-20, 170), (0, 230), (20, 170)]
        trazo_central = [(-10, 200), (10, 200)]
        self.reportar_dh_trayectoria("Letra A - trazo exterior", trazo_externo, cerrarlo=False, max_puntos=10)
        self.reportar_dh_trayectoria("Letra A - puente", trazo_central, cerrarlo=False, max_puntos=10)
        
        self.enviar_comando(-20, 170, z=0)
        time.sleep(0.3)
        self.enviar_comando(-20, 170, z=1)
        self.trazar_linea(-20, 170, 0, 230)
        self.trazar_linea(0, 230, 20, 170)
        
        if not self.detener_emergencia:
            self.enviar_comando(20, 170, z=0)
            self.enviar_comando(-10, 200, z=0)
            time.sleep(0.3)
            self.enviar_comando(-10, 200, z=1)
            self.trazar_linea(-10, 200, 10, 200)
            
            self.enviar_comando(10, 200, z=0)
            self.enviar_comando(CENTRO_X, CENTRO_Y - 40, z=0)
            self.actualizar_estado("TAREA COMPLETADA EXITOSAMENTE", SUCCESS_COLOR)

    def dibujar_f1(self):
        """El Gran Premio de México (Autódromo Hermanos Rodríguez)"""
        # Vectorizado paramétrico para encajar en tu espacio de trabajo (70x40 aprox)
        # Puntos: Recta -> Eses -> Foro Sol -> Peraltada
        # Vectorizado Paramétrico de Alta Fidelidad: Autódromo Hermanos Rodríguez
        # Vectorizado Paramétrico de Alta Fidelidad: RED BULL RING (Spielberg)
        # Escala Maximizada: ~85mm x 80mm. Trazado fluido (Curvas Spline)
        pista_f1 = [
            # Recta Principal (Start/Finish)
            (-25.0, 165.0), (-20.0, 165.0), (-15.0, 165.0), (-10.0, 165.0), 
            (-5.0, 165.0), (0.0, 165.0), (5.0, 165.0), (10.0, 165.0), 
            (15.0, 165.0), (20.0, 165.0), (25.0, 165.0), (30.0, 165.0), (35.0, 165.0),

            # Curva 1 (Niki Lauda Kurve) - Derecha cerrada y fluida
            (38.0, 165.2), (40.5, 165.8), (42.5, 166.8), (44.0, 168.2), 
            (44.8, 170.0), (44.5, 172.0), (43.5, 174.0), (42.0, 176.0), (40.5, 178.0),

            # Larga recta en subida (Hacia la Curva 3)
            (38.0, 181.0), (35.0, 184.6), (32.0, 188.2), (29.0, 191.8), 
            (26.0, 195.4), (23.0, 199.0), (20.0, 202.6), (17.0, 206.2), 
            (14.0, 209.8), (11.0, 213.4), (8.0, 217.0), (5.0, 220.6), 
            (2.0, 224.2), (-1.0, 227.8), (-4.0, 231.4), (-7.0, 235.0), 
            (-10.0, 238.6), (-13.0, 242.2),

            # Curva 3 (Remus) - Horquilla de fuerte frenada
            (-14.5, 244.0), (-16.5, 245.2), (-18.8, 245.5), (-21.0, 244.8), 
            (-22.5, 243.2), (-23.0, 241.0), (-22.2, 238.5), (-20.8, 236.0),

            # Recta en bajada (Hacia Schlossgold)
            (-18.5, 233.7), (-16.0, 231.2), (-13.5, 228.7), (-11.0, 226.2), 
            (-8.5, 223.7), (-6.0, 221.2), (-3.5, 218.7), (-1.0, 216.2), 
            (1.5, 213.7), (4.0, 211.2), (6.5, 208.7), (9.0, 206.2), 
            (11.5, 203.7), (14.0, 201.2),

            # Curva 4 (Schlossgold) - Fuerte derecha bajando
            (16.0, 199.0), (17.5, 196.5), (18.2, 193.5), (18.0, 190.5), 
            (17.0, 187.8), (15.5, 185.5), (13.5, 183.5),

            # Curva 6 (Rauch) - Curva rápida y fluida a la izquierda
            (11.0, 182.0), (8.0, 181.0), (5.0, 180.3), (2.0, 180.0), 
            (-1.0, 180.2), (-4.0, 180.8), (-7.0, 181.8),

            # Curva 7 (Würth) - Continúa el barrido a la izquierda
            (-10.0, 183.0), (-13.0, 184.4), (-16.0, 185.8), (-19.0, 187.0), (-22.0, 187.8),

            # Curvas 8 y 9 (Rindt) - Barrido ciego muy rápido a la derecha
            (-25.0, 188.0), (-28.0, 187.5), (-31.0, 186.2), (-34.0, 184.0), 
            (-36.5, 181.0), (-38.5, 177.5),

            # Curva 10 (Red Bull Mobile) - Curva a la derecha hacia la recta principal
            (-39.8, 174.0), (-40.5, 170.5), (-40.0, 167.5), (-38.0, 165.8), 
            (-35.0, 165.2), (-32.0, 165.0), (-28.5, 165.0), 
            
            # Cierre perfecto del circuito
            (-25.0, 165.0)
        ]
        self.ejecutar_trayectoria("Autódromo Hnos. Rodríguez", pista_f1, cerrarlo=True)

if __name__ == "__main__":
    app = ScaraMasterPro()
    app.mainloop()