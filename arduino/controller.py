#!/usr/bin/env python

import serial.serialutil
import time

from nanpy import ArduinoApi
from nanpy import SerialManager
import nanpy.serialmanager

from arduino.led_blinker import LedBlinker
from arduino.led_fader import LedFader

# indicator led pin
LED_PIN = 9

# individual pins
PIN_READ_QR = 2
PIN_PLAY = 4
PIN_STOP = 7
PIN_PREV = 8
PIN_NEXT = 12

# array of all the pins
BUTTON_PINS = [PIN_READ_QR, PIN_PLAY, PIN_STOP, PIN_NEXT, PIN_PREV]

# debounce threshold in milliseconds
DEBOUNCE = 25

# events
E_READ_QR = 'read_qr'
E_PLAY = 'play'
E_STOP = 'stop'
E_NEXT = 'next'
E_PREV = 'prev'
EVENTS = [E_READ_QR, E_PLAY, E_STOP, E_NEXT, E_PREV]


class ArduinoController(object):
  callbacks = []

  def __init__(self):
    self.connection = SerialManager()
    self.a = ArduinoApi(connection=self.connection)
    self.timestamps = {pin: None for pin in BUTTON_PINS}
    self.last_led_change = self._millis()

    self.set_led_fading()

  def setup(self):
    self.a.pinMode(LED_PIN, self.a.OUTPUT)
    for pin in BUTTON_PINS:
      self.a.pinMode(pin, self.a.INPUT)

  def subscribe(self, type, fn_callback):
    self.callbacks.append({'type': type, 'fn_callback': fn_callback})

  def loop(self):
    for pin in BUTTON_PINS:

      if self.a.digitalRead(pin) == self.a.HIGH:
        if self.timestamps[pin] is None:
          self._keypress(pin)
        self.timestamps[pin] = self._millis()

      else:
        if self.timestamps[pin] is not None:
          if self.timestamps[pin] + DEBOUNCE < self._millis():
            self._keyup(pin)
            self.timestamps[pin] = None

      if self.timestamps[pin] is not None:
        self._keydown(pin)

    self._led_frame()

  def set_led_controller(self, led_controller):
    self.led_controller = led_controller

  def set_led_blinking(self):
    self.set_led_controller(LedBlinker(freq=10))

  def set_led_fading(self):
    self.set_led_controller(LedFader(freq=0.25))

  def darken_led(self):
    self.set_led_controller(None)

  def _keypress(self, pin):
    print('fire_keypress {}'.format(pin))
    self._fire(self._get_event_for_pin(pin), pin=pin)

  def _keydown(self, pin):
    # print('fire_keydown {}'.format(pin))
    pass

  def _keyup(self, pin):
    print('fire_keyup {}'.format(pin))

  def _get_event_for_pin(self, pin):
    return {
      PIN_READ_QR: E_READ_QR,
      PIN_PLAY: E_PLAY,
      PIN_STOP: E_STOP,
      PIN_NEXT: E_NEXT,
      PIN_PREV: E_PREV
    }[pin]

  def _fire(self, type, **attrs):
    for cb in self.callbacks:
      if cb['type'] == type:
        cb['fn_callback'](type=type, **attrs)

  def _millis(self):
    return int(time.time() * 1000)

  def _led_frame(self):
    if self.led_controller is None:
      self.a.analogWrite(LED_PIN, 0)
    else:
      brightness = self.led_controller.frame(self._millis())
      self.a.analogWrite(LED_PIN, brightness)


def observert(type, pin=None):
  print('observer={} pin={}'.format(type, pin))

if __name__ == '__main__':
  while True:
    try:
      c = ArduinoController()

      for e in EVENTS:
        c.subscribe(e, observert)

      c.setup()
      while True:
        c.loop()

    except serial.serialutil.SerialException as e:
      print(e)
      time.sleep(1)

    except nanpy.serialmanager.SerialManagerError as e:
      print(e)
      time.sleep(1)
