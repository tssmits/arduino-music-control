#!/usr/bin/env python

import signal
import time
import subprocess
import os
import threading
import zmq

from music.musiclib import get_item_for_qr_code
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

SERVER_CMUS = 'cmus'
SERVER_MPD = 'mpd'
current_server = None

def is_a_server_doing_something_already():
  global current_server


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
  try:
    subprocess.call(["cmus-remote", '-s'])
    subprocess.call(["mpc", 'stop'])
  except subprocess.CalledProcessError as e:
    print(e)

def play_item(item):
  if item['type'] == 'file':
    stop_all()
    play_file(item['uri'])
  elif item['type'] == 'spotify':
    stop_all()
    play_spotify(item['uri'])

def play_file(dirname):
  global current_server
  current_server = SERVER_CMUS

  try:
    # volumo zero
    subprocess.call(["cmus-remote", '-C', 'vol 0'])
    # stop playing if you're playing
    subprocess.call(["cmus-remote", '-p'])
    subprocess.call(["cmus-remote", '-s'])
    # clear all the lists
    subprocess.call(["cmus-remote", '-C', 'clear -l'])
    subprocess.call(["cmus-remote", '-C', 'clear -p'])
    subprocess.call(["cmus-remote", '-C', 'clear -q'])
    # add found album
    # subprocess.call(["cmus-remote", "/media/pi/LACIE/music/Storage2/audio/Pearl Jam - Ten (PBTHAL Vinyl Rip 2011)"])
    subprocess.call(["cmus-remote", dirname])
    # start playing baby
    subprocess.call(["cmus-remote", '-C', 'vol 70%'])
    subprocess.call(["cmus-remote", '-p'])
    subprocess.call(["cmus-remote", '-n'])
    subprocess.call(["cmus-remote", '-p'])

    # Show status
    subprocess.call(["cmus-remote", '-Q'])
  except subprocess.CalledProcessError as e:
    print(e)

def play_spotify(uri):
  global current_server
  current_server = SERVER_MPD

  try:
    subprocess.call(["mpc", 'stop'])
    subprocess.call(["mpc", 'clear'])
    subprocess.call(["mpc", 'volume', '80'])
    subprocess.call(["mpc", 'add', uri])
    subprocess.call(["mpc", 'play'])
  except subprocess.CalledProcessError as e:
    print(e)

def btn_play():
  run_command(cmus=['cmus-remote', '-u'], mpd=['mpc', 'toggle'])

def btn_stop():
  run_command(cmus=['cmus-remote', '-s'], mpd=['mpc', 'stop'])

def btn_next():
  run_command(cmus=['cmus-remote', '-n'], mpd=['mpc', 'next'])

def btn_prev():
  run_command(cmus=['cmus-remote', '-r'], mpd=['mpc', 'prev'])

def run_command(cmus, mpd):
  global current_server
  try:
    if current_server == SERVER_CMUS:
      subprocess.call(cmus)
    elif current_server == SERVER_MPD:
      subprocess.call(mpd)
  except subprocess.CalledProcessError as e:
    print(e)


def exit_if_cmus_is_not_running():
  try:
    return_code = subprocess.call(["cmus-remote", '-Q'])
    if return_code == 0:
      return
  except subprocess.CalledProcessError as e:
    print(e)

  print("cmus (probably) not running, quitting...")
  quit()

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
      btn_play()
    elif evt == driver.EVT_STOP:
      btn_stop()
    elif evt == driver.EVT_PREV:
      btn_prev()
    elif evt == driver.EVT_NEXT:
      btn_next()
    elif evt == driver.EVT_READ_QR:
      led_on()
      qr = look_for_qr()
      if qr:
        led_off()
        start_the_good_music(qr)
      else:
        led_blink_three_times()

def user_input_thread():
  while True:
    cmd = input('cmd: ').strip()

    if 'QR-Code:' == cmd[:8]:
      start_the_good_music(cmd)
    else:
      print("Unknown command: {}".format(cmd))

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
