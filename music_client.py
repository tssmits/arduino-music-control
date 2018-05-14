#!/usr/bin/env python

import signal
import time
import subprocess
import os
import threading
import zmq

from music.musiclib import get_item_for_qr_code, all_music_files_in_directory
import driver

zmq_context = zmq.Context.instance()

zmq_button_sub = zmq_context.socket(zmq.SUB)
zmq_button_sub.connect('tcp://127.0.0.1:5555')
zmq_button_sub.setsockopt(zmq.SUBSCRIBE, b'')

zmq_command_req = zmq_context.socket(zmq.REQ)
zmq_command_req.connect('tcp://127.0.0.1:5556')

# max shots in ./shots/ dir
MAX_SAVED_SHOTS = 25

# retry on no qr found?
QR_MAX_RETRIES = 3

shots_counter = 1
def look_for_qr():
  global shots_counter
  retries = QR_MAX_RETRIES
  while retries > 0:
    filename = "shots/photo{:08d}.jpg".format(shots_counter)

    remove_if_exists(filename)

    # Make sure we never run out of diskspace and reset
    # file counter when we've reached our preconfigured max.
    shots_counter = (shots_counter+1, 1)[shots_counter < MAX_SAVED_SHOTS]

    # Capture webcam image and write to filename
    capture_webcam_image(filename)

    # ascii art! (i have too much time...)
    ascii_art(filename)

    qr = parse_qr_from_image(filename)
    if qr:
      return qr

    retries = retries - 1

  # nothing found
  return None


def remove_if_exists(filename):
  try:
    os.remove(filename)
  except OSError:
    pass

def capture_webcam_image(filename):
  subprocess.check_output(["fswebcam", "-r", "1280x720", filename])

def ascii_art(filename):
  try:
    # get something between 10 and term_height
    term_height = int(subprocess.check_output(["tput", "lines"]))
    height = min(term_height, max(10, term_height - 10))
    # draw ascii art
    subprocess.call(['jp2a', '--height={}'.format(height), '--colors', '--fill', filename])
  except subprocess.CalledProcessError as e:
    print(e)

def parse_qr_from_image(filename):
  try:
    return subprocess.check_output(['zbarimg', filename]).strip().decode()
  except subprocess.CalledProcessError as e:
    print("no qr code embedded")


def start_the_good_music(msg_from_qrcode):
  print("we a qr code! {}".format(msg_from_qrcode))

  print("do we have music?")

  item = get_item_for_qr_code(msg_from_qrcode)
  if item:
    print("yes! it's:")
    print(item['uri'])
    play_item(item)
    return True
  else:
    print("sadly, no... try again!")
    return False

def stop_all():
  run_command(["mpc", '-q', 'stop'])

def play_item(item):
  if item['type'] == 'file':
    stop_all()
    play_dir(item['uri'])
  elif item['type'] == 'spotify':
    stop_all()
    play_spotify(item['uri'])

def play_dir(uri):
  run_command(["mpc", '-q', 'stop'])
  run_command(["mpc", '-q', 'clear'])
  run_command(["mpc", '-q', 'volume', '80'])
  for filename in all_music_files_in_directory(uri):
    run_command(["mpc", '-q', 'add', 'file:{}'.format(filename)])
  run_command(["mpc", '-q', 'play'])
  time.sleep(0.1)
  run_command(["mpc", 'status'])

def play_spotify(uri):
  run_command(["mpc", '-q', 'stop'])
  run_command(["mpc", '-q', 'clear'])
  run_command(["mpc", '-q', 'volume', '80'])
  run_command(["mpc", '-q', 'add', uri])
  run_command(["mpc", '-q', 'play'])
  time.sleep(0.1)
  run_command(["mpc", 'status'])

def btn_play():
  run_command(['mpc', '-q', 'play'])
  time.sleep(0.1)
  run_command(["mpc", 'status'])

def btn_pause():
  run_command(['mpc', '-q', 'toggle'])
  time.sleep(0.1)
  run_command(["mpc", 'status'])

def btn_stop():
  run_command(['mpc', '-q', 'stop'])
  time.sleep(0.1)
  run_command(["mpc", 'status'])

def btn_next():
  run_command(['mpc', '-q', 'next'])
  time.sleep(0.1)
  run_command(["mpc", 'status'])

def btn_prev():
  run_command(['mpc', '-q', 'prev'])
  time.sleep(0.1)
  run_command(["mpc", 'status'])

def read_qr():
  led_fade()
  qr = look_for_qr()
  if qr:
    led_off()
    start_the_good_music(qr)
  else:
    led_blink_three_times()

def run_command(cmd):
  try:
    subprocess.call(cmd)
  except subprocess.CalledProcessError as e:
    print(e)

def led_on():
  zmq_command_req.send(b'led_on')
  return zmq_command_req.recv()

def led_off():
  zmq_command_req.send(b'led_off')
  return zmq_command_req.recv()

def led_blink_three_times():
  zmq_command_req.send(b'led_blink=3')
  return zmq_command_req.recv()

def led_fade():
  zmq_command_req.send(b'led_fade')
  return zmq_command_req.recv()

def button_thread():
  while True:
    evt = zmq_button_sub.recv()

    if evt == driver.EVT_PLAY:
      btn_pause()
    elif evt == driver.EVT_STOP:
      btn_stop()
    elif evt == driver.EVT_PREV:
      btn_prev()
    elif evt == driver.EVT_NEXT:
      btn_next()
    elif evt == driver.EVT_READ_QR:
      read_qr()

def print_help():
  print("Commands: ")
  for item in ['play', 'pause', 'next', 'prev', 'ls', 'read_qr', 'help']:
    print("\t{}".format(item))
  print("Quit by pressing Ctrl-C (twice if running from ./client.sh)")

def user_input_thread():
  while True:
    cmd = input('cmd: ').strip()

    if 'QR-Code:' == cmd[:8]:
      start_the_good_music(cmd)
    elif 'read_qr' == cmd:
      read_qr()
    elif 'next' == cmd:
      btn_next()
    elif 'prev' == cmd:
      btn_prev()
    elif 'stop' == cmd:
      btn_stop()
    elif 'pause' == cmd:
      btn_pause()
    elif 'play' == cmd:
      btn_play()
    elif 'ls' == cmd:
      run_command(['mpc', 'playlist'])
    elif 'help' == cmd:
      print_help()
    else:
      print("Unknown command: {}".format(cmd))
      print_help()

bt = threading.Thread(target=button_thread, daemon=True)
bt.start()

uit = threading.Thread(target=user_input_thread, daemon=True)
uit.start()

def run():
  print("OK make shots!")
  led_fade()
  while True:
    for t in [bt, uit]:
      t.join(0.1)
      if not t.isAlive():
        exit(1)

if __name__ == '__main__':
  run()
