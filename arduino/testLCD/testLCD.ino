#include <LiquidCrystal.h>

// Initialize the library with the numbers of the interface pins
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

void setup() {
  // Set up the LCD's number of columns and rows
  lcd.begin(16, 2);
  lcd.print("Hello, Arduino!");
}

void loop() {
  // Do nothing for now
}