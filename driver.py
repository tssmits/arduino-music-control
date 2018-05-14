#!./venv/bin/python

import threading
import time
import zmq
import serial.serialutil

import arduino.controller
import nanpy.serialmanager


# pins
LED_PIN = 9
PIN_READ_QR = 2
PIN_PLAY = 4
PIN_STOP = 7
PIN_PREV = 8
PIN_NEXT = 12

# events
EVT_READ_QR = b'read_qr'
EVT_PLAY = b'play'
EVT_STOP = b'stop'
EVT_PREV = b'prev'
EVT_NEXT = b'next'

# replies
REP_OK = b'ok'
REP_UNKNOWN = b'unknown'


def parse_event(evt_binary):
  evt = evt_binary.decode()
  if evt[:9] == 'keypress=':
    try:
      pin = int(evt[9:])
      return {
        PIN_READ_QR: EVT_READ_QR,
        PIN_PLAY: EVT_PLAY,
        PIN_STOP: EVT_STOP,
        PIN_PREV: EVT_PREV,
        PIN_NEXT: EVT_NEXT
      }[pin]
    except ValueError:
      pass
    except KeyError:
      pass

  return None

def pass_cmd_onto_arduino(c, cmd):
  reply = REP_UNKNOWN

  if cmd == b'led_blink':
    c.set_led_blinking()
    reply = REP_OK
  if cmd == b'led_blink_once':
    c.set_led_blink_once()
    reply = REP_OK
  elif cmd == b'led_fade':
    c.set_led_fading()
    reply = REP_OK
  elif cmd == b'led_on':
    c.set_led_on()
    reply = REP_OK
  elif cmd == b'led_off':
    c.set_led_off()
    reply = REP_OK
  else:
    cmd_str = cmd.decode()
    if cmd_str[:10] == 'led_blink=':
      try:
        countdown = max(1, int(cmd_str[10:]))
        c.set_led_blinking(countdown=countdown)
        reply = REP_OK
      except ValueError:
        pass

  return reply

def button_thread():
  global zmq_context

  zmq_arduino_buttons_pub = zmq_context.socket(zmq.SUB)
  zmq_arduino_buttons_pub.connect('inproc://arduino/buttons_pub')
  zmq_arduino_buttons_pub.setsockopt(zmq.SUBSCRIBE, b'')

  zmq_driver_button_pub = zmq_context.socket(zmq.PUB)
  zmq_driver_button_pub.bind('tcp://*:5555')

  while True:
    evt_raw = zmq_arduino_buttons_pub.recv()
    evt = parse_event(evt_raw)
    if evt:
      zmq_driver_button_pub.send(evt)
      print(evt)
    else:
      print('Not bound to event: {}'.format(evt_raw))

def command_thread(c):
  global zmq_context

  zmq_driver_command_rep = zmq_context.socket(zmq.REP)
  zmq_driver_command_rep.bind('tcp://*:5556')

  while True:
    cmd = zmq_driver_command_rep.recv()
    reply = pass_cmd_onto_arduino(c, cmd)
    zmq_driver_command_rep.send(reply)

def program_thread(c):
  c.connect()
  c.setup()

  print("Ready!")
  while True:
    c.loop()

if __name__ == '__main__':
  c = arduino.controller.ArduinoController(led_pin=LED_PIN, button_pins=[PIN_READ_QR, PIN_PLAY, PIN_STOP, PIN_NEXT, PIN_PREV])

  zmq_context = zmq.Context.instance()

  bt = threading.Thread(target=button_thread, daemon=True)
  bt.start()

  ct = threading.Thread(target=command_thread, daemon=True, args=[c])
  ct.start()

  pt = threading.Thread(target=program_thread, daemon=True, args=[c])
  pt.start()

  while True:
    for t in [bt, ct, pt]:
      t.join(0.1)
      if not t.isAlive():
        exit(1)
