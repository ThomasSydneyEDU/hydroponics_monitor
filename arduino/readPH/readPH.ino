#include <Wire.h>

// Calibration constants from your setup
float slope = 12.2;                  // Slope determined during calibration
float calibration_voltage = 1.916;   // Voltage corresponding to pH 7.0

int pHsensor = A0;                   // pH sensor connected to analog pin A0
unsigned long int avgval; 
int buffer_arr[10], temp;

float ph_act;

// Timing variables
unsigned long lastDisplayTime = 0;   // Tracks the last display update time
const unsigned long displayInterval = 1000; // Interval for displaying pH values (1 second)

void setup() {
  Serial.begin(9600);                // Initialize Serial Communication
  pinMode(pHsensor, INPUT);          // Set pH sensor pin as input
  Serial.println("pH Measurement Ready");
}

void loop() {
  // Collect and sort 10 samples from the pH sensor
  for (int i = 0; i < 10; i++) { 
    buffer_arr[i] = analogRead(pHsensor);
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
  ph_act = 7 + (slope * (volt - calibration_voltage));

  // Print the pH value every second
  unsigned long currentTime = millis();
  if (currentTime - lastDisplayTime >= displayInterval) {
    lastDisplayTime = currentTime;

    // Print the pH value to the Serial Monitor
    Serial.print("Voltage: ");
    Serial.print(volt, 3);           // Voltage with 3 decimal places
    Serial.print(" V    pH Value: ");
    Serial.println(ph_act, 2);       // pH with 2 decimal places
  }
}
