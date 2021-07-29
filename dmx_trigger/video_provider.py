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
DEFAULT_PLAYMODE="default"

class VLCVideoProviderDir(object):
    def __init__(self, media_config=None, file_ext=valid_extensions, volume=0):
        self._media_config = media_config
        self._playlist = media_config["playlist"]
        self._vlclist = {}
        self._file_ext = file_ext
        self.current_theme = None
        self.requested_theme = 0
        self.current_scenee = None
        self.requested_scene = 0
        self.current_rate = self.requested_rate = 0
        self.requested_reset_rate = False
        self._rewind = False
        self.requested_release = 0
        self._release = False
        self._volume = volume
        self.vlc = {
            "instance": None,
            "player": None,
            "list_player": None,
            "playlist": None,
        }

        # vlc player
        self._init_vlc()
        # indexed access list to file names and properties
        self._vlclist = self._build_playlist_from_config()

    def _init_vlc(self):
        """
        Initialise the VLC variables:
            - The VLC instance
            - A MediaListPlayer for playing playlists
            - A MediaPlayer for controlling playback
            - A MediaList to load in the MediaListPlayer
        Documentation for these can be found here:
            http://www.olivieraubert.net/vlc/python-ctypes/doc/
        """
        # vlc media list player
        flags = ["--quiet", "--no-audio", "--intf", "--mouse-hide-timeout=0", "--video-on-top", "volume={}".format(self._volume)]
        self.vlc["instance"] = vlc.Instance(flags)
        self.vlc['list_player'] = self.vlc['instance'].media_list_player_new()
        self.vlc['player'] = self.vlc['list_player'].get_media_player()
        self.vlc["player"].set_fullscreen(True)
        self.vlc['playlist'] = self.vlc['instance'].media_list_new()
        self.vlc["list_player"].set_media_list(self.vlc["playlist"])

    def _get_filename(self, theme, scene=0):
        """Get the full path filename.

        :param int theme: theme number
        :param int scene: scene number
        :rtype str
        """
        logger.debug("Get filename in position {}.{}".format(theme, scene))
        try:
            logger.debug("vlclist item {}.{}: {}".format(theme, scene, self._vlclist[theme, scene]))
            return self._vlclist[theme, scene]["file"]
        except KeyError:
            msg = "No files in position {}.{}".format(theme, scene)
            logger.warn(msg)
            raise Exception(msg)

    def _build_playlist_from_config(self, media_list = None):
        """
        This function is responsible for checking the media list.

        It reads a yaml configuration file and adds all valid entries
        to the returned playlist.

        :rtype dict
        """
        logger.debug("Check load file list from config")
        vlclist = {}
        pos = 0
        for p in self._playlist:
            dir = self._playlist[p]["dir"]
            files = self._playlist[p]["files"]
            try:
                playmode = self._playlist[p]["playmode"]
            except KeyError:
                playmode = DEFAULT_PLAYMODE
            for (idx, f) in enumerate(files):
                # expand user and convert to absolute path
                file = os.path.abspath(os.path.expanduser(os.path.join(dir, f)))
                if os.path.isfile(file):
                    logger.debug("File {} in pos {}.{} exists".format(file, p, idx))
                    if os.path.splitext(f)[1] not in self._file_ext:
                        logger.warn("File {} in pos {}.{} does not have a valid extension".format(file, p, idx))
                    vlclist[p, idx] = {"file": file, "playmode": playmode, "pos": pos}
                    if media_list:
                        media_list.add_media(vlc.Media(file))
                    pos += 1
                    logger.debug("vlclist item {}.{}: {}".format(p, idx, vlclist[p, idx]))
                else:
                    logger.warn("File {} in pos {}.{} does not exist".format(file, p, idx))
        return vlclist

    def _load_media(self, file, playmode=DEFAULT_PLAYMODE):
        """Loads media

        Loads the requested media.

        Returns True if all could be executed successfully, False otherwise.

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
        self.vlc["player"].set_media(media)
        return True

    def _play_media(self):
        """Play media unconditionally.

        Loads and plays the requested media, resetting all the properties that
        need not be executed.

        Returns True if all could be executed successfully, False otherwise.

        :rtype bool
        """
        logger.debug("Media play requested: {}.{}".format(self.requested_theme, self.requested_scene))
        # forget rewind when asked to play media
        self._rewind = False
        try:
            file = self._get_filename(self.requested_theme, scene=self.requested_scene)
            playmode = self._vlclist[self.requested_theme, self.requested_scene]["playmode"]
        except:
            msg = "Error getting file name in position {}.{}".format(self.requested_theme, self.requested_scene)
            logger.error(msg)
            return False

        # load_media
        if self._load_media(file, playmode=playmode):
            # update current video
            self.current_theme = self.requested_theme
            self.current_scenee = self.requested_scene
            self.current_rate = self.requested_rate
            # reset rate
            self.vlc["player"].set_rate(DEFAULT_RATE)
            # start playing video
            logger.debug("Play video {} in position {}.{}".format(file, self.requested_theme, self.requested_scene))
            self.vlc["player"].play()
            return True
        else:
            logger.debug("Could not start video {} in position {}.{}".format(file, self.requested_theme, self.requested_scene))
            return False

    def _load_medialist(self, file, playmode=DEFAULT_PLAYMODE):
        """Loads media

        Loads the requested media list with a single file.

        Returns True if all could be executed successfully, False otherwise.

        :rtype bool
        """
        logger.debug("Media list load requested: {}, playmode = {}".format(file, playmode))

        # check that file exists
        if not os.path.isfile(file):
            logger.warning("Video not found: {}".format(file))
            return False

        # create media list with one file
        # first empty list
        i = self.vlc["playlist"].count()
        self.vlc["playlist"].lock()
        while i:
            self.vlc["playlist"].remove_index(0)
            i -= 1;
        # create a media object
        media = self.vlc['instance'].media_new(file)
        # add media to the playlist
        self.vlc["playlist"].add_media(media)
        self.vlc["playlist"].unlock()
        if playmode == "loop":
            self.vlc["list_player"].set_playback_mode(vlc.PlaybackMode.loop)
        elif playmode == "repeat":
            self.vlc["list_player"].set_playback_mode(vlc.PlaybackMode.repeat)
        else:
            self.vlc["list_player"].set_playback_mode(vlc.PlaybackMode.default)

        return True

    def _play_medialist(self):
        """Play media unconditionally from playlist.

        Loads and plays the requested media, resetting all the properties that
        need not be executed.

        Returns True if all could be executed successfully, False otherwise.

        :rtype bool
        """
        # forget rewind when asked to play media
        self._rewind = False
        logger.debug("Media play requested: {}.{}".format(self.requested_theme, self.requested_scene))
        try:
            pos = self._vlclist[self.requested_theme, self.requested_scene]["pos"]
            file = self._get_filename(self.requested_theme, scene=self.requested_scene)
            playmode = self._vlclist[self.requested_theme, self.requested_scene]["playmode"]
            logger.debug("Media play requested: {}.{} is in playlist position {}".format(self.requested_theme, self.requested_scene, pos))
        except:
            msg = "Error getting file name in position {}.{}".format(self.requested_theme, self.requested_scene)
            logger.error(msg)
            return False

        # load_media
        if self._load_medialist(file, playmode=playmode):
            # update current video
            self.current_theme = self.requested_theme
            self.current_scenee = self.requested_scene
            self.current_rate = self.requested_rate
            # reset rate
            self.vlc["player"].set_rate(DEFAULT_RATE)
            # start playing video
            logger.debug("Play video {} in position {}.{}".format(file, self.requested_theme, self.requested_scene))
            # we play the file in position 0
            self.vlc["list_player"].play_item_at_index(0)
            return True
        else:
            logger.debug("Could not start video {} in position {}.{}".format(file, self.requested_theme, self.requested_scene))
            return False

    def _change_delta_rate(self):
        """Execute the delta rate change.
        """
        logger.debug("Change delta rate")
        new_rate = rate = self.vlc["player"].get_rate()
        # change rate
        if self.current_rate > self.requested_rate:
            new_rate = rate - DELTA_RATE
        elif self.current_rate < self.requested_rate:
            new_rate = rate + DELTA_RATE
        self.vlc["player"].set_rate(new_rate)
        # update current rate
        self.current_rate = self.requested_rate

        logger.info("Delta rate changed from {:f} to: {:f}".format(rate, new_rate))

    def exec_pending(self):
        """Execute the pending actions.

        Returns True if all could be executed successfully, False otherwise.

        :rtype bool
        """
        logger.info("Execute pending actions: release = {}".format(self._release))
        # do not consider playing until we have a release
        # check for new theme and scene or rewind
        if  (self._release and
            (self.requested_theme != self.current_theme or
            self.requested_scene != self.current_scenee)):
            return self._play_medialist()
         # check for rewind
        elif self._rewind:
            return self._play_medialist()
        # check for rate reset
        elif self.requested_reset_rate:
            # update current rate
            self.vlc["player"].set_rate(DEFAULT_RATE)
            self.requested_reset_rate = False
        # check for rate change
        elif self.requested_rate != self.current_rate:
            self._change_delta_rate()
        return True

    def release(self, n, current=None):
        """Allow action to be executed.

        When we move from zero to a positive value, we play the video.

        :param int n: value
        """
        logger.info("Release requested: {:d}".format(n))

        # When we move from 0 to positive value, it's a release
        logger.debug("pre: requested_release = {}, release = {}".format(self.requested_release, self._release))
        self._release = (n > 0)
        self.requested_release = n
        logger.debug("post: requested_release = {}, release = {}".format(self.requested_release, self._release))

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
            self._rewind = True

    def pause(self, n, current=None):
        if self.vlc["player"].is_playing():
            logger.info("Video pause requested {:d}".format(n))
        else:
            logger.info("Video unpause requested {:d}".format(n))
        self.vlc["player"].pause()

    def resume(self, n, current=None):
        logger.info("Video resume requested {:d}".format(n))
        self.vlc["player"].play()
