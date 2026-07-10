#include <Servo.h>
#include "HX711.h"
#include <Wire.h>
#include <INA226_WE.h>

#define I2C_ADDRESS 0x40

INA226_WE ina226 = INA226_WE(I2C_ADDRESS);

Servo myESC;  // Create a servo object to control the ESC
HX711 scale;  // Create a scale object

// Values to calculate power draw
const float supplyVoltage = 12;

const int escPin = 13;

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;

void setup() {
  Serial.begin(9600);

  // Wait up to 2 seconds for a configuration signal from Python
  unsigned long startTime = millis();
  while (millis() - startTime < 2000) { 
    if (Serial.available() > 0) {
      char incomingByte = Serial.read();
      if (incomingByte == 'Q') {
        quietMode = true;
        break; // Exit the loop early since we got our signal
      }
    }
  }

  myESC.attach(escPin);

  if (!quietMode) {
    Serial.println("\n--- Starting ESC Calibration ---");

    // 1. Send HIGH throttle signal
    Serial.println("1. Sending High Throttle (2000ms)...");
    myESC.writeMicroseconds(2000);

    // 2. NOW plug in the 12V power supply while this message prints!
    Serial.println("--> NOW TURN ON/PLUG IN 12V POWER SUPPLY");
    Serial.println("Waiting 5 seconds for the ESC to register high throttle...");
    delay(5000);  // It should make a couple of short beeps here

    // 3. Send LOW throttle signal to lock it in
    Serial.println("2. Sending Low Throttle (1000ms) to Arm...");
    myESC.writeMicroseconds(1000);

    Serial.println("Waiting 5 seconds for final arming tones...");
    delay(5000);  // It should make a long, happy confirmation tone

    Serial.println("--- Calibration complete ---");
  }

  Wire.begin();

  if (!ina226.init()) {
    Serial.println("Failed to find INA226 chip!");
    while (1)
      ;
  }

  // calibrate for the 0.002 ohm resistor
  ina226.setResistorRange(0.002, 20.0);
  ina226.waitUntilConversionCompleted();
}

void loop() {

  // Check if text has been typed into the Serial Monitor
  if (Serial.available() > 0) {
    // Read the incoming line of text until a newline character
    String inputString = Serial.readStringUntil('\n');
    inputString.trim();  // Remove any accidental spaces or hidden characters

    // Convert string to lowercase so commands aren't case-sensitive
    inputString.toLowerCase();

    // --- COMMAND DESERIALIZATION ---

    // 1. COMMAND: STOP
    if (inputString == "st") {
      myESC.writeMicroseconds(1000);
      Serial.println("--> STOP: Motor Disabled (1000ms)");
    }

    // 2. COMMAND: SPEED [VALUE]
    else if (inputString.startsWith("speed ")) {
      // Extract the number part after the word "speed "
      String valueString = inputString.substring(6);
      int speedValue = valueString.toInt();

      // Bench Safety Caps
      if (speedValue < 1000) speedValue = 1000;
      if (speedValue > 1300) {
        Serial.println("--> Warning: Speed capped at 1300 for bench safety!");
        speedValue = 1300;
      }

      myESC.writeMicroseconds(speedValue);
      Serial.println("--> Motor Speed Set To: ");
      Serial.println(speedValue);
    }

    // TEST COMMANDS
    else if (inputString.startsWith("test ")) {
      // Extract the command after test
      String valueString = inputString.substring(5);

      if (valueString == "sweep") {

        // Start the test
        if (!quietMode) {
          Serial.println("=== Test Running... ===");
        }

        scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
        scale.set_scale(393);
        scale.tare();

        // Loop UP
        for (int speed = 1050; speed <= 1818; speed += 12) {

          // Check for emergency mid-sweep stop command
          if (Serial.available() > 0) {
            String emergency = Serial.readStringUntil('\n');
            if (emergency.indexOf("st") >= 0) {
              break;
            }
          }
          myESC.writeMicroseconds(speed);

          delay(400);

          float reading = scale.get_units(40);  // Average of 40 readings

          // 1. Define how many samples you want to average (e.g., 40 samples)
          int numSamples = 40;

          float totalCurrent = 0.0;
          float totalVoltage = 0.0;
          float totalPower = 0.0;

          // 2. Collect the samples
          for (int i = 0; i < numSamples; i++) {
            totalCurrent += ina226.getCurrent_mA();
            totalVoltage += ina226.getBusVoltage_V();

            // Using getBusPower() / 1000.0 directly from the chip gives you the most accurate power calculation
            totalPower += (ina226.getBusPower() / 1000.0);

            delay(10);  // Tiny delay between samples to let the sensor refresh
          }

          // 3. Calculate the averages
          float averageCurrent_mA = totalCurrent / numSamples;
          float averageVoltage_V = totalVoltage / numSamples;
          float averagePower_W = totalPower / numSamples;

          // 4. (Optional) Convert mA to Amps for your final printout
          float averageCurrent_A = averageCurrent_mA / 1000.0;

          // 3. Print Results
          Serial.print("\n");
          Serial.print(speed);
          Serial.print(",");
          Serial.print(averagePower_W);
          Serial.print(",");
          Serial.print(reading);
          Serial.print(",");
          Serial.print(averageCurrent_A);
          Serial.print(",");
          Serial.print(averageVoltage_V);
        }

        // End the test
        myESC.writeMicroseconds(1000);

        if (!quietMode) {
          Serial.println("=== Test Complete ===");
        }

      } else if (valueString == "load") {

        // Initialize library with data and clock pins
        scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

        Serial.println("Before setting up the scale:");
        Serial.print("read: \t\t");
        Serial.println(scale.read());  // print a raw reading from the ADC

        Serial.print("read average: \t\t");
        Serial.println(scale.read_average(20));  // print the average of 20 readings from the ADC

        // This tares the scale (sets the current weight as the 0 reference point)
        // Make sure there is nothing on the scale during startup!
        scale.set_scale(393);
        scale.tare();

        Serial.println("After setting up the scale:");
        Serial.print("read: \t\t");
        Serial.println(scale.read());  // should be close to 0

        Serial.print("read average: \t\t");
        Serial.println(scale.read_average(20));  // should be close to 0

        Serial.println("Scale is ready. Place a known weight on it to see the raw values change...");

        while (true) {
          if (scale.is_ready()) {
            long reading = scale.get_units(10);  // Average of 10 readings
            Serial.print("Raw Value (Average of 10): ");
            Serial.println(reading);
          } else {
            Serial.println("HX711 not found. Check your wiring!");
          }
          delay(1000);
        }
      }
    }  // <--- THIS BRACE WAS MISSING! It closes the "test " command block.

    // 3. COMMAND: HELP / INFO
    else if (inputString == "help" || inputString == "?") {
      printHelp();
    }

    // 4. INVALID COMMAND HANDLER
    else if (inputString.length() > 0) {
      Serial.print("Unknown Command: '");
      Serial.print(inputString);
      Serial.println("'. Type 'help' to see available commands.");
    }
  }
}  // Closes void loop()

// Handy function to print the command menu sits cleanly outside now
void printHelp() {
  Serial.println("\n=== Available Test Bench Commands ===");
  Serial.println("  speed XXXX  - Set speed between 1000 and 1300 (e.g., 'speed 1080')");
  Serial.println("  test sweep  - Run the automated sweep test");
  Serial.println("  st          - Instantly cut power to the motor");
  Serial.println("=======================================\n");
}