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

# "clean" quitting with C-c
def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)


# constants won't change. They're used here to set pin numbers:
# the number of the pushbutton pin
BUTTON_PIN = 2
# the number of the LED pin
LED_PIN = 13
# max shots in ./shots/ dir
MAX_SAVED_SHOTS = 25

BUTTON2_PIN = 4
BUTTON3_PIN = 7
BUTTON4_PIN = 8
BUTTON5_PIN = 12

POT_PIN = 2

# variables will change:
buttonState = 0    # variable for reading the pushbutton status

counter = 1

pot_value_normalized = 0

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
  subprocess.call(["cmus-remote", '-C', 'vol 70%'])


def loop():
  global counter
  global pot_value_normalized

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
    subprocess.call(["cmus-remote", '-p'])
    time.sleep(0.5)
  if a.digitalRead(BUTTON3_PIN) == a.HIGH:
    print("BUTTON3_PIN high (stop)")
    subprocess.call(["cmus-remote", '-s'])
    time.sleep(0.5)
  if a.digitalRead(BUTTON4_PIN) == a.HIGH:
    print("BUTTON4_PIN high (prev)")
    subprocess.call(["cmus-remote", '-r'])
    time.sleep(0.5)
  if a.digitalRead(BUTTON5_PIN) == a.HIGH:
    print("BUTTON5_PIN high (next)")
    subprocess.call(["cmus-remote", '-n'])
    time.sleep(0.5)


  # check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState == a.HIGH):
    # turn LED on:
    a.digitalWrite(LED_PIN, a.HIGH)

    found = False
    while not found:
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
      subprocess.check_output(["fswebcam", filename])

      try:
        # Capture output from stdout "QR-Code:Pearl Jam - Ten"
        msg = subprocess.check_output(['zbarimg', filename])
        found = True
        pass_on_the_good_music(msg)
      except subprocess.CalledProcessError as e:
        print("no qr code embedded")

  else:
    # turn LED off:
    a.digitalWrite(LED_PIN, a.LOW);


def pass_on_the_good_music(msg_from_qrcode):
  print("we have music! {}".format(msg_from_qrcode))
  try:
    # stop playing if you're playing
    subprocess.call(["cmus-remote", '-p'])
    subprocess.call(["cmus-remote", '-s'])
    # clear all the lists
    subprocess.call(["cmus-remote", '-C', 'clear -l'])
    subprocess.call(["cmus-remote", '-C', 'clear -p'])
    subprocess.call(["cmus-remote", '-C', 'clear -q'])
    # add found album
    subprocess.call(["cmus-remote", "/media/pi/LACIE/music/Storage2/audio/Pearl Jam - Ten (PBTHAL Vinyl Rip 2011)"])
    # start playing baby
    subprocess.call(["cmus-remote", '-p'])
    subprocess.call(["cmus-remote", '-n'])
    subprocess.call(["cmus-remote", '-p'])

    # Show status
    subprocess.call(["cmus-remote", '-Q'])
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

interrupted = False
if __name__ == '__main__':

  exit_if_cmus_is_not_running()

  setup()
  print("OK make shots!")
  while True:
    loop()

    if interrupted:
      print("Gotta go")
      break
