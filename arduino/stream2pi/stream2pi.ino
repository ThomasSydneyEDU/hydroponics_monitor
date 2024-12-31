#include "DFRobot_EC.h"
#include <EEPROM.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Ultrasonic Sensor Configuration
const int trigPin = 10; // Trigger pin
const int echoPin = 11; // Echo pin
const float tankHeight = 1.0; // Total height of the tank in meters

// EC Sensor Pin
#define EC_PIN A1

// DS18B20 Sensor Pin
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Variables for EC, TDS, and temperature
float voltage = 0.0, ecValue = 0.0, tdsValue = 0.0, temperature = 25.0;
DFRobot_EC ec;

// pH Sensor Configuration
#define PH_PIN A2 // Analog pin connected to pH sensor
float slope = 12.2;                  // Slope determined during calibration
float calibration_voltage = 1.916;   // Voltage corresponding to pH 7.0
unsigned long int avgval; 
int buffer_arr[10], temp;
float ph_act;

// Real-time measurements
float currentWaterLevel = 0.0; // Measured water level in meters

// Sampling Intervals
const unsigned long samplingInterval = 1000; // 1 second
unsigned long lastSampleTime = 0;

void setup() {
  // Ultrasonic Sensor Pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Initialize DS18B20 Temperature Sensor
  sensors.begin();

  // Initialize EC Sensor
  ec.begin();

  // Initialize Serial Communication
  Serial.begin(115200);
  Serial.println("Integrated Sensor Array with TDS Ready");
}

void loop() {
  unsigned long currentTime = millis();

  // Sample and stream data every second
  if (currentTime - lastSampleTime >= samplingInterval) {
    lastSampleTime = currentTime;
    sampleAndStreamData();
  }
}

void sampleAndStreamData() {
  // Measure water level using ultrasonic sensor
  currentWaterLevel = measureWaterLevel();

  // Measure temperature using DS18B20
  temperature = measureTemperature();

  // Measure EC using the EC sensor
  ecValue = measureEC();

  // Calculate TDS from EC
  tdsValue = ecValue * 500;

  // Measure pH using the calibrated pH sensor
  ph_act = measurePH();

  // Stream the data to the Serial port
  Serial.print("WATER_LEVEL:");
  Serial.print(currentWaterLevel, 2);
  Serial.print(" m, WATER_TEMP:");
  Serial.print(temperature, 1);
  Serial.print(" °C, EC:");
  Serial.print(ecValue, 2);
  Serial.print(" ms/cm, TDS:");
  Serial.print(tdsValue, 1);
  Serial.print(" ppm, PH:");
  Serial.println(ph_act, 2);
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

float measureEC() {
  // Read voltage from EC sensor
  voltage = analogRead(EC_PIN) / 1024.0 * 5000;

  // Convert voltage to EC with temperature compensation
  return ec.readEC(voltage, temperature);
}

float measurePH() {
  // Collect and sort 10 samples from the pH sensor
  for (int i = 0; i < 10; i++) { 
    buffer_arr[i] = analogRead(PH_PIN);
    delay(30);
  }
  for (int i = 0; i < 9; i++) {
    for (int j = i + 1; j < 10; j++) {
      if (buffer_arr[i] > buffer_arr[j]) {
        temp = buffer_arr[i];
        buffer_arr[i] = buffer_arr[j];
        buffer_arr[j] = temp;
      }
    }
  }

  // Average the middle 6 samples
  avgval = 0;
  for (int i = 2; i < 8; i++) {
    avgval += buffer_arr[i];
  }

  // Convert the average to a voltage
  float volt = (float)avgval * 5 / 1024.0 / 6;

  // Calculate the pH value using the calibration equation
  return 7 + (slope * (volt - calibration_voltage));
}

float measureTemperature() {
  sensors.requestTemperatures(); // Request temperature from DS18B20
  return sensors.getTempCByIndex(0); // Return temperature in Celsius
}
