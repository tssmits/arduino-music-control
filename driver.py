#!./venv/bin/python

import threading
import time
import zmq
import serial.serialutil

import arduino.controller
import nanpy.serialmanager


LED_PIN = 9
PIN_READ_QR = 2
PIN_PLAY = 4
PIN_STOP = 7
PIN_PREV = 8
PIN_NEXT = 12

EVT_READ_QR = b'read_qr'
EVT_PLAY = b'play'
EVT_STOP = b'stop'
EVT_PREV = b'prev'
EVT_NEXT = b'next'

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
      print('Unknown event: {}'.format(evt_raw))

def command_thread():
  global zmq_context

  zmq_arduino_command_req = zmq_context.socket(zmq.REQ)
  zmq_arduino_command_req.connect('inproc://arduino/commands_rep')

  zmq_driver_command_rep = zmq_context.socket(zmq.REP)
  zmq_driver_command_rep.bind('tcp://*:5556')

  while True:
    cmd = zmq_driver_command_rep.recv()
    zmq_arduino_command_req.send(cmd)
    reply = zmq_arduino_command_req.recv()
    zmq_driver_command_rep.send(reply)

zmq_context = zmq.Context.instance()

bt = threading.Thread(target=button_thread, daemon=True)
bt.start()

ct = threading.Thread(target=command_thread, daemon=True)
ct.start()

c = arduino.controller.ArduinoController(led_pin=LED_PIN,
  button_pins=[PIN_READ_QR, PIN_PLAY, PIN_STOP, PIN_NEXT, PIN_PREV])

running = True
while running:
  try:
    c.connect()
    c.setup()

    print("Ready!")
    while True:
      c.loop()

  except serial.serialutil.SerialException as e:
    print(e)
    time.sleep(1)

  except nanpy.serialmanager.SerialManagerError as e:
    print(e)
    time.sleep(1)
