#!/usr/bin/env python

import sys
import threading
import zmq
import time

zmq_context = zmq.Context()

zmq_button_sub = zmq_context.socket(zmq.SUB)
zmq_button_sub.connect('tcp://127.0.0.1:5555')
zmq_button_sub.setsockopt(zmq.SUBSCRIBE, b'')

zmq_command_req = zmq_context.socket(zmq.REQ)
zmq_command_req.connect('tcp://127.0.0.1:5556')

def button_thread():
  while True:
    logger.info(zmq_button_sub.recv())

def command_thread():
  global running
  while True:
    # get user input and strip the newline
    cmd_orig = input('cmd: ').strip()

    # strip the newline and encode to binary blob
    cmd = cmd_orig.encode()

    # send command if we know it.
    if cmd in [b'led_on', b'led_off', b'led_fade', b'led_blink', b'led_blink_once']:
      zmq_command_req.send(cmd)
      reply = zmq_command_req.recv()
      logger.info('Reply: {}'.format(reply))
    elif cmd in [b'exit', b'quit']:
      running = False
    else:
      logger.info('Unknown command: {}'.format(cmd_orig))
      logger.info('Use led_on, led_off, led_fade, led_blink or led_blink_once')

bt = threading.Thread(target=button_thread, daemon=True)
bt.start()

ct = threading.Thread(target=command_thread, daemon=True)
ct.start()

running = True
while running:
  pass

logger.info("\nDone")
