#!/usr/bin/env python

import sys
import zmq

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect('tcp://127.0.0.1:5555')
subscriber.setsockopt(zmq.SUBSCRIBE, b'')

requester = context.socket(zmq.REQ)
requester.connect('tcp://127.0.0.1:5556')

print(subscriber.recv())

requester.send(b'led_on')
print(requester.recv())
