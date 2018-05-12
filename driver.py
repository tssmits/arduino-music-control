#!/usr/bin/env python

import threading
import time
import zmq

import arduino.controller

class PublisherThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.context = zmq.Context()
    self.publisher = self.context.socket(zmq.PUB)
    self.publisher.bind("tcp://*:5555")

  def run(self):
    while True:
      self.publisher.send_string("Hello :)")

class ReceiverThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.context = zmq.Context()
    self.receiver = self.context.socket(zmq.REP)
    self.receiver.bind("tcp://*:5556")

  def run(self):
    while True:
      msg = self.receiver.recv()
      self.receiver.send(b'Echo: '+msg)

publisherThread = PublisherThread()
receiverThread = ReceiverThread()

publisherThread.daemon = True
receiverThread.daemon = True

publisherThread.start()
receiverThread.start()

while True:
  time.sleep(1)
