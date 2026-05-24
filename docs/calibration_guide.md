# Guía de Calibración — ROBOEGG SCARA 2R

## Resumen

La calibración del robot SCARA involucra tres etapas:
1. **Alineación mecánica** — Posicionar el brazo en su orientación de referencia
2. **Calibración de gamma** — Ajustar el offset angular del codo
3. **Calibración de escala** — Corregir las dimensiones reales vs. esperadas

## Requisitos

- Robot ensamblado y cableado correctamente (ver [Guía de Cableado](wiring_guide.md))
- Firmware cargado en Arduino
- Python con pyserial instalado

---

## Etapa 1: Alineación Mecánica

### Procedimiento

1. **Desconectar motores** (quitar cables de NEMA 17 del CNC Shield)
2. **Posicionar manualmente** el brazo en línea recta (extensión completa)
3. El brazo debe apuntar en la dirección positiva Y (hacia adelante)
4. **Reconectar motores** con el brazo en esta posición

> ⚠️ **Importante**: Esta posición define el "cero" del robot. Los ángulos q₁ y q₂ se miden desde aquí.

---

## Etapa 2: Calibración de Gamma

### Herramienta

Usar la aplicación de calibración de barrido:

```bash
python -m src.calibration.sweep_180
```

### Procedimiento

1. **Conectar** al puerto serial
2. Usar los botones de posición rápida: **0°**, **90°**, **180°**
3. Verificar que el brazo se mantiene **recto como una regla** en las 3 posiciones
4. Si el codo "se dobla" durante el barrido:
   - Ajustar gamma con los botones **±0.1°**, **±1°**, **±5°**
   - El valor correcto hace que el brazo se mantenga rígido en todo el rango
5. **Anotar el valor final de gamma** para usarlo en `src/scara_control/config.py`

### Criterio de Aceptación

- El brazo debe verse como una barra rígida al mover el slider de 0° a 180°
- No debe haber flexión visible en la articulación del codo

---

## Etapa 3: Calibración de Escala

### Procedimiento

1. Dibujar un **cuadrado de referencia** (nominalmente 60×60 mm)
2. **Medir** las dimensiones reales del cuadrado trazado en papel
3. Calcular los factores de corrección:

```
ESCALA_X = dimensión_deseada_X / dimensión_medida_X
ESCALA_Y = dimensión_deseada_Y / dimensión_medida_Y
```

### Ejemplo

Si el cuadrado de 60mm se trazó como 70mm en X y 50mm en Y:

```
ESCALA_X = 60 / 70 ≈ 0.857
ESCALA_Y = 60 / 50 = 1.200
```

4. Actualizar los valores en `src/scara_control/config.py`
5. Repetir el trazo y verificar las dimensiones

---

## Perfil de Calibración

El archivo `config/calibration_profile.json` almacena los parámetros de calibración avanzados:

```json
{
  "workspace": {
    "offset_x": 0.0,
    "offset_y": 0.0,
    "escala_x": 0.857,
    "escala_y": 1.200,
    "rotacion_grados": 0.0
  }
}
```

## Verificación Final

Después de calibrar, trazar las siguientes figuras y verificar:

| Figura | Verificación |
|--------|-------------|
| Cuadrado | Los 4 lados deben medir 60 ± 2 mm |
| Círculo | Debe verse circular, no ovalado |
| Triángulo | Los ángulos deben coincidir visualmente |
| Repetibilidad | Trazar 3 veces la misma figura — deben superponerse |
