#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Pau Aliagas <linuxnow@gmail.com>"

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

from ola.ClientWrapper import ClientWrapper

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
    def __init__(self, universe, dmx_cb, video_provider, verbosity=0):
        self._universe = universe
        self.dmx_cb = dmx_cb
        self.video_provider = video_provider
        self._verbosity = verbosity
        # initialise empty list of channels
        self.dmx_channel = [0]*512

    def newdata(self, data):
        if self._verbosity >= 2:
            print(data)

        # check data for monitored channels only and trigger callbacks
        for c in self.dmx_cb:
            idx, func = c
            try:
                # on change call function and update with new value when done
                if data[idx] != self.dmx_channel[idx]:
                    if self._verbosity >= 2:
                        getattr(self.video_provider, func)(data[idx])
                    self.dmx_channel[idx] = data[idx]
            except IndexError:
                # either we have a bad channel or we have iterated data
                # print ("Out of range channel requested: {:d}".format(idx))
                break

    def run(self):
        wrapper = ClientWrapper()
        client = wrapper.Client()
        client.RegisterUniverse(self._universe, client.REGISTER, self.newdata)
        wrapper.Run()
