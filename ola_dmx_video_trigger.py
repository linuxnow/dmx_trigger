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
import os
import vlc
from ola.ClientWrapper import ClientWrapper

valid_extensions = [".avi", ".gif", ".mkv", ".mov", ".mp4", ".jpg", ".jpeg", ".png"]

VIDEO_CHANNEL=0
RATE_CHANNEL=1
RESET_RATE_CHANNEL=2
REWIND_CHANNEL=3
PAUSE_CHANNEL=4
RESUME_CHANNEL=5

DMX=[[VIDEO_CHANNEL, "play_video"],
    [RATE_CHANNEL, "change_rate_video"],
    [RESET_RATE_CHANNEL, "reset_rate_video"],
    [REWIND_CHANNEL, "rewind_video"],
    [PAUSE_CHANNEL, "pause_video"],
    [RESUME_CHANNEL, "resume_video"]]

video_provider = None
RATE_DELTA=0.05

# initialise empty list of channels
current_dmx_channel = [0]*512
args = []

class DMX512Monitor(object):
    def __init__(self, universe, dmx):
        self._universe = universe
        self.dmx = dmx

    def newdata(self, data):
        global current_dmx_channel

        if args.verbosity >= 2:
            print(data)

        # check monitored channels
        for c in self.dmx:
            idx, func = c
            try:
                # on change call function and update with new value when done
                if data[idx] != current_dmx_channel[idx]:
                    getattr(video_provider, func)(data[idx])
                    current_dmx_channel[idx] = data[idx]
            except IndexError:
                print ("Out of range channel requeested: {:d}".format(data[idx]))

    def run(self):
        wrapper = ClientWrapper()
        client = wrapper.Client()
        client.RegisterUniverse(self._universe, client.REGISTER, self.newdata)
        wrapper.Run()

class VideoProviderDir(object):
    def __init__(self, rootpath, file_ext=valid_extensions):
        self._media_files = []
        self._rootpath = rootpath
        self._file_ext = file_ext

        # vlc player
        self.media_player = vlc.MediaPlayer("--fullscreen ", "--no-audio", "--intf", "'--mouse-hide-timeout=0", "--video-on-top")
        self.media_player.set_fullscreen(True)

        # read files from dir
        self.load_files()

    def load_files(self):
        """
        this function is responsible of opening the media.
        it could have been done in the __init__, but it is just an example

        in this case it scan the specified folder, but it could also scan a
        remote url or whatever you prefer.
        """

        if args.verbosity >= 2:
            print("read file list")
        self._media_files = [f for f in os.listdir(self._rootpath) if os.path.splitext(f)[1] in self._file_ext]
        self._media_files.sort()

        if args.verbosity >= 2:
            print("playlist:")
        for index, media_file in enumerate(self._media_files):
            if args.verbosity >= 2:
                print(f"[{index}] {media_file}")

    def play_video(self, n):
        if args.verbosity:
            print ("Video requeested: {:d}".format(n))
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
        # start playing video
        self.media_player.play()

    def change_rate_video(self, n):
        new_rate = rate = self.media_player.get_rate()

        # change rate
        if current_dmx_channel[RATE_CHANNEL] > n:
            new_rate = rate - RATE_DELTA
        elif current_dmx_channel[RATE_CHANNEL] < n:
            new_rate = rate + RATE_DELTA
        self.media_player.set_rate(new_rate)

        if args.verbosity:
            print ("Rate changed from {:f} to: {:f}".format(rate, new_rate))

    def reset_rate_video(self, n):
        if args.verbosity:
            rate = self.media_player.get_rate()
            print ("Video rate reset requeested: rate was {:f}".format(rate))
        self.media_player.set_rate(1.0)

    def rewind_video(self, n):
        if args.verbosity:
            print ("Video rewind requeested {:d}".format(n))

        # only rewind when value is zero
        if n == 0:
            if self.media_player.get_state() != vlc.State.Ended:
                self.media_player.set_position(0)
                self.media_player.play()
            else:
                # replay video when finished as set_position does not work

                # This works but closes and opens the player waindow
                # self.media_player.stop()
                # self.media_player.play()

                # We play the video as new
                self.play_video(current_dmx_channel[idx])

    def pause_video(self, n):
        if args.verbosity:
            if self.media_player.is_playing():
                print ("Video pause requeested {:d}".format(n))
            else:
                print ("Video unpause requeested {:d}".format(n))
        self.media_player.pause()

    def resume_video(self, n):
        if args.verbosity:
            print ("Video resume requeested {:d}".format(n))
        self.media_player.play()

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
    global args, video_provider
    # read caommand line args
    args = parse_args()

    # setup the video provider
    video_provider = VideoProviderDir(args.media_folder)

    # listen for DMX512 values in the specified universe
    dmx_monitor = DMX512Monitor(args.universe, DMX)
    dmx_monitor.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bye!")
