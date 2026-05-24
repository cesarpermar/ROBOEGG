# Security Policy — ROBOEGG SCARA Robot

## ⚠️ Hardware Safety Considerations

This project controls **physical robotic hardware** (stepper motors, servo actuators). Improper operation can result in:

- Damage to the robot structure or work surface
- Unexpected motor movements
- Servo overload or burnout

## 🛡️ Built-in Safety Mechanisms

### 1. Workspace Zone Validation
All Cartesian coordinates are validated against the robot's reachable workspace before any motor command is sent. Points outside the safe zone are **rejected** and the robot returns to its home position.

### 2. Emergency Stop (E-STOP)
The GUI provides a hardware-independent emergency stop button that:
- Immediately sets the `detener_emergencia` flag
- Lifts the pen (Z=0) at the last known position
- Halts all trajectory execution

### 3. Serial Timeout Protection
Every motor command waits for an `OK` acknowledgment from the Arduino firmware. If no response is received within the configured timeout (default: 15 seconds), the system aborts and returns to home.

### 4. Pre-Flight Checklist
Before executing any figure, the operator must confirm:
- The arm is in the correct starting orientation
- Motors are powered and the green LED on the power supply is active

## 🔐 Reporting a Safety Issue

If you discover a safety-related bug (e.g., the robot moves without validation, the E-STOP doesn't respond, or the serial protocol can desynchronize), please:

1. **Do not operate the robot** until the issue is resolved
2. Open a GitHub Issue with the label `safety`
3. Include: steps to reproduce, firmware version, Python version, and hardware configuration

## 📌 Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Current |
| < 1.0   | ❌ Legacy (monolithic, no modular safety layer) |
