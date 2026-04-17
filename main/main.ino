#include <AccelStepper.h>
#include "HX711.h"

// ====================setup area====================
#define STEP_PIN 1
#define DIR_PIN 2

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

#define DOUT 18
#define CLK 17

HX711 scale;

long position = 0;
int direction = 1;

unsigned long settleTime = 200;

void setup() {
  Serial.begin(115200);

  stepper.setMaxSpeed(2000);
  stepper.setAcceleration(1500);

  scale.begin(DOUT, CLK);
  scale.tare();

  Serial.println("READY");
}

// ==================end setup area==================
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

    else if (cmd == "Z") {

      scale.tare();
      Serial.println("ZEROED");
    }

    else if (cmd.startsWith("S") && !cmd.startsWith("SR")) {

      int steps = cmd.substring(1).toInt();
      if (steps == 0) steps = 1;

      for (int i = 0; i < steps; i++) {

        if (direction == 1) position += 1;
        else position -= 1;

        stepper.moveTo(position);

        while (stepper.distanceToGo() != 0) {
          stepper.run();
        }
      }

      Serial.println("STEPPED");
    }

    else if (cmd.startsWith("SR")) {

      int steps = cmd.substring(2).toInt();
      if (steps == 0) steps = 1;

      for (int i = 0; i < steps; i++) {

        if (direction == 1) position += 1;
        else position -= 1;

        stepper.moveTo(position);

        while (stepper.distanceToGo() != 0) {
          stepper.run();
        }

        delay(settleTime);

        while (!scale.is_ready());

        long reading = scale.read();

        Serial.print(position);
        Serial.print(",");
        Serial.println(reading);
      }
    }

    else if (cmd.startsWith("R")) {

      int reads = cmd.substring(1).toInt();
      if (reads == 0) reads = 1;

      for (int i = 0; i < reads; i++) {

        while (!scale.is_ready());

        long reading = scale.read();

        Serial.print(position);
        Serial.print(",");
        Serial.println(reading);
      }
    }
  }
}