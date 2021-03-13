#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Receive DMX data from olad.

We receive an array of DMX channel values (max 512).
we trigger callback functions for each channel with the received value
only when values change.

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
__all__ = ['DMX512Monitor']

import logging
from ola.ClientWrapper import ClientWrapper

logger = logging.getLogger(__name__)


VIDEO_CHANNEL=0
RATE_CHANNEL=1
RESET_RATE_CHANNEL=2
REWIND_CHANNEL=3
PAUSE_CHANNEL=4
RESUME_CHANNEL=5

DMX_CALLBACK=[[VIDEO_CHANNEL, "play_video"],
    [RATE_CHANNEL, "change_rate_video"],
    [RESET_RATE_CHANNEL, "reset_rate_video"],
    [REWIND_CHANNEL, "rewind_video"],
    [PAUSE_CHANNEL, "pause_video"],
    [RESUME_CHANNEL, "resume_video"]]

class DMX512Monitor(object):
    def __init__(self, universe, dmx_cb, video_provider):
        self._universe = universe
        self.dmx_cb = dmx_cb
        self.video_provider = video_provider
        # initialise empty list of channels
        self.dmx_channel = [None]*512

    def newdata(self, data):
        # too much noise
        # logger.debug(data)

        # check data for monitored channels only and trigger callbacks
        for c in self.dmx_cb:
            idx, func = c
            try:
                # on change call function and update with new value when done
                if data[idx] != self.dmx_channel[idx]:
                    logger.info("Request change channel {} value from {} to {}".format(idx, self.dmx_channel[idx], data[idx]))
                    getattr(self.video_provider, func)(data[idx], current=self.dmx_channel[idx])
                    self.dmx_channel[idx] = data[idx]
            except IndexError:
                # either we have a bad channel or we have iterated data
                break

    def run(self):
        wrapper = ClientWrapper()
        client = wrapper.Client()
        client.RegisterUniverse(self._universe, client.REGISTER, self.newdata)
        wrapper.Run()
