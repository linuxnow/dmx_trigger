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
DEFAULT_RATE=1.0
DELTA_RATE=0.05

class VLCVideoProviderDir(object):
    def __init__(self, rootpath, media_config=None, file_ext=valid_extensions, volume=0):
        self._media_files = []
        self._rootpath = rootpath
        self._media_config = media_config
        self._playlist = media_config['playlist']
        self._file_ext = file_ext
        self.current_theme = None
        self.requested_theme = 0
        self.current_scenee = None
        self.requested_scene = 0
        self.current_rate = self.requested_rate = 0
        self.requested_reset_rate = False
        self._rewind = False
        self._volume = volume

        # vlc player
        self.media_player = vlc.MediaPlayer("--fullscreen ", "--no-audio", "--intf", "'--mouse-hide-timeout=0", "--video-on-top")
        self.media_player.set_fullscreen(True)
        self.media_player.audio_set_volume(self._volume)

        # read file list
        if self._media_config:
            self._check_files_from_config()
        else:
            self._load_files_from_dir()

    def _get_filename(self, n, scene=0):
        """Get the full path filename.

        :param int n: theme number
        :param int scene: scene number
        :rtype str
        """
        logger.debug("Get filename in position {}.{}".format(n, scene))
        try:
            dir = self._playlist[n]['dir']
            files = self._playlist[n]['files']
        except KeyError:
            msg = "No 'dirs' or 'files' section in position {}.{}".format(n, scene)
            logger.warn(msg)
            raise Exception(msg)
        try:
            f = files[scene]
        except IndexError:
            msg = "No file in position {}.{}".format(n, scene)
            logger.warn(msg)
            raise Exception(msg)
        file = os.path.join(dir, f)
        logger.debug("File {} in pos {}.{}".format(file, n, scene))
        return file

    def _check_files_from_config(self):
        """
        This function is responsible for checking the media list.

        IT reads a yaml configuration file.
        """
        logger.debug("Check load file list from config")
        for p in self._playlist:
            dir = self._playlist[p]['dir']
            files = self._playlist[p]['files']
            for (idx, f) in enumerate(files):
                file = os.path.join(dir, f)
                if os.path.isfile(file):
                    logger.debug("File {} in pos {}.{} exists".format(file, p, idx))
                    if os.path.splitext(f)[1] not in self._file_ext:
                        logger.warn("File {} in pos {}.{} does not have a valid extension".format(file, p, idx))
                else:
                    logger.warn("File {} in pos {}.{} does not exist".format(file, p, idx))

    def _load_files_from_dir(self):
        """
        This function is responsible of loading the media list.

        In this case it scan the specified folder, but it could also scan a
        remote url or whatever you prefer.
        """
        logger.debug("Load file list from dir")
        self._media_files = [f for f in os.listdir(self._rootpath) if os.path.splitext(f)[1] in self._file_ext]
        self._media_files.sort()

        logger.debug("playlist:")
        for index, media_file in enumerate(self._media_files):
            logger.debug("{}: {}".format(index, media_file))

    def _load_media(self, file, reset_rate=True):
        """Loads media

        Loads the requested media.

        Returns True if all could be executted successfully, False otherwise.

        :rtype bool
        """
        logger.debug("Video load requested: {}".format(file))

        # check that file exists
        if not os.path.isfile(file):
            logger.warning("Video not found: {}".format(file))
            return False

        # create a media object
        media = vlc.Media(file)
        # set media to the media player
        self.media_player.set_media(media)
        return True

    def _play_media(self):
        """Play media unconditionally.

        Loads and plays the requested media, resetting all the properties that
        need not be ececuted.

        Returns True if all could be executted successfully, False otherwise.

        :rtype bool
        """
        logger.debug("Media play requested: {}.{}".format(self.requested_theme, self.requested_scene))
        try:
            file = self._get_filename(self.requested_theme, scene=self.requested_scene)
        except:
            msg = "Error getting file name in position {}.{}".format(self.requested_theme, self.requested_scene)
            logger.error(msg)
            return False
        # load_media
        if self._load_media(file):
            # update current video
            self.current_theme = self.requested_theme
            self.current_scenee = self.requested_scene
            self.current_rate = self.requested_rate
            self._rewind = False
            # reset rate
            self.media_player.set_rate(DEFAULT_RATE)
            # start playing video
            logger.debug("Play video {} in position {}.{}".format(file, self.requested_theme, self.requested_scene))
            self.media_player.play()
            return True
        else:
            logger.debug("Could not start video {} in position {}.{}".format(file, self.requested_theme, self.requested_scene))
            return False

    def _change_delta_rate(self):
        """Execute the delta rate change.
        """
        logger.debug("Change delta rate")
        new_rate = rate = self.media_player.get_rate()
        # change rate
        if self.current_rate > self.requested_rate:
            new_rate = rate - DELTA_RATE
        elif self.current_rate < self.requested_rate:
            new_rate = rate + DELTA_RATE
        self.media_player.set_rate(new_rate)
        # update current rate
        self.current_rate = self.requested_rate

        logger.info("Delta rate changed from {:f} to: {:f}".format(rate, new_rate))

    def exec_pending(self):
        """Execute the pending actions.

        Returns True if all could be executted successfully, False otherwise.

        :rtype bool
        """
        logger.info("Execute pending actions")
        # check for new thene and scene or rewind
        if (self.requested_theme != self.current_theme or
            self.requested_scene != self.current_scenee):
            return self._play_media()
         # check for rewind
        elif self._rewind:
            return self._play_media()
        # check for rate reset
        elif self.requested_reset_rate:
            # update current rate
            self.media_player.set_rate(DEFAULT_RATE)
            self.requested_reset_rate = False
        # check for rate change
        elif self.requested_rate != self.current_rate:
            self._change_delta_rate()
        return True

    def set_theme(self, n, current=None):
        """Set the requested theme.

        Theme and scxene define the media to play.

        :param int n: theme number
        """
        logger.info("Theme requested: {:d}".format(n))
        self.requested_theme = n

    def set_scene(self, n, current=None):
        """Set the requested scene.

        Theme and scxene define the media to play.

        :param int n: scene number
        """
        logger.info("Scene requested: {:d}".format(n))
        self.requested_scene = n

    def change_delta_rate(self, n, current=None):
        """Change delta rate.

        When n increases, increase play rate by DELTA_RATE.
        When n decreases, decrease play rate by DELTA_RATE.

        :param int n: rate
        """
        logger.info("Delta rate change requested: {:d}".format(n))
        self.requested_rate = n

    def reset_rate(self, n, current=None):
        """Reset rate.

        Set play rate to default.

        :param int n: rate
        """
        logger.info("Rate reset requested: {:d}".format(n))
        self.requested_reset_rate = True

    def rewind(self, n, current=None):
        """Rewind media.

        Rewind only when value changes to 0.

        :param int n: value
        """
        logger.info("Video rewind requested {:d}".format(n))

        # only rewind when value is zero
        if n == 0:
            self._rewind = 1

    def pause(self, n, current=None):
        if self.media_player.is_playing():
            logger.info("Video pause requested {:d}".format(n))
        else:
            logger.info("Video unpause requested {:d}".format(n))
        self.media_player.pause()

    def resume(self, n, current=None):
        logger.info("Video resume requested {:d}".format(n))
        self.media_player.play()
