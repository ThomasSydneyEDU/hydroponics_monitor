#include <LiquidCrystal.h>

// Initialize the LCD
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

// Constants for data ranges
const float waterLevelMin = 0.0, waterLevelMax = 1.0; // meters
const float waterTempMin = 20.0, waterTempMax = 30.0; // Celsius
const float ecMin = 0.5, ecMax = 2.5;                 // mS/cm
const float tdsMin = 0.0, tdsMax = 500.0;             // ppm
const float phMin = 5.5, phMax = 7.5;                 // pH

// Sampling intervals
const unsigned long samplingInterval = 5000; // 5 seconds
unsigned long lastSampleTime = 0;
unsigned long lastDisplayUpdateTime = 0;

// Circular buffers for data
const int bufferSize = 12; // Store up to 12 samples (60 seconds)
float waterLevelBuffer[bufferSize];
float waterTempBuffer[bufferSize];
float ecBuffer[bufferSize];
float tdsBuffer[bufferSize];
float phBuffer[bufferSize];
int bufferIndex = 0;
int sampleCount = 0;

// Display variables
const int displayInterval = 2000; // 2 seconds per measurement
int currentMeasurement = 0;

void setup() {
  // Initialize LCD
  lcd.begin(16, 2);
  lcd.print("Simulating...");
  delay(2000);
  
  // Initialize buffers
  for (int i = 0; i < bufferSize; i++) {
    waterLevelBuffer[i] = 0;
    waterTempBuffer[i] = 0;
    ecBuffer[i] = 0;
    tdsBuffer[i] = 0;
    phBuffer[i] = 0;
  }
  
  lcd.clear();
}

void loop() {
  unsigned long currentTime = millis();
  
  // Sample data every 5 seconds
  if (currentTime - lastSampleTime >= samplingInterval) {
    lastSampleTime = currentTime;
    sampleData();
  }

  // Update LCD display every 2 seconds
  if (currentTime - lastDisplayUpdateTime >= displayInterval) {
    lastDisplayUpdateTime = currentTime;
    updateDisplay();
  }
}

void sampleData() {
  // Simulate random values within typical ranges
  float waterLevel = randomFloat(waterLevelMin, waterLevelMax);
  float waterTemp = randomFloat(waterTempMin, waterTempMax);
  float ec = randomFloat(ecMin, ecMax);
  float tds = randomFloat(tdsMin, tdsMax);
  float ph = randomFloat(phMin, phMax);
  
  // Store data in circular buffers
  waterLevelBuffer[bufferIndex] = waterLevel;
  waterTempBuffer[bufferIndex] = waterTemp;
  ecBuffer[bufferIndex] = ec;
  tdsBuffer[bufferIndex] = tds;
  phBuffer[bufferIndex] = ph;
  
  // Update buffer index and sample count
  bufferIndex = (bufferIndex + 1) % bufferSize;
  if (sampleCount < bufferSize) {
    sampleCount++;
  }
}

float calculateMean(float buffer[], int count) {
  float sum = 0;
  for (int i = 0; i < count; i++) {
    sum += buffer[i];
  }
  return sum / count;
}

void updateDisplay() {
  lcd.clear();
  float meanValue;
  
  // Display each measurement in turn
  switch (currentMeasurement) {
    case 0:
      meanValue = calculateMean(waterLevelBuffer, sampleCount);
      lcd.print("Water Level:");
      lcd.setCursor(0, 1);
      lcd.print(meanValue, 2);
      lcd.print(" m");
      break;
    case 1:
      meanValue = calculateMean(waterTempBuffer, sampleCount);
      lcd.print("Water Temp:");
      lcd.setCursor(0, 1);
      lcd.print(meanValue, 1);
      lcd.print(" C");
      break;
    case 2:
      meanValue = calculateMean(ecBuffer, sampleCount);
      lcd.print("EC:");
      lcd.setCursor(0, 1);
      lcd.print(meanValue, 2);
      lcd.print(" mS/cm");
      break;
    case 3:
      meanValue = calculateMean(tdsBuffer, sampleCount);
      lcd.print("TDS:");
      lcd.setCursor(0, 1);
      lcd.print(meanValue, 1);
      lcd.print(" ppm");
      break;
    case 4:
      meanValue = calculateMean(phBuffer, sampleCount);
      lcd.print("pH:");
      lcd.setCursor(0, 1);
      lcd.print(meanValue, 1);
      break;
  }

  // Scroll to the next measurement
  currentMeasurement = (currentMeasurement + 1) % 5;
}

float randomFloat(float min, float max) {
  return min + ((float)rand() / RAND_MAX) * (max - min);
}