#!/usr/bin/env python

import time
from subprocess import call
from nanpy import ArduinoApi
from nanpy import SerialManager

from common import a

# constants won't change. They're used here to set pin numbers:
BUTTON_PIN = 2     # the number of the pushbutton pin
LED_PIN    =  13   # the number of the LED pin

# variables will change:
buttonState = 0    # variable for reading the pushbutton status


def setup():
  # initialize the LED pin as an output:
  a.pinMode(LED_PIN, a.OUTPUT)
  # initialize the pushbutton pin as an input:
  a.pinMode(BUTTON_PIN, a.INPUT)


def loop():
  # read the state of the pushbutton value:
  buttonState = a.digitalRead(BUTTON_PIN);

  # check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState == a.HIGH):
    # turn LED on:
    a.digitalWrite(LED_PIN, a.HIGH)
    return_code = call(["ls", "-l"])
    time.sleep(1)
    print(return_code)
  else:
    # turn LED off:
    a.digitalWrite(LED_PIN, a.LOW);


if __name__ == '__main__':
    setup()
    while True:
        loop()
