#!/usr/bin/env python

import serial.serialutil
import time

from nanpy import ArduinoApi
from nanpy import SerialManager
import nanpy.serialmanager

from led_blinker import LedBlinker
from led_fader import LedFader

from music_arduino import BUTTON_PINS, LED_PIN

# debounce threshold in milliseconds
DEBOUNCE = 25


class ArduinoController(object):
  callbacks = []
  keydown_timestamps = {pin: None for pin in BUTTON_PINS}
  keypress_timestamps = {pin: None for pin in BUTTON_PINS}

  def __init__(self, button_pins=[], led_pin=None, debounce=DEBOUNCE):
    self.button_pins = button_pins
    self.led_pin = led_pin
    self.debounce = debounce

  def connect(self):
    self.connection = SerialManager('/dev/tty.usbmodem1411')
    self.a = ArduinoApi(connection=self.connection)

  def setup(self):
    if self.led_pin is not None:
      self.a.pinMode(LED_PIN, self.a.OUTPUT)

    for pin in self.button_pins:
      self.a.pinMode(pin, self.a.INPUT)

  def subscribe(self, type, fn_callback):
    self.callbacks.append({'type': type, 'fn_callback': fn_callback})

  def loop(self):
    for pin in self.button_pins:

      millis = self._millis()

      if self.a.digitalRead(pin) == self.a.HIGH:
        if self.keydown_timestamps[pin] is None:
          self._keypress(pin)
          self.keypress_timestamps[pin] = millis
        self.keydown_timestamps[pin] = millis

      else:
        if self.keydown_timestamps[pin] is not None:
          if self.keydown_timestamps[pin] + self.debounce < millis:
            self._keyup(pin)
            self.keypress_timestamps[pin] = None
            self.keydown_timestamps[pin] = None

      if self.keydown_timestamps[pin] is not None:
        already = millis - self.keypress_timestamps[pin]
        self._keydown(pin, already=already)

    self._led_frame()

  def set_led_controller(self, led_controller):
    self.led_controller = led_controller

  def set_led_blinking(self):
    self.set_led_controller(LedBlinker(freq=10))

  def set_led_fading(self):
    self.set_led_controller(LedFader(freq=1))

  def darken_led(self):
    self.set_led_controller(None)

  def _keypress(self, pin):
    self._fire('keypress', pin=pin)

  def _keydown(self, pin, already):
    self._fire('keydown', pin=pin, already=already)

  def _keyup(self, pin):
    self._fire('keyup', pin=pin)

  def _fire(self, type, **attrs):
    for cb in self.callbacks:
      if cb['type'] == type:
        cb['fn_callback'](type=type, **attrs)

  def _millis(self):
    return int(time.time() * 1000)

  def _led_frame(self):
    if self.led_pin is None:
      return

    if self.led_controller is None:
      self.a.analogWrite(LED_PIN, 0)
    else:
      brightness = self.led_controller.frame(self._millis())
      self.a.analogWrite(LED_PIN, brightness)


def observert(type, pin=None, already=None):
  print('observer={} pin={} already={}'.format(type, pin, already))

if __name__ == '__main__':
  c = None
  while True:
    try:
      if c is None:
        c = ArduinoController(button_pins=BUTTON_PINS, led_pin=LED_PIN)
        c.set_led_fading()
        c.subscribe('keypress', observert)
        c.subscribe('keydown', observert)
        c.subscribe('keyup', observert)

      c.connect()
      c.setup()

      while True:
        c.loop()

    except serial.serialutil.SerialException as e:
      print(e)
      time.sleep(1)

    except nanpy.serialmanager.SerialManagerError as e:
      print(e)
      time.sleep(1)
