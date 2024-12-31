#include "DFRobot_EC.h"
#include <EEPROM.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// EC Sensor Pin
#define EC_PIN A1

// DS18B20 Sensor Pin
#define ONE_WIRE_BUS 2

// OneWire and DallasTemperature setup
OneWire oneWire(ONE_WIRE_BUS);	
DallasTemperature sensors(&oneWire);

// Variables for EC and temperature
float voltage, ecValue, temperature = 25.0;
DFRobot_EC ec;

void setup()
{
  // Initialize Serial Communication
  Serial.begin(115200);

  // Initialize DS18B20 Temperature Sensor
  sensors.begin();

  // Initialize EC Sensor
  ec.begin();

  Serial.println("EC Sensor with Temperature Compensation Ready");
}

void loop()
{
  static unsigned long timepoint = millis();
  if (millis() - timepoint > 1000U)  // Time interval: 1s
  {
    timepoint = millis();

    // Read voltage from EC sensor
    voltage = analogRead(EC_PIN) / 1024.0 * 5000;

    // Read temperature from DS18B20
    temperature = readTemperature();

    // Convert voltage to EC with temperature compensation
    ecValue = ec.readEC(voltage, temperature);

    // Print results to Serial Monitor
    Serial.print("Temperature: ");
    Serial.print(temperature, 1);
    Serial.print(" °C  |  EC: ");
    Serial.print(ecValue, 2);
    Serial.println(" ms/cm");
  }

  // Calibration process via Serial Commands
  ec.calibration(voltage, temperature);
}

float readTemperature()
{
  // Request temperature readings from DS18B20
  sensors.requestTemperatures();
  
  // Return temperature in Celsius
  return sensors.getTempCByIndex(0);
}
