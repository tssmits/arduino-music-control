#!/usr/bin/env bash

cd /media/pi/LACIE/music
rm ~/list.txt
ls -d -1 $PWD/Storage2/audio/** >> ~/list.txt
ls -d -1 $PWD/Storage3/audio/clean/** >> ~/list.txt
ls -d -1 $PWD/Storage3/audio/filthy/** >> ~/list.txt
ls -d -1 $PWD/Storage3/audio/filthier/** >> ~/list.txt
ls -d -1 $PWD/Storage3/Downloads/** >> ~/list.txt
ls -d -1 $PWD/Storage3/music/bandcamp/** >> ~/list.txt
ls -d -1 $PWD/Storage3/music/public/** >> ~/list.txt
ls -d -1 $PWD/Storage3/whatcd/** >> ~/list.txt
ls -d -1 $PWD/Storage3/whatcd/whatcd/** >> ~/list.txt
