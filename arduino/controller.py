#!/usr/bin/env python

import logging
import serial.serialutil
import sys
import threading
import time
import zmq

from nanpy import ArduinoApi
from nanpy import SerialManager
import nanpy.serialmanager

from arduino.led_blinker import LedBlinker
from arduino.led_fader import LedFader
from arduino.led_single import LedSingle


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# default debounce threshold in milliseconds
DEFAULT_DEBOUNCE = 25

# default led pin
DEFAULT_LED_PIN = 9

class ArduinoController(object):
  serialManager = None
  led_controller = None

  def __init__(self, zmq_context=None, debounce=DEFAULT_DEBOUNCE, button_pins=[], led_pin=DEFAULT_LED_PIN):
    self.debounce = debounce
    self.button_pins = button_pins
    self.led_pin = led_pin

    self.zmq_context = zmq_context or zmq.Context.instance()

    self.zmq_buttons_pub = self.zmq_context.socket(zmq.PUB)
    self.zmq_buttons_pub.bind("inproc://arduino/buttons_pub")

    self.buttons_timestamps = {pin: None for pin in self.button_pins}

  def connect(self):
    # close old connection if exists
    if self.serialManager:
      self.serialManager.close()

    # make new connection
    self.serialManager = SerialManager()
    self.a = ArduinoApi(connection=self.serialManager)

  def setup(self):
    self.a.pinMode(self.led_pin, self.a.OUTPUT)
    for pin in self.button_pins:
      self.a.pinMode(pin, self.a.INPUT)

  def loop(self):
    for pin in self.button_pins:

      if self.a.digitalRead(pin) == self.a.HIGH:
        if self.buttons_timestamps[pin] is None:
          self._keypress(pin)
        self.buttons_timestamps[pin] = self._get_millis()

      else:
        if self.buttons_timestamps[pin] is not None:
          if self.buttons_timestamps[pin] + self.debounce < self._get_millis():
            self._keyup(pin)
            self.buttons_timestamps[pin] = None

      if self.buttons_timestamps[pin] is not None:
        self._keydown(pin)

    self._led_frame()

  def set_led_controller(self, led_controller):
    self.led_controller = led_controller

  def set_led_blinking(self, countdown=None):
    self.set_led_controller(LedBlinker(freq=10, countdown=countdown))

  def set_led_fading(self):
    self.set_led_controller(LedFader(freq=0.25))

  def set_led_off(self):
    self.set_led_controller(LedSingle(brightness=0))

  def set_led_on(self):
    self.set_led_controller(LedSingle(brightness=255))

  def set_led_blink_once(self):
    self.set_led_controller(LedBlinker(freq=25, countdown=1))

  def _keypress(self, pin):
    evt = 'keypress={}'.format(pin).encode()
    self.zmq_buttons_pub.send(evt)

  def _keydown(self, pin):
    evt = 'keydown={}'.format(pin).encode()
    self.zmq_buttons_pub.send(evt)

  def _keyup(self, pin):
    evt = 'keyup={}'.format(pin).encode()
    self.zmq_buttons_pub.send(evt)

  def _get_millis(self):
    return int(time.time() * 1000)

  def _led_frame(self):
    if self.led_controller is None:
      self.a.analogWrite(self.led_pin, 0)
    else:
      brightness = self.led_controller.frame(self._get_millis())
      self.a.analogWrite(self.led_pin, brightness)
