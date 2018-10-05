# arduino-music-control

Part of [retroversion](https://github.com/tssmits/retroversion) project.

## Usage of current version

Currently, the project is capable of scanning a QR code, and uses a manually constructed mapping ([map.csv](https://github.com/tssmits/arduino-music-control/map.csv)) to get the Spotify URI. It then plays the music.

1. Power up Raspberry Pi
2. Connect webcam and Arduino
3. Connect to HiFi Audio system
3. ssh into raspberry pi
4. navigate to ~/arduino-music-control
5. `./start.sh`

A tmux session is now started with three running programs:
* `mopidy` (music player)
* `./driver.sh` (listens to arduino buttons)
* `./client.sh` (webcam, read qr code, send commands to mopidy)

You can already use it! Place a QR code on the scanner surface, and press the "Read QR" button on the Arduino. Wait a little while, and music starts playing.

Do you want to see the internals?
1. `tmux a -t music`
2. `ctrl-b n` to navigate to next window
3. `ctrl-b d` to detach from tmux

## How it works (roughly)

`driver.py` uses Nanpy to communicate and control Arduino. When buttons are registered, the signal is passed on via ZeroMQ to `music_client.py`. There, the webcam is started and the photo is passed on to `zbarimg` to find QR code. When found, if it is in `map.csv`, its Spotify URI is passed to Mopidy via `mpc` commands.
