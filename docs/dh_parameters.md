# Parámetros Denavit-Hartenberg — ROBOEGG SCARA 2R

## Convención D-H Estándar

El robot SCARA ROBOEGG es un manipulador planar de 2 eslabones (2R). Se utiliza la convención estándar de Denavit-Hartenberg para describir la cinemática del sistema.

### Tabla de Parámetros

| Eslabón (i) | θᵢ (variable) | dᵢ (mm) | aᵢ (mm) | αᵢ (°) |
|:-----------:|:--------------:|:-------:|:-------:|:------:|
| 1 | q₁ | 0 | 150.0 | 0 |
| 2 | q₂ | 0 | 159.94 | 0 |

### Constantes Geométricas

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| L₁ | 150.0 mm | Longitud del eslabón 1 (hombro → codo) |
| L₂ nominal | 150.0 mm | Longitud nominal del eslabón 2 |
| L₂ efectivo | 159.94 mm | √(150² + 55.5²) — incluye offset del end-effector |
| γ (gamma) | 2.0° | Corrección angular calibrada del codo |
| Escala X | 60/70 ≈ 0.857 | Factor de corrección dimensional en X |
| Escala Y | 60/50 = 1.200 | Factor de corrección dimensional en Y |

### Relación L₂ Efectivo

El eslabón 2 tiene un offset perpendicular de 55.5 mm en el end-effector, lo que modifica la longitud efectiva:

```
L₂_eff = √(L₂² + offset²) = √(150² + 55.5²) = 159.94 mm
```

---

## Cinemática Inversa

### Algoritmo

Dado un punto objetivo (x, y) en coordenadas cartesianas del workspace:

**Paso 1 — Compensación de escala:**
```
x_esc = (x - Cx) · ESCALA_X + Cx
y_esc = (y - Cy) · ESCALA_Y + Cy
```

**Paso 2 — Ley de cosenos para q₂:**
```
D = (x_esc² + y_esc² - L₁² - L₂²) / (2·L₁·L₂)
```

**Paso 3 — Validación de alcance:**
```
Si |D| > 1 → Punto inalcanzable
```

**Paso 4 — Ángulo del codo (codo derecho):**
```
q₂ = atan2(-√(1 - D²), D)
```

**Paso 5 — Ángulo del hombro:**
```
q₁ = atan2(y_esc, x_esc) - atan2(L₂·sin(q₂), L₁ + L₂·cos(q₂))
```

**Paso 6 — Conversión a ángulos de máquina:**
```
q₁_máquina = 90° - q₁
q₂_máquina = -q₁_máquina + q₂ + γ
```

### Diagrama del Workspace

```
           Y (mm)
           ↑
     240 ──┤        ┌─────────┐
           │        │ Zona de │
     200 ──┤  ──────│ Trabajo │──────  ← Centro (0, 200)
           │        │  Segura │
     160 ──┤        └─────────┘
           │
     ──────┼────────┬─────────┬──────→ X (mm)
          -40       0         40
```

---

## Configuración de Motores

### Transmisión

| Componente | Valor |
|-----------|-------|
| Pasos por revolución (motor) | 200 (1.8°/paso) |
| Microstepping | 1/16 |
| Reducción mecánica | 3:1 (20T → 60T) |
| **Pasos por revolución (eje)** | **9600** |
| **Pasos por grado** | **26.667** |

### Velocidades

| Parámetro | Motor 1 (Hombro) | Motor 2 (Codo) |
|-----------|:-----------------:|:--------------:|
| Velocidad máxima | 900 pasos/s | 900 pasos/s |
| Aceleración | 1200 pasos/s² | 1200 pasos/s² |
