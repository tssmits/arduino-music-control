#!/usr/bin/env python

import signal
import time
import subprocess
import re
import os
import math
from xml.etree import ElementTree
from nanpy import ArduinoApi
from nanpy import SerialManager

from common import a

# "clean" quitting with C-c
def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)


POT_PIN = 2
LED_PIN = 13
value = 0

def setup():
  a.pinMode(LED_PIN, a.OUTPUT)


def loop():
  value = a.analogRead(POT_PIN)
  # print(value)
  better = int(float(value) / 1023 * 100)
  # print(better)

  log = (1-math.pow((float(value) / 1023 - 1), 2.0)) * 255
  print('pot: {} log: {}'.format(better, log))

  subprocess.call(["cmus-remote", '-C', 'vol {}'.format(int(log))])

  time.sleep(0.1)
  # digitalWrite(LED_PIN, HIGH)
  # time.sleep(1)
  # digitalWrite(LED_PIN, LOW)
  # time.sleep(1)


interrupted = False
if __name__ == '__main__':
    setup()
    print("Start potmetering")
    while True:
        loop()

        if interrupted:
          print("Gotta go")
          break
