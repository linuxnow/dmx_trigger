#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__author__ = "Pau Aliagas <linuxnow@gmail.com>"
__copyright__ = "Copyright (c) 2021 Pau Aliagas"
__license__ = "GPL 3.0"


import os
import argparse

from dmx_trigger.dmx_monitor import DMX512Monitor, DMX_CALLBACK
from dmx_trigger.video_provider import VLCVideoProviderDir
from dmx_trigger.config import load_config
# running settings
# from dmx_trigger.settings import settings


# default params
LOGGER = "dmx_trigger"

def parse_args():
    parser = argparse.ArgumentParser(
            description="Make files found in specified media folder (in alphabetic order) available to the specified universe.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--config", dest="config_file",
            help="the configuration file",
            default=(os.environ.get("DMX_TRIGGER_CONFIG") or
            "~/.config/dmx_trigger.yaml"))
    parser.add_argument("--logger", dest="logger",
            help="optional logger name (defaults to %s)" % LOGGER)
    parser.add_argument(
            "media_folder",
            help="Where to find files to play")
    parser.add_argument(
            "-u", "--universe",
            type=int, default=1,
            help="Universe number")
    parser.add_argument(
            '--extension',
            default='mkv',
            help="file extension of the files to play")

    return(parser.parse_args())

def main():
    # read command line args
    args = parse_args()

    # convert to absolute path before forking to allow user and relative paths
    config_file = os.path.abspath(os.path.expanduser(args.config_file))

    # combine args and config file
    # load config file and check provided values
    config = load_config(config_file)
    # always import after configuring logging (load_config does it)
    import logging

    # update settings with config params
    # settings.update(config)

    # setup the video provider
    video_provider = VLCVideoProviderDir(args.media_folder)

    # listen for DMX512 values in the specified universe
    dmx_monitor = DMX512Monitor(args.universe, DMX_CALLBACK, video_provider)
    dmx_monitor.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
