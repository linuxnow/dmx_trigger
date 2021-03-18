#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DMX controlled Media Server.

* Configure a numbered playlist with:
  -a config file
  -listing and sorting a directory
* Then receive DMX data to control the video play.

We receive an array of DMX channel values (max 512)
Channel 0: theme number
Channel 1: theme's scene number
Channel 2: faster/slower
Channel 3: reset rate
Channel 4: rewind (if value is zero)
Channel 5: pause/unpause
Channel 6: resume
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
            description="Make files found in specified media config available to the specified universe.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--config", dest="config_file",
            help="the configuration file",
            default=(os.environ.get("DMX_TRIGGER_CONFIG") or
            "~/.config/dmx_trigger.yaml"))
    parser.add_argument("--logger", dest="logger",
            help="optional logger name (defaults to %s)" % LOGGER)
    parser.add_argument("--media", dest="media_file",
            help="the media config file",
            default=(os.environ.get("DMX_TRIGGER_MEDIA") or
            "~/.config/media_list.yaml"))
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

    # convert to absolute path before forking to allow user and relative paths
    media_file = os.path.abspath(os.path.expanduser(args.media_file))
    # load media config file
    media_config = load_config(media_file)

    # update settings with config params
    # settings.update(config)

    # setup the video provider
    video_provider = VLCVideoProviderDir(media_config=media_config)

    # listen for DMX512 values in the specified universe
    dmx_monitor = DMX512Monitor(args.universe, DMX_CALLBACK, video_provider)
    dmx_monitor.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
