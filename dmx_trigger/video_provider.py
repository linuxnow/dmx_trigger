#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Pau Aliagas <linuxnow@gmail.com>"

"""
Create a playlist with videos from a folder sorted alphabetically
and provide control with classs methods.

"""

import os
import vlc

valid_extensions = [".avi", ".gif", ".mkv", ".mov", ".mp4", ".jpg", ".jpeg", ".png"]
RATE_DELTA=0.05

class VLCVideoProviderDir(object):
    def __init__(self, rootpath, file_ext=valid_extensions, volume=0, log_level=0):
        self._media_files = []
        self._rootpath = rootpath
        self._file_ext = file_ext
        self._log_level = log_level
        self._current_video = 0
        self._current_rate = 0
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

        if self._log_level >= 2:
            print("read file list")
        self._media_files = [f for f in os.listdir(self._rootpath) if os.path.splitext(f)[1] in self._file_ext]
        self._media_files.sort()

        if self._log_level >= 2:
            print("playlist:")
        for index, media_file in enumerate(self._media_files):
            if self._log_level >= 2:
                print(index, media_file)

    def _load_media(self, n, reset_rate=True):
        if self._log_level:
            print ("Video load requested: {:d}".format(n))

        # get source name
        try:
            source = os.path.join(self._rootpath, self._media_files[n])
        except IndexError:
            print ("Video not found in position: {:d}".format(n))
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

    def play_video(self, n, load=True, reset_rate=True):
        if self._log_level:
            print ("Video requested: {:d}".format(n))
        # load_media
        if load:
            self._load_media(n, reset_rate)
        # start playing video
        self.media_player.play()

        if self._log_level >= 2:
            print ("Started video: {:d}".format(n))

    def change_rate_video(self, n):
        new_rate = rate = self.media_player.get_rate()

        # change rate
        if self._current_rate > n:
            new_rate = rate - RATE_DELTA
        elif self._current_rate < n:
            new_rate = rate + RATE_DELTA
        self.media_player.set_rate(new_rate)
        # update current rate
        self._current_rate = n

        if self._log_level:
            print ("Rate changed from {:f} to: {:f}".format(rate, new_rate))

    def reset_rate_video(self, n):
        reset_rate = 1.0
        if self._log_level:
            rate = self.media_player.get_rate()
            print ("Video rate reset requested: rate was {:f}".format(rate))
        self.media_player.set_rate(reset_rate)
        # update current rate
        self._current_rate = reset_rate

    def rewind_video(self, n):
        if self._log_level:
            print ("Video rewind requested {:d}".format(n))

        # only rewind when value is zero
        if n == 0:
            if self.media_player.get_state() != vlc.State.Ended:
                self.media_player.set_position(0)
                load = False
                # if video hasn't ended, keep rate
                reset_rate=False
            else:
                # reload video when finished as set_position does not work
                load = True
                # if video hss ended, reset rate
                reset_rate=True
            self.play_video(self._current_video, load=load, reset_rate=reset_rate)

    def pause_video(self, n):
        if self._log_level:
            if self.media_player.is_playing():
                print ("Video pause requested {:d}".format(n))
            else:
                print ("Video unpause requested {:d}".format(n))
        self.media_player.pause()

    def resume_video(self, n):
        if self._log_level:
            print ("Video resume requested {:d}".format(n))
        self.media_player.play()
