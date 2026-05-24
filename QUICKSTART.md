# 🚀 QUICKSTART — Guía Paso a Paso para ROBOEGG

> Esta guía te lleva de cero a dibujar tu primera figura.  
> Sigue los pasos **en orden**. No te saltes ninguno.

---

## 📍 Mapa de Ruta

```
PASO 1: Verificar dependencias de software     (5 min)
PASO 2: Compilar y subir el firmware al Arduino (10 min)
PASO 3: Conectar el hardware                    (15 min)
PASO 4: Calibrar el brazo (gamma)               (10 min)
PASO 5: Calibrar la escala (cuadrado de prueba) (10 min)
PASO 6: Dibujar figuras                         (¡diversión!)
```

---

## PASO 1: Verificar Dependencias de Software

### 1.1 Python

Abre una terminal y verifica:

```bash
python3 --version
```

Necesitas **Python 3.11 o superior**. Si no lo tienes:

```bash
sudo apt update && sudo apt install python3 python3-pip python3-tk
```

### 1.2 Instalar pyserial

```bash
cd ~/Descargas/ROBOEGG
pip install -r requirements.txt
```

Verifica que funcione:

```bash
python3 -c "import serial; print('pyserial OK:', serial.__version__)"
python3 -c "import tkinter; print('tkinter OK')"
```

### 1.3 Arduino IDE

Descarga desde [arduino.cc](https://www.arduino.cc/en/software) si no lo tienes.

Necesitas instalar **una librería** dentro del Arduino IDE:

1. Abre Arduino IDE
2. Ve a **Sketch → Include Library → Manage Libraries**
3. Busca **AccelStepper**
4. Instala "AccelStepper by Mike McCauley"

---

## PASO 2: Compilar y Subir el Firmware

### 2.1 Abrir el firmware

1. En Arduino IDE: **File → Open**
2. Navega a: `~/Descargas/ROBOEGG/firmware/scara_2r_controller/scara_2r_controller.ino`

### 2.2 Configurar la placa

1. **Tools → Board → Arduino UNO**
2. **Tools → Port → /dev/ttyUSB0** (o el puerto donde esté tu Arduino)

> 💡 Si no ves el puerto, verifica que el cable USB está conectado y ejecuta:
> ```bash
> ls /dev/ttyUSB* /dev/ttyACM*
> ```

### 2.3 Compilar y subir

1. Haz clic en **✓ Verify** (compila sin subir — verifica que no hay errores)
2. Si compila bien, haz clic en **→ Upload**
3. Espera a que diga "Done uploading"

### 2.4 Verificar el firmware

Abre el **Serial Monitor** (Tools → Serial Monitor):
- Baudrate: **115200**
- Deberías ver: `READY`

Prueba enviar este texto manualmente:

```
0.00,0.00,0
```

Deberías recibir: `OK`

> ✅ Si ves `OK`, el firmware está funcionando.  
> ❌ Si no responde, revisa el puerto y el baudrate.

---

## PASO 3: Conectar el Hardware

### 3.1 Checklist de conexiones

Antes de encender nada, verifica:

| # | Conexión | ¿Listo? |
|---|----------|:-------:|
| 1 | CNC Shield montada sobre Arduino UNO | ☐ |
| 2 | Driver A4988 en slot **X** (Motor 1 — Hombro) | ☐ |
| 3 | Driver A4988 en slot **Y** (Motor 2 — Codo) | ☐ |
| 4 | 3 jumpers en cada slot (M0, M1, M2) para microstepping 1/16 | ☐ |
| 5 | Motor NEMA 17 del hombro → conector X del CNC Shield | ☐ |
| 6 | Motor NEMA 17 del codo → conector Y del CNC Shield | ☐ |
| 7 | Servo SG90 señal (naranja) → Pin D11 | ☐ |
| 8 | Servo SG90 alimentación (rojo) → 5V, (café) → GND | ☐ |
| 9 | Fuente 12V 5A → bornera de la CNC Shield (¡polaridad!) | ☐ |
| 10 | Cable USB Arduino → PC | ☐ |

### 3.2 Secuencia de encendido

**ORDEN IMPORTANTE:**

```
1. Conectar cable USB al Arduino (se enciende el LED azul)
2. Conectar la fuente 12V (se enciende el LED verde en la fuente)
3. Verificar que los drivers A4988 NO estén calientes al tacto
```

> ⚠️ **NUNCA** desconectes los motores con la fuente encendida — puede quemar los drivers.

### 3.3 Posición inicial del brazo

**ANTES de ejecutar cualquier software:**

1. Desconecta la fuente 12V (deja solo el USB)
2. Mueve el brazo **manualmente** hasta que quede **completamente recto** (extensión total)
3. El brazo debe apuntar hacia **adelante** (dirección positiva Y)
4. Reconecta la fuente 12V
5. Los motores se "bloquearán" — esto es normal

```
        ← El brazo debe verse ASÍ →

   [BASE]────────[CODO]────────[LÁPIZ]
                  
         Completamente recto, apuntando al frente
```

---

## PASO 4: Calibrar Gamma (Offset del Codo)

### 4.1 Lanzar la herramienta de calibración

```bash
cd ~/Descargas/ROBOEGG
python3 -m src.calibration.sweep_180
```

### 4.2 Conectar

1. Selecciona tu puerto serial en el dropdown (ej: `/dev/ttyUSB0`)
2. Haz clic en **Conectar**
3. Debería decir "Robot conectado y sincronizado"

### 4.3 Calibrar gamma

El objetivo es que el brazo se mantenga **rígido como una regla** cuando mueves el slider.

1. Mueve el slider lentamente de 90° hacia 0° y luego hacia 180°
2. **Observa el codo**: ¿se dobla? ¿se abre?

| Si el codo... | Entonces gamma debe... |
|--------------|----------------------|
| Se dobla hacia adentro | Aumentar (+) |
| Se abre hacia afuera | Disminuir (−) |

3. Usa los botones **±0.1°** para ajuste fino
4. Repite hasta que el brazo se mantenga perfectamente recto en todo el rango

### 4.4 Guardar el valor

**Anota tu valor de gamma** (ej: `2.0`).

Edita el archivo `src/scara_control/config.py` línea 21:

```python
GAMMA: float = 2.0    # ← Cambia este número por tu valor calibrado
```

> 💡 Cierra la herramienta de calibración cuando termines.

---

## PASO 5: Calibrar la Escala

### 5.1 Preparar el papel

1. Coloca una hoja de papel bajo el lápiz del robot
2. Fija el papel con cinta para que no se mueva
3. Pon un marcador/plumón en el portaherramientas (eje Z)

### 5.2 Dibujar cuadrado de prueba

```bash
cd ~/Descargas/ROBOEGG
python3 run.py
```

1. Selecciona tu puerto serial
2. Haz clic en **CONECTAR SISTEMA** (debe decir "SISTEMA ONLINE")
3. Haz clic en **⬛ Cuadrado**
4. Responde **Sí** a las dos preguntas del checklist
5. Espera a que dibuje

### 5.3 Medir y corregir

Con una regla, mide el cuadrado dibujado:

```
Dimensión esperada: 60 × 60 mm

Si midió 70mm en X y 50mm en Y:
    ESCALA_X = 60 / 70 = 0.857
    ESCALA_Y = 60 / 50 = 1.200
```

Edita `src/scara_control/config.py` líneas 38-41:

```python
ESCALA_X: float = 60.0 / 70.0    # ← Tu medida real en X
ESCALA_Y: float = 60.0 / 50.0    # ← Tu medida real en Y
```

### 5.4 Verificar

1. Dibuja otro cuadrado
2. Mide de nuevo — debe ser **60 ± 2 mm** en ambos ejes
3. Si no, ajusta los valores y repite

---

## PASO 6: ¡Dibujar Figuras!

### 6.1 Lanzar la aplicación

```bash
cd ~/Descargas/ROBOEGG
python3 run.py
```

### 6.2 Flujo de uso

```
   CONECTAR
      ↓
   Seleccionar figura (ej: ▲ Triángulo)
      ↓
   Confirmar checklist (Sí / Sí)
      ↓
   El robot dibuja automáticamente ✏️
      ↓
   "TAREA COMPLETADA EXITOSAMENTE" ✅
      ↓
   Seleccionar otra figura o cerrar
```

### 6.3 Botones disponibles

| Botón | Qué dibuja |
|-------|-----------|
| ⬛ Cuadrado | 60×60mm |
| ▭ Rectángulo | 80×40mm |
| ▲ Triángulo | Equilátero |
| ⬠ Pentágono | Regular, r=35mm |
| ◯ Círculo | r=30mm, 48 puntos |
| A Letra 'A' | Con puente central |
| 🏎️ Pista F1 | Red Bull Ring (~85×80mm) |

### 6.4 Emergencia

Si algo sale mal:

```
🛑 Presiona el botón rojo "PARADA DE EMERGENCIA (E-STOP)"
```

Esto levanta el lápiz inmediatamente y detiene todo movimiento.

---

## 🔧 Solución de Problemas

| Problema | Solución |
|----------|---------|
| "Sin puertos" en la app | Verifica cable USB. Ejecuta `ls /dev/ttyUSB*` |
| "Error de Hardware" al conectar | Cierra Arduino Serial Monitor (no pueden compartir puerto) |
| El brazo no se mueve | Verifica fuente 12V encendida (LED verde) |
| El lápiz no baja | Ajusta ángulos del servo en `firmware/.../scara_2r_controller.ino` líneas 24-25 |
| Cuadrado sale torcido | Recalibra escala (Paso 5) |
| Cuadrado sale como rombo | Ajusta gamma (Paso 4) |
| "Fallo de enlace con motores" | Apaga y enciende la fuente 12V, reconecta |
| El robot se traba a medio dibujo | Presiona E-STOP, verifica que el papel no estorba |

---

## 📋 Resumen de Comandos

```bash
# Verificar dependencias
python3 --version
pip install -r requirements.txt

# Calibrar gamma
python3 -m src.calibration.sweep_180

# Ejecutar la app principal
python3 run.py

# (Alternativa) Ejecutar la app legacy
python3 SCARA.py
```

---

## ¿Qué sigue?

Una vez que domines las figuras básicas:

1. **Agregar nuevas figuras**: Edita `src/scara_control/figures.py`
2. **Ajustar velocidad**: Modifica `RESOLUCION_MM` en `config.py` (menor = más lento pero más suave)
3. **Ver reporte D-H**: Ejecuta `python3 PruebaDH.py` para análisis cinemático detallado
4. **Documentar resultados**: Actualiza el reporte en `report/PLANTILLA_REPORTE.tex`
