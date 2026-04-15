#include <AccelStepper.h>
#include "HX711.h"

// pin assignments
#define STEP_PIN 3
#define DIR_PIN 4
#define DOUT 6
#define CLK 7

HX711 scale;
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

long position = 0;
int direction = 1;

unsigned long settleTime = 200;

// setup
void setup() {
  Serial.begin(115200);

  stepper.setMaxSpeed(2000);
  stepper.setAcceleration(1500);

  scale.begin(DOUT, CLK);
  scale.tare();

  Serial.println("READY");
}

// main loop
void loop() {

  stepper.run();

  if (Serial.available()) {

    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("D")) {

      direction = cmd.substring(1).toInt();

      Serial.print("DIR ");
      Serial.println(direction);
    }

    else if (cmd.startsWith("W")) {

      settleTime = cmd.substring(1).toInt();

      Serial.print("SETTLE ");
      Serial.println(settleTime);
    }

    else if (cmd == "S") {

      if (direction == 1) position += 1;
      else position -= 1;

      stepper.moveTo(position);

      while (stepper.distanceToGo() != 0) {
        stepper.run();
      }

      Serial.println("STEPPED");
    }

    else if (cmd == "SR") {

      if (direction == 1) position += 1;
      else position -= 1;

      stepper.moveTo(position);

      while (stepper.distanceToGo() != 0) {
        stepper.run();
      }

      delay(settleTime);

      long reading = scale.read();


      Serial.print(position);
      Serial.print(",");
      Serial.println(reading);
    }

    else if (cmd == "R") {

      long reading = scale.read();


      Serial.print(position);
      Serial.print(",");
      Serial.println(reading);
    }

    else if (cmd == "Z") {

      scale.tare();
      Serial.println("ZEROED");
    }
  }
}