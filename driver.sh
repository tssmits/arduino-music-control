#!/usr/bin/env bash

# If music_client crashes, we spin it up again automatically.

while true; do
  venv/bin/python driver.py

  # gives the user a change to do Ctrl-C again to quit this bash script.
  sleep 1
done
