#include <AccelStepper.h>
#include <Servo.h>

// ============================================================================
// FIRMWARE SCARA 2R + Servo Z
// Protocolo serial esperado desde Python: q1,q2,z\n
// Ejemplo: 10.50,-22.30,0
// Respuesta al finalizar movimiento: OK
// ============================================================================

// 1) PINES (CNC Shield V3)
#define PIN_EN        8
#define PIN_STEP_M1   2
#define PIN_DIR_M1    5
#define PIN_STEP_M2   3
#define PIN_DIR_M2    6
#define PIN_SERVO     11

// 2) OBJETOS Y PARAMETROS
AccelStepper stepper1(AccelStepper::DRIVER, PIN_STEP_M1, PIN_DIR_M1);
AccelStepper stepper2(AccelStepper::DRIVER, PIN_STEP_M2, PIN_DIR_M2);
Servo penServo;

const int ANGULO_ARRIBA = 5;
const int ANGULO_ABAJO  = 175;

// 200 pasos/rev * 16 microsteps * reduccion 3:1 = 9600 pasos/rev
const float PASOS_POR_GRADO = 9600.0f / 360.0f;

const float MAX_SPEED_M1 = 900.0f;
const float MAX_SPEED_M2 = 900.0f;
const float ACCEL_M1     = 1200.0f;
const float ACCEL_M2     = 1200.0f;

int estadoZActual = -1;

void setPenState(int estadoZ) {
  if (estadoZ == estadoZActual) return;

  if (estadoZ == 0) {
    penServo.write(ANGULO_ARRIBA);
    delay(80);
  } else {
    penServo.write(ANGULO_ABAJO);
    delay(90);
  }

  estadoZActual = estadoZ;
}

void moverMotoresAGrados(float q1_grados, float q2_grados) {
  long target1 = lround(q1_grados * PASOS_POR_GRADO);
  long target2 = lround(q2_grados * PASOS_POR_GRADO);

  stepper1.moveTo(target1);
  stepper2.moveTo(target2);

  while (stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0) {
    stepper1.run();
    stepper2.run();
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_EN, LOW);  // habilita drivers

  penServo.attach(PIN_SERVO);
  setPenState(0);

  stepper1.setMaxSpeed(MAX_SPEED_M1);
  stepper2.setMaxSpeed(MAX_SPEED_M2);
  stepper1.setAcceleration(ACCEL_M1);
  stepper2.setAcceleration(ACCEL_M2);

  Serial.println("READY");
}

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

  setPenState(estadoZ);
  moverMotoresAGrados(q1_grados, q2_grados);

  Serial.println("OK");
}
