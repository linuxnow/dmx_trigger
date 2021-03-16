#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create a playlist with videos from a folder sorted alphabetically
and provide control with classs methods.
"""

__author__ = "Pau Aliagas <linuxnow@gmail.com>"
__copyright__ = "Copyright (c) 2021 Pau Aliagas"
__license__ = "GPL 3.0"
__all__ = ['VLCVideoProviderDir']

import logging
import os
import vlc

logger = logging.getLogger(__name__)

valid_extensions = [".avi", ".gif", ".mkv", ".mov", ".mp4", ".jpg", ".jpeg", ".png"]
RATE_DELTA=0.05

class VLCVideoProviderDir(object):
    def __init__(self, rootpath, file_ext=valid_extensions, volume=0):
        self._media_files = []
        self._rootpath = rootpath
        self._file_ext = file_ext
        self._current_video = 0
        self._current_rate = 1
        self._volume = volume

        # vlc player
        self.media_player = vlc.MediaPlayer("--fullscreen ", "--no-audio", "--intf", "'--mouse-hide-timeout=0", "--video-on-top")
        self.media_player.set_fullscreen(True)
        self.media_player.audio_set_volume(self._volume)

        # read files from dir
        self.load_files()

    def load_files(self):
        """
        this function is responsible of opening the media.
        it could have been done in the __init__, but it is just an example

        in this case it scan the specified folder, but it could also scan a
        remote url or whatever you prefer.
        """

        logger.debug("read file list")
        self._media_files = [f for f in os.listdir(self._rootpath) if os.path.splitext(f)[1] in self._file_ext]
        self._media_files.sort()

        logger.debug("playlist:")
        for index, media_file in enumerate(self._media_files):
            logger.debug("{}: {}".format(index, media_file))

    def _load_media(self, n, reset_rate=True):
        logger.debug("Video load requested: {:d}".format(n))

        # get source name
        try:
            source = os.path.join(self._rootpath, self._media_files[n])
        except IndexError:
            logger.warning("Video not found in position: {:d}".format(n))
            return

        # create a media object
        media = vlc.Media(source)
        # set media to the media player
        self.media_player.set_media(media)
        # update current video
        self._current_video = n
        # reset rate
        if reset_rate:
            self.reset_rate_video(n)

    def play_video(self, n, current=None, load=True, reset_rate=True):
        logger.info("Video requested: {:d}".format(n))
        # load_media
        if load:
            self._load_media(n, reset_rate)
        # start playing video
        self.media_player.play()

        logger.debug("Started video:: {:d}".format(n))

    def change_rate_video(self, n, current=None):
        # ignore initial rate change
        if current is None:
            logger.debug("Initial rate change ignored.")
            return

        new_rate = rate = self.media_player.get_rate()

        # change rate
        if self._current_rate > n:
            new_rate = rate - RATE_DELTA
        elif self._current_rate < n:
            new_rate = rate + RATE_DELTA
        self.media_player.set_rate(new_rate)
        # update current rate
        self._current_rate = n

        logger.info("Rate changed from {:f} to: {:f}".format(rate, new_rate))

    def reset_rate_video(self, n, current=None):
        reset_rate = 1.0
        logger.info("Video rate reset requested: rate was {:f}".format(self.media_player.get_rate()))
        self.media_player.set_rate(reset_rate)
        # update current rate
        self._current_rate = reset_rate

    def rewind_video(self, n, current=None):
        # ignore initial rewind
        if current is None:
            logger.debug("Initial rewind ignored.")
            return

        logger.info("Video rewind requested {:d}".format(n))

        # only rewind when value is zero
        if n == 0:
            """
            if self.media_player.get_state() != vlc.State.Ended:
                self.media_player.set_position(0)
                load = False
                # if video hasn't ended, keep rate
                reset_rate = False
            else:
                # reload video when finished as set_position does not work
                load = True
                # if video hss ended, reset rate
                reset_rate = True
            """
            # It's *much* faster to always load, so we do it unconditionally
            # In slow systems like RPi it could take several seconds
            load = reset_rate = True
            self.play_video(self._current_video, load=load, reset_rate=reset_rate)

    def pause_video(self, n, current=None):
        # ignore initial pause
        if current is None:
            logger.debug("Initial pause ignored.")
            return

        if self.media_player.is_playing():
            logger.info("Video pause requested {:d}".format(n))
        else:
            logger.info("Video unpause requested {:d}".format(n))
        self.media_player.pause()

    def resume_video(self, n, current=None):
        logger.info("Video resume requested {:d}".format(n))
        self.media_player.play()
