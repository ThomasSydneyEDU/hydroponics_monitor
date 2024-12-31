#include <Wire.h>

// Initial calibration constants
float slope = 12.2;           // Default slope
float calibration_voltage = 1.916; // Voltage corresponding to pH 7.0 (set during calibration)

int pHsensor = A0;
int phval = 0; 
unsigned long int avgval; 
int buffer_arr[10], temp;

float ph_act;

// Timing variables
unsigned long lastDisplayTime = 0; // Tracks the last display update time
const unsigned long displayInterval = 1000; // Interval for displaying pH values (1 second)

void setup() {
  Serial.begin(9600);
  pinMode(pHsensor, INPUT);
  Serial.println("pH Meter Ready");
  Serial.println("Type 'set slope <value>' to adjust slope.");
  Serial.println("Voltage at pH 7 is fixed at origin (0,0).");
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

  // Calculate the pH value using the corrected calibration equation
  ph_act = 7 + (slope * (volt - calibration_voltage));

  // Print the pH value every second
  unsigned long currentTime = millis();
  if (currentTime - lastDisplayTime >= displayInterval) {
    lastDisplayTime = currentTime;

    // Print the pH value to the Serial Monitor
    Serial.print("Voltage: ");
    Serial.print(volt, 3); // Voltage with 3 decimal places
    Serial.print(" V    pH Value: ");
    Serial.println(ph_act, 2); // pH with 2 decimal places
  }

  // Check for Serial input to adjust calibration
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n'); // Read user input
    input.trim(); // Remove extra spaces or newlines
    processCommand(input); // Process the input command
  }
}

void processCommand(String input) {
  // Process "set slope <value>" command
  if (input.startsWith("set slope ")) {
    float newSlope = input.substring(10).toFloat();
    slope = newSlope;
    Serial.print("Slope updated to: ");
    Serial.println(slope, 5); // Print slope with 5 decimal places
  } 
  else {
    Serial.println("Invalid command. Use 'set slope <value>'.");
  }
}
