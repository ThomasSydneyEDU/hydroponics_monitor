#include <LiquidCrystal.h>

// Initialize the LCD
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

// Constants for data ranges
const float waterLevelMin = 0.0, waterLevelMax = 1.0; // meters
const float waterTempMin = 20.0, waterTempMax = 30.0; // Celsius
const float ecMin = 0.5, ecMax = 2.5;                 // mS/cm
const float tdsMin = 0.0, tdsMax = 500.0;             // ppm
const float phMin = 5.5, phMax = 7.5;                 // pH

// Current simulated values
float currentWaterLevel = 0.5;
float currentWaterTemp = 25.0;
float currentEC = 1.5;
float currentTDS = 250.0;
float currentPH = 6.5;

// Sampling intervals
const unsigned long samplingInterval = 1000; // 1 second
unsigned long lastSampleTime = 0;
unsigned long lastDisplayUpdateTime = 0;

// Display variables
const int displayInterval = 2000; // 2 seconds per measurement
int currentMeasurement = 0;

void setup() {
  // Initialize LCD
  lcd.begin(16, 2);
  lcd.print("Initializing...");
  delay(2000);
  
  // Initialize Serial for data streaming
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
  // Simulate random fluctuations within ranges
  currentWaterLevel += randomFloat(-0.02, 0.02); // Small variation
  currentWaterTemp += randomFloat(-0.3, 0.3);
  currentEC += randomFloat(-0.05, 0.05);
  currentTDS += randomFloat(-10, 10);
  currentPH += randomFloat(-0.1, 0.1);

  // Clip values to stay within valid ranges
  currentWaterLevel = constrain(currentWaterLevel, waterLevelMin, waterLevelMax);
  currentWaterTemp = constrain(currentWaterTemp, waterTempMin, waterTempMax);
  currentEC = constrain(currentEC, ecMin, ecMax);
  currentTDS = constrain(currentTDS, tdsMin, tdsMax);
  currentPH = constrain(currentPH, phMin, phMax);

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
  
  // Display each measurement in turn
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

  // Scroll to the next measurement
  currentMeasurement = (currentMeasurement + 1) % 5;
}

float randomFloat(float min, float max) {
  return min + ((float)rand() / RAND_MAX) * (max - min);
}