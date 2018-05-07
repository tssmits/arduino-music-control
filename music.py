#!/usr/bin/env python

import signal
import time
import subprocess
import re
import os
from xml.etree import ElementTree
from nanpy import ArduinoApi
from nanpy import SerialManager

from common import a
from musiclib import get_item_for_qr_code


# constants won't change. They're used here to set pin numbers:
# the number of the pushbutton pin
BUTTON_PIN = 2
# the number of the LED pin
LED_PIN = 13
# max shots in ./shots/ dir
MAX_SAVED_SHOTS = 25

SCAN_ON_FIRST_LOOP = True

BUTTON2_PIN = 4
BUTTON3_PIN = 7
BUTTON4_PIN = 8
BUTTON5_PIN = 12

POT_PIN = 2

# variables will change:
buttonState = 0    # variable for reading the pushbutton status

looking_for_qr = False

counter = 1

pot_value_normalized = 0

SERVER_CMUS = 'cmus'
SERVER_MPD = 'mpd'
current_server = None

def setup():
  # initialize the LED pin as an output:
  a.pinMode(LED_PIN, a.OUTPUT)
  # initialize the pushbutton pin as an input:
  a.pinMode(BUTTON_PIN, a.INPUT)
  # rest of the buttons
  a.pinMode(BUTTON2_PIN, a.INPUT)
  a.pinMode(BUTTON3_PIN, a.INPUT)
  a.pinMode(BUTTON4_PIN, a.INPUT)
  a.pinMode(BUTTON5_PIN, a.INPUT)


is_first_loop = True

def loop():
  global is_first_loop
  global counter
  global pot_value_normalized
  global looking_for_qr

  # read the state of the pushbutton value:
  buttonState = a.digitalRead(BUTTON_PIN)

  # pot_value = a.analogRead(POT_PIN)
  # new_pot_value_normalized = int(float(pot_value) / 1023 * 255)
  #
  # if new_pot_value_normalized != pot_value_normalized:
  #   print("new pot value: {}".format(new_pot_value_normalized))
  #   pot_value_normalized = new_pot_value_normalized
  #   subprocess.call(["cmus-remote", '-C', 'vol {}'.format(pot_value_normalized)])



  if a.digitalRead(BUTTON2_PIN) == a.HIGH:
    print("BUTTON2_PIN high (play)")
    btn_play()
    time.sleep(0.5)
  if a.digitalRead(BUTTON3_PIN) == a.HIGH:
    print("BUTTON3_PIN high (stop)")
    btn_stop()
    time.sleep(0.5)
  if a.digitalRead(BUTTON4_PIN) == a.HIGH:
    print("BUTTON4_PIN high (prev)")
    btn_prev()
    time.sleep(0.5)
  if a.digitalRead(BUTTON5_PIN) == a.HIGH:
    print("BUTTON5_PIN high (next)")
    btn_next()
    time.sleep(0.5)


  # check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState == a.HIGH or (SCAN_ON_FIRST_LOOP and is_first_loop)):
    is_first_loop = False
    looking_for_qr = True

  if looking_for_qr:
    # turn LED on:
    a.digitalWrite(LED_PIN, a.HIGH)

    filename = "shots/photo{:08d}.jpg".format(counter)

    # Make sure we never run out of diskspace and reset
    # file counter when we've reached our preconfigured max.
    if counter < MAX_SAVED_SHOTS:
      counter += 1
    else:
      counter = 1

    # Remove if exists
    try:
      os.remove(filename)
    except OSError:
      pass

    # Capture webcam image and write to filename
    subprocess.check_output(["fswebcam", "-r", "1280x720", filename])

    try:
      # ascii art! (too much time)
      term_height = int(subprocess.check_output(["tput", "lines"]))
      # get something between 10 and term_height
      height = min(term_height, max(10, term_height - 10))
      subprocess.call(['jp2a', '--height={}'.format(height), '--colors', '--fill', filename])
    except subprocess.CalledProcessError as e:
      print(e)

    try:
      # Capture output from stdout "QR-Code:Pearl Jam - Ten"
      msg = subprocess.check_output(['zbarimg', filename])

      # turn of the light
      a.digitalWrite(LED_PIN, a.LOW)

      # stdout had a newline or something, so strip() is applied here
      # to remove it.
      msg = msg.strip()
      # let the loop know we found the qr code
      looking_for_qr = False
      # now let's see if we can play that qr code!
      pass_on_the_good_music(msg)
    except subprocess.CalledProcessError as e:
      print("no qr code embedded")

  else:
    # turn LED off:
    a.digitalWrite(LED_PIN, a.LOW)


def pass_on_the_good_music(msg_from_qrcode):
  print("we a qr code! {}".format(msg_from_qrcode))

  print("do we have music?")

  item = get_item_for_qr_code(msg_from_qrcode)
  if item:
    print("yes! it's:")
    print(item['uri'])
    play_item(item)
  else:
    print "sadly, no... try again!"
    return

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
  run_command(cmus=['cmus-remote', '-p'], mpd=['mpc', 'play'])

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


# "clean" quitting with C-c
def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)

interrupted = False
def run():
  global interrupted

  # we only start through tmux so cmus should always be running
  # exit_if_cmus_is_not_running()

  setup()
  print("OK make shots!")
  while True:
    loop()

    if interrupted:
      print("Gotta go")
      break


if __name__ == '__main__':
  run()
