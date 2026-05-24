# Guía de Cableado — ROBOEGG SCARA 2R

## Bill of Materials (Electrónica)

| Componente | Cantidad | Especificación |
|-----------|:--------:|---------------|
| Arduino UNO | 1 | Microcontrolador ATmega328P |
| CNC Shield V3 | 1 | Interfaz para drivers de motor |
| Driver A4988 | 2 | Con disipador de calor |
| Motor NEMA 17 | 2 | ~4 kg·cm de torque |
| Servo SG90S | 1 | Engranajes metálicos (preferible) |
| Fuente 12V DC | 1 | 5A mínimo (tipo eliminador) |
| Correa GT2 | 2 | 280 mm bucle cerrado |
| Poleas 20T/60T | 2 juegos | Aluminio, reducción 3:1 |
| Rodamientos 608ZZ | 8 | 8 × 22 × 7 mm |
| Microswitches | 2 | Fines de carrera (homing) |
| Cables Dupont | Set | Macho-hembra y macho-macho |

## Diagrama de Conexiones

### CNC Shield V3 — Asignación de Pines

```
┌─────────────────────────────────────────┐
│           CNC SHIELD V3                  │
│                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  EJE X   │  │  EJE Y   │  │  EJE Z   │ │
│  │ (Motor 1)│  │ (Motor 2)│  │ (vacío)  │ │
│  │ Hombro   │  │  Codo    │  │          │ │
│  └─────────┘  └─────────┘  └─────────┘ │
│                                          │
│  Jumpers: [M0][M1][M2] ← TODOS puestos │
│           (Microstepping 1/16)           │
│                                          │
│  ENABLE: Pin D8 → LOW = drivers activos  │
│                                          │
│  Bornera 12V: [+] [−] ← Fuente de poder │
└─────────────────────────────────────────┘
```

### Asignación de Pines Arduino

| Pin Arduino | Función | Destino |
|:-----------:|---------|---------|
| D2 | STEP Motor 1 | Eje X (CNC Shield) |
| D5 | DIR Motor 1 | Eje X (CNC Shield) |
| D3 | STEP Motor 2 | Eje Y (CNC Shield) |
| D6 | DIR Motor 2 | Eje Y (CNC Shield) |
| D8 | ENABLE | Habilitación de drivers |
| D11 | PWM Servo | Señal del SG90S |

### Conexión del Servo SG90S (Eje Z)

La CNC Shield **no tiene pin PWM dedicado** para servos. Se utiliza el pin D11:

```
Servo SG90S:
├── Cable naranja (señal) → Pin D11 del Arduino
├── Cable rojo (5V)       → Pin 5V de la CNC Shield
└── Cable café (GND)      → Pin GND de la CNC Shield
```

### Fines de Carrera (Homing)

```
Microswitch X-min → Pin X-min de la CNC Shield
Microswitch Y-min → Pin Y-min de la CNC Shield

Conexión: NC (Normalmente Cerrado) recomendado
           COM → GND
           NC  → Pin de señal
```

## ⚠️ Precauciones Críticas

1. **Polaridad de la fuente**: Verificar `+` y `−` antes de conectar. Inversión = daño permanente a drivers
2. **VREF de A4988**: Ajustar el potenciómetro del driver **antes** de conectar motores. VREF ≈ 0.7V para NEMA 17 estándar
3. **Jumpers de microstepping**: Los 3 jumpers (M0, M1, M2) deben estar instalados para 1/16 de paso
4. **Secuencia de encendido**: Primero conectar la fuente 12V, luego el USB al Arduino
