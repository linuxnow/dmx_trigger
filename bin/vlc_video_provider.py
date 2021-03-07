#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Pau Aliagas <linuxnow@gmail.com>"

"""
Create a playlist with videos from a folder sorted alphabetically.
Then receive DMX data to control the video play.

We receive an array of DMX channel values (max 512)
Channel 0: video number
Channel 1: faster/slower
Channel 2: reset rate
Channel 3: rewind (if value is zero)
Channel 4: pause/unpause
Channel 5: resume

"""

import argparse

from dmx_trigger.dmx_monitor import DMX512Monitor, DMX_CALLBACK
from dmx_trigger.video_provider import VLCVideoProviderDir

def parse_args():
    parser = argparse.ArgumentParser(
            description="Make files found in specified media folder (in alphabetic order) available to the specified universe.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            "media_folder",
            help="Where to find files to play")
    parser.add_argument(
            "-u", "--universe",
            type=int, default=1,
            help="Universe number).")
    parser.add_argument(
            '--extension',
            default='ts',
            help="file extension of the files to play")
    parser.add_argument("-v", "--verbosity", action="count",default=0,
           help="increase output verbosity")
    return(parser.parse_args())

def main():
    global args
    # read caommand line args
    args = parse_args()

    # setup the video provider
    video_provider = VLCVideoProviderDir(args.media_folder, verbosity=args.verbosity)

    # listen for DMX512 values in the specified universe
    dmx_monitor = DMX512Monitor(args.universe, DMX_CALLBACK, video_provider, verbosity=args.verbosity)
    dmx_monitor.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bye!")
