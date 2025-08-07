#include <Arduino.h>

// Motor 1 Pins
#define ENCA1 9
#define ENCB1 10
#define PWM1 6
#define IN11 20
#define IN12 21

// Motor 2 Pins
#define ENCA2 11
#define ENCB2 12
#define PWM2 7
#define IN21 18
#define IN22 19

// Motor 3 Pins
#define ENCA3 13
#define ENCB3 14
#define PWM3 8
#define IN31 16
#define IN32 17

// Number of motors
#define NUM_MOTORS 3

// Motor control structure
typedef struct {
  // Pins
  int encA, encB, pwm, in1, in2;
  
  // Position and velocity
  volatile int pos_i;
  volatile float velocity_i;
  volatile long prevT_i;
  
  // Filtered velocity
  float vFilt;
  float vPrev;
  
  // PID control
  float eintegral;
  float eprev;
  
  // Target velocity
  float vt;
  
  // PID constants
  float kp, ki, kd;
} Motor;

// Array of motors
Motor motors[NUM_MOTORS] = {
  {ENCA1, ENCB1, PWM1, IN11, IN12, 0, 0, 0, 0, 0, 0, 0, 0, 30, 5, 0.1}, // Motor 1
  {ENCA2, ENCB2, PWM2, IN21, IN22, 0, 0, 0, 0, 0, 0, 0, 0, 30, 5, 0.1}, // Motor 2
  {ENCA3, ENCB3, PWM3, IN31, IN32, 0, 0, 0, 0, 0, 0, 0, 0, 30, 5, 0.1}  // Motor 3
};

// Timing variables
long prevT = 0;
int posPrev[NUM_MOTORS] = {0};

// UART buffer
char uartBuffer[64];
int bufferIndex = 0;

// Encoder interrupt handlers
void readEncoder1() { handleEncoderInterrupt(0); }
void readEncoder2() { handleEncoderInterrupt(1); }
void readEncoder3() { handleEncoderInterrupt(2); }

// Handle encoder interrupt for a specific motor
void handleEncoderInterrupt(int motorIndex) {
  int b = digitalRead(motors[motorIndex].encB);
  int increment = (b > 0) ? 1 : -1;
  motors[motorIndex].pos_i += increment;
  
  // Compute velocity
  long currT = micros();
  float deltaT = ((float)(currT - motors[motorIndex].prevT_i)) / 1.0e6;
  motors[motorIndex].velocity_i = increment / deltaT;
  motors[motorIndex].prevT_i = currT;
}

// Parse target speeds from UART (format "20.12,30.41,40.11")
void parseTargetSpeeds(char* buffer) {
  char* token = strtok(buffer, ",");
  for (int i = 0; i < NUM_MOTORS && token != NULL; i++) {
    float speed = atof(token);
    if (speed == 0 && token[0] != '0') { // Check for invalid conversion
      Serial.println("Error: Invalid speed value");
      return;
    }
    motors[i].vt = speed;
    token = strtok(NULL, ",");
  }
  if (token != NULL) {
    Serial.println("Error: Too many values in UART data");
  }
}

// Send actual speeds via UART1
void sendActualSpeeds() {
  String output;
  for (int i = 0; i < NUM_MOTORS; i++) {
    output += String(motors[i].vFilt, 2);
    if (i < NUM_MOTORS - 1) {
      output += ",";
    }
  }
  Serial1.println(output);
  
  // Optional: Also send to USB for debugging
  Serial.println(output);
}

// Set motor speed and direction
void setMotor(int dir, int pwmVal, int pwm, int in1, int in2) {
  analogWrite(pwm, pwmVal);
  if (dir == 1) {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
  } else if (dir == -1) {
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
  } else {
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
  }
}

void setup() {
  // Initialize all motors
  for (int i = 0; i < NUM_MOTORS; i++) {
    pinMode(motors[i].encA, INPUT);
    pinMode(motors[i].encB, INPUT);
    pinMode(motors[i].pwm, OUTPUT);
    pinMode(motors[i].in1, OUTPUT);
    pinMode(motors[i].in2, OUTPUT);
    
    // Set PID constants (tune these for your system)
    motors[i].kp = 5.0;
    motors[i].ki = 10.0;
    motors[i].kd = 0.1;
    
    // Initialize target speed
    motors[i].vt = 0.0;
  }
  
  // Attach interrupts for each encoder
  attachInterrupt(digitalPinToInterrupt(ENCA1), readEncoder1, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCA2), readEncoder2, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCA3), readEncoder3, RISING);
  pinMode(25, OUTPUT);
  Serial.begin(115200);  // USB serial for debugging
  Serial1.begin(115200); // UART1 for target speed communication
  
  // while(!Serial1.available())
  // {
  //   digitalWrite(25, HIGH);
  //   delay(100);
  //   digitalWrite(25, LOW);
  //   delay(100);
  // }

  digitalWrite(25, HIGH);
}

void loop() {
  // Timing
  long currT = micros();
  float deltaT = ((float)(currT - prevT)) / 1.0e6;
  prevT = currT;

  // Process UART data if available
  while (Serial1.available()) {
    char c = Serial1.read();
    if (c == '\n') {
      uartBuffer[bufferIndex] = '\0';
      Serial.print("Received UART data: ");
      Serial.println(uartBuffer); // Debugging: Print received data
      parseTargetSpeeds(uartBuffer);
      bufferIndex = 0;
    } else if (bufferIndex < sizeof(uartBuffer) - 1) {
      uartBuffer[bufferIndex++] = c;
    } else {
      Serial.println("Error: UART buffer overflow");
      bufferIndex = 0; // Reset buffer to prevent overflow
    }
  }
  
  // Control each motor
  for (int i = 0; i < NUM_MOTORS; i++) {
    // Read position and velocity (with interrupts disabled)
    int pos = 0;
    float velocity = 0;
    noInterrupts();
    pos = motors[i].pos_i;
    velocity = motors[i].velocity_i;
    interrupts();
    
    // Compute velocity (alternative method)
    float velocityAlt = (pos - posPrev[i]) / deltaT;
    posPrev[i] = pos;
    
    // Convert count/s to RPM (adjust this based on your encoder CPR)
    float v = velocity / 1500.0*60.0;       // Method 1 (interrupt)
    float vAlt = velocityAlt / 1500.0*60.0; // Method 2 (loop timing)
    
    // Low-pass filter (25 Hz cutoff)
    motors[i].vFilt = 0.854 * motors[i].vFilt + 0.0728 * v + 0.0728 * motors[i].vPrev;
    motors[i].vPrev = v;
    
    // PID control
    float e = motors[i].vt - motors[i].vFilt;
    motors[i].eintegral += e * deltaT;
    float dedt = (e - motors[i].eprev) / deltaT;
    motors[i].eprev = e;
    
    float u = motors[i].kp * e + motors[i].ki * motors[i].eintegral + motors[i].kd * dedt;
    
    // Set motor direction and power
    int dir = (u > 0) ? 1 : -1;
    int pwr = constrain((int)fabs(u), 0, 255);
    setMotor(dir, pwr, motors[i].pwm, motors[i].in1, motors[i].in2);
  }
  
  // Send actual speeds via UART1
  // sendActualSpeeds();
  
  // Small delay to prevent USB serial flooding
  delay(1);
}
