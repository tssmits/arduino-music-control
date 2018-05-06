#!/usr/bin/env bash

# This is to test how to use cmus-remote.
#
# cmus-remote sucks.
#
# I haven't found a good way to select the starting
# track. That's why i do these hacks where i play-stop and then play-next.
# Don't know why it works. But it seems to work well enough.

# stop playing (hack)
cmus-remote -p
cmus-remote -s
# clear all lists
cmus-remote -C "clear -l"
cmus-remote -C "clear -p"
cmus-remote -C "clear -q"
# add found album
cmus-remote "/media/pi/LACIE/music/Storage2/audio/Pearl Jam - Ten (PBTHAL Vinyl Rip 2011)"
# start playing baby (hack)
cmus-remote -p
cmus-remote -n
cmus-remote -p
