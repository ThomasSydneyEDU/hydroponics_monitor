// Constants for data ranges
const float waterLevelMin = 0.0, waterLevelMax = 1.0; // meters
const float waterTempMin = 20.0, waterTempMax = 30.0; // Celsius
const float ecMin = 0.5, ecMax = 2.5;                 // mS/cm
const float tdsMin = 0.0, tdsMax = 500.0;             // ppm
const float phMin = 5.5, phMax = 8.0;                 // pH

// Current simulated values
float currentWaterLevel = 0.5;
float currentWaterTemp = 25.0;
float currentEC = 1.5;
float currentTDS = 250.0;
float currentPH = 6.5;

// Sampling intervals
const unsigned long samplingInterval = 1000; // 1 second
unsigned long lastSampleTime = 0;

void setup() {
  // Initialize Serial for data streaming
  Serial.begin(9600);
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

float randomFloat(float min, float max) {
  return min + ((float)rand() / RAND_MAX) * (max - min);
}
