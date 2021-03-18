#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Receive DMX data from olad.

We receive an array of DMX channel values (max 512).
we trigger callback functions for each channel with the received value
only when values change.
Channels are always processed sequentially from 0 to the highest number.

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
__all__ = ['DMX512Monitor']

import logging
from ola.ClientWrapper import ClientWrapper

logger = logging.getLogger(__name__)

# We sort the channels to optimize two things:
# 1. DMX partial transmission: only updated channels are transmitted
# 2. program logic: we know that previous channels have been processed
CHANNEL = {'THEME': 0, 'SCENE': 1, 'RATE': 2, 'RESET': 3, 'REWIND': 4,
    'PAUSE': 5, 'RESUME': 6}

DMX_CALLBACK=[ [CHANNEL['THEME'], "set_theme"],
    [CHANNEL['SCENE'], "set_scene"],
    [CHANNEL['RATE'], "change_delta_rate"],
    [CHANNEL['RESET'], "reset_rate"],
    [CHANNEL['REWIND'], "rewind"],
    [CHANNEL['PAUSE'], "pause"],
    [CHANNEL['RESUME'], "resume"]]

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
        changed = False

        # check data for monitored channels only and trigger callbacks
        for c in self.dmx_cb:
            idx, func = c
            try:
                # on change call function and update with new value when done
                if data[idx] != self.dmx_channel[idx]:
                    changed = True
                    logger.info("Request change channel {} value from {} to {}".format(idx, self.dmx_channel[idx], data[idx]))
                    getattr(self.video_provider, func)(data[idx], current=self.dmx_channel[idx])
                    self.dmx_channel[idx] = data[idx]
            except IndexError:
                # either we have a bad channel or we have iterated data
                break
        # Call post callback function if anything has changed
        if changed:
            self.video_provider.exec_pending()

    def run(self):
        wrapper = ClientWrapper()
        client = wrapper.Client()
        client.RegisterUniverse(self._universe, client.REGISTER, self.newdata)
        wrapper.Run()
