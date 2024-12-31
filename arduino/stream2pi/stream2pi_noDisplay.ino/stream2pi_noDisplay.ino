#include <LiquidCrystal.h>

// LCD Configuration
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

// Ultrasonic Sensor Configuration
const int trigPin = 10; // Trigger pin
const int echoPin = 11; // Echo pin
const float tankHeight = 1.0; // Total height of the tank in meters

// TDS Sensor Configuration
#define TdsSensorPin A1
#define VREF 5.0 // Reference voltage for Arduino
#define SCOUNT 30 // Number of samples for median filtering

int analogBuffer[SCOUNT]; // Buffer to store analog readings
int analogBufferTemp[SCOUNT]; // Temporary buffer for median filtering
int analogBufferIndex = 0; // Index for circular buffer

float averageVoltage = 0; // Average voltage
float tdsValue = 0; // Calculated TDS value
float temperature = 25.0; // Water temperature for compensation

// Simulated Values for Other Sensors
float currentWaterTemp = 25.0; // Temperature in °C
float currentEC = 1.5;         // Electrical conductivity in mS/cm
float currentTDS = 0.0;        // TDS in ppm
float currentPH = 6.5;         // pH value
float currentWaterLevel = 0.0; // Measured water level in meters

// Sampling Intervals
const unsigned long samplingInterval = 1000; // 1 second
unsigned long lastSampleTime = 0;
unsigned long lastDisplayUpdateTime = 0;

// Display Variables
const int displayInterval = 2000; // 2 seconds per measurement
int currentMeasurement = 0;

void setup() {
  // Initialize LCD
  lcd.begin(16, 2);
  lcd.print("Initializing...");
  delay(2000);

  // Ultrasonic Sensor Pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // TDS Sensor Pin
  pinMode(TdsSensorPin, INPUT);

  // Serial Communication
  Serial.begin(9600);
  lcd.clear();
}

void loop() {
  unsigned long currentTime = millis();

  // Sample and stream data every second
  if (currentTime - lastSampleTime >= samplingInterval) {
    lastSampleTime = currentTime;
    sampleAndStreamData();
  }

  // Update LCD display every 2 seconds
  if (currentTime - lastDisplayUpdateTime >= displayInterval) {
    lastDisplayUpdateTime = currentTime;
    updateDisplay();
  }
}

void sampleAndStreamData() {
  // Measure water level using ultrasonic sensor
  currentWaterLevel = measureWaterLevel();

  // Measure TDS using TDS sensor
  currentTDS = measureTDS();

  // Simulate random fluctuations for other sensors
  currentWaterTemp += randomFloat(-0.3, 0.3);
  currentEC += randomFloat(-0.05, 0.05);
  currentPH += randomFloat(-0.1, 0.1);

  // Stream the data to the Serial port
  Serial.print("WATER_LEVEL:");
  Serial.print(currentWaterLevel, 2);
  Serial.print(",WATER_TEMP:");
  Serial.print(currentWaterTemp, 1);
  Serial.print(",EC:");
  Serial.print(currentEC, 2);
  Serial.print(",TDS:");
  Serial.print(currentTDS, 1);
  Serial.print(",PH:");
  Serial.println(currentPH, 1);
}

void updateDisplay() {
  lcd.clear();

  // Cycle through measurements
  switch (currentMeasurement) {
    case 0:
      lcd.print("Water Level:");
      lcd.setCursor(0, 1);
      lcd.print(currentWaterLevel, 2);
      lcd.print(" m");
      break;
    case 1:
      lcd.print("Water Temp:");
      lcd.setCursor(0, 1);
      lcd.print(currentWaterTemp, 1);
      lcd.print(" C");
      break;
    case 2:
      lcd.print("EC:");
      lcd.setCursor(0, 1);
      lcd.print(currentEC, 2);
      lcd.print(" mS/cm");
      break;
    case 3:
      lcd.print("TDS:");
      lcd.setCursor(0, 1);
      lcd.print(currentTDS, 1);
      lcd.print(" ppm");
      break;
    case 4:
      lcd.print("pH:");
      lcd.setCursor(0, 1);
      lcd.print(currentPH, 1);
      break;
  }

  // Move to the next measurement
  currentMeasurement = (currentMeasurement + 1) % 5;
}

float measureWaterLevel() {
  // Send a 10-microsecond pulse to trigger pin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read the duration of the echo signal
  long duration = pulseIn(echoPin, HIGH, 40000); // Timeout after 40ms

  if (duration == 0) {
    // No echo received
    return 0.0;
  }

  // Convert the duration to distance (meters)
  float distance = (duration / 2.0) * 0.000343;

  // Calculate water level
  float waterLevel = tankHeight - distance;

  // Ensure non-negative water level
  return max(waterLevel, 0.0);
}

float measureTDS() {
  // Read analog value into circular buffer
  analogBuffer[analogBufferIndex] = analogRead(TdsSensorPin);
  analogBufferIndex++;
  if (analogBufferIndex == SCOUNT) {
    analogBufferIndex = 0; // Reset index
  }

  // Copy buffer for filtering
  for (int i = 0; i < SCOUNT; i++) {
    analogBufferTemp[i] = analogBuffer[i];
  }

  // Calculate median voltage
  int medianValue = getMedianNum(analogBufferTemp, SCOUNT);
  averageVoltage = medianValue * VREF / 1024.0;

  // Apply temperature compensation
  float compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0);
  float compensationVoltage = averageVoltage / compensationCoefficient;

  // Convert voltage to TDS
  tdsValue = (133.42 * compensationVoltage * compensationVoltage * compensationVoltage)
             - (255.86 * compensationVoltage * compensationVoltage)
             + (857.39 * compensationVoltage);

  return tdsValue; // Return TDS in ppm
}

int getMedianNum(int bArray[], int iFilterLen) {
  int bTab[iFilterLen];
  for (int i = 0; i < iFilterLen; i++) {
    bTab[i] = bArray[i];
  }

  // Sort the array
  for (int j = 0; j < iFilterLen - 1; j++) {
    for (int i = 0; i < iFilterLen - j - 1; i++) {
      if (bTab[i] > bTab[i + 1]) {
        int temp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = temp;
      }
    }
  }

  // Return median value
  if ((iFilterLen & 1) > 0) {
    return bTab[(iFilterLen - 1) / 2];
  } else {
    return (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  }
}

float randomFloat(float min, float max) {
  return min + ((float)rand() / RAND_MAX) * (max - min);
}
