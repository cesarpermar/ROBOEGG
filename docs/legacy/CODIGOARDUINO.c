#include <AccelStepper.h>
#include <Servo.h>

// ==============================================================================
// 1. PINES (CNC Shield V3)
// ==============================================================================
#define PIN_EN        8
#define PIN_STEP_M1   2   // Motor 1 (Hombro) STEP
#define PIN_DIR_M1    5   // Motor 1 (Hombro) DIR
#define PIN_STEP_M2   3   // Motor 2 (Codo) STEP
#define PIN_DIR_M2    6   // Motor 2 (Codo) DIR
#define PIN_SERVO     11  // Servo (Eje Z)

// ==============================================================================
// 2. OBJETOS Y PARAMETROS
// ==============================================================================
AccelStepper stepper1(AccelStepper::DRIVER, PIN_STEP_M1, PIN_DIR_M1);
AccelStepper stepper2(AccelStepper::DRIVER, PIN_STEP_M2, PIN_DIR_M2);
Servo penServo;

const int ANGULO_ARRIBA = 90;
const int ANGULO_ABAJO  = 135;

// 200 pasos/rev * 16 microsteps * reduccion 3:1 = 9600 pasos/rev
const float PASOS_POR_GRADO = 9600.0f / 360.0f;

// Ajusta estos valores si quieres mas suavidad/rapidez
const float MAX_SPEED_M1 = 900.0f;
const float MAX_SPEED_M2 = 900.0f;
const float ACCEL_M1     = 1200.0f;
const float ACCEL_M2     = 1200.0f;

// Estado actual de Z para evitar escribir servo en cada punto
int estadoZActual = -1; // -1 = desconocido al inicio

// ==============================================================================
// 3. FUNCIONES AUXILIARES
// ==============================================================================
void setPenState(int estadoZ) {
  if (estadoZ == estadoZActual) return; // No repetir accion ni delay

  if (estadoZ == 0) {
    penServo.write(ANGULO_ARRIBA);
    delay(80);   // menor tiempo al subir
  } else {
    penServo.write(ANGULO_ABAJO);
    delay(90);   // un poco mas al bajar para asentamiento
  }

  estadoZActual = estadoZ;
}

void moverMotoresAGrados(float q1_grados, float q2_grados) {
  long target1 = lround(q1_grados * PASOS_POR_GRADO);
  long target2 = lround(q2_grados * PASOS_POR_GRADO);

  stepper1.moveTo(target1);
  stepper2.moveTo(target2);

  // Movimiento con aceleracion/desaceleracion (mas suave)
  while (stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0) {
    stepper1.run();
    stepper2.run();
  }
}

// ==============================================================================
// 4. SETUP
// ==============================================================================
void setup() {
  Serial.begin(115200);

  pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_EN, LOW); // habilita drivers

  penServo.attach(PIN_SERVO);
  setPenState(0); // lapiz arriba al inicio

  stepper1.setMaxSpeed(MAX_SPEED_M1);
  stepper2.setMaxSpeed(MAX_SPEED_M2);
  stepper1.setAcceleration(ACCEL_M1);
  stepper2.setAcceleration(ACCEL_M2);

  Serial.println("READY");
}

// ==============================================================================
// 5. LOOP
// ==============================================================================
void loop() {
  if (Serial.available() <= 0) return;

  String data = Serial.readStringUntil('\n');
  data.trim();
  if (data.length() == 0) return;

  int coma1 = data.indexOf(',');
  int coma2 = data.indexOf(',', coma1 + 1);

  if (coma1 <= 0 || coma2 <= 0) {
    Serial.println("ERR");
    return;
  }

  float q1_grados = data.substring(0, coma1).toFloat();
  float q2_grados = data.substring(coma1 + 1, coma2).toFloat();
  int estadoZ = data.substring(coma2 + 1).toInt();

  // 1) Actualiza Z solo si cambia (evita micro-golpes por cada punto)
  setPenState(estadoZ);

  // 2) Mueve articulaciones
  moverMotoresAGrados(q1_grados, q2_grados);

  Serial.println("OK");
}
