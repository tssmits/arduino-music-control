#!/usr/bin/env python

import time
from nanpy import ArduinoApi
from nanpy import SerialManager

from common import a


a.pinMode(13, a.OUTPUT)

while True:
    a.digitalWrite(13, a.HIGH)
    time.sleep(1)
    a.digitalWrite(13, a.LOW)
    time.sleep(1)
