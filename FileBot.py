# !/usr/bin/python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License,published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import os
import re
import glob
from os import listdir, access, X_OK, makedirs
from os.path import join, exists, basename

from module.plugins.Hook import Hook
from module.utils import save_join


class FileBot(Hook):
    __name__ = "FileBot"
    __version__ = "0.41"
    __config__ = [("activated", "bool", "Activated", "False"),

                  ("destination", "folder", "destination folder", ""),

                  ("conflict", """skip;override""", "conflict handling", "override"),

                  ("action", """move;copy;test""", "copy, move or test(dry run)", "move"),

                  ("lang", "str", "language (en, de, fr, es, etc)", "de"),

                  ("subtitles", "str", "subtitles language (en, de, fr, es, etc)", "de"),

                  ("ignore", "str", "ignore files (regex)", ""),

                  ("artwork", """y;n""", "download artwork", "y"),

                  ("clean", """y;n""", "clean folder from clutter thats left behind", "y"),

                  ("movie", "str", "movie destination (relative to destination or absolute)", ""),

                  ("series", "str", "series destination (relative to destination or absolute)", ""),

                  ("excludeList", "str", "exclude list file", "pyload-amc.txt"),

                  ("pushover", "str", "pushover user key", ""),

                  ("reperror", """y;n""", "Report Error via Email", "n"),

                  ("filebot", "str", "filebot executable", "filebot"),

                  ("exec", "str", "additional exec script", "")]

    __description__ = "Automated renaming and sorting for tv episodes movies, music and animes"
    __author_name__ = ("Branko Wilhelm", "Kotaro", "Gutz-Pilz")
    __author_mail__ = ("branko.wilhelm@gmail.com", "screver@gmail.com", "unwichtig@gmail.com")

    #event_list = ["packageFinished", "unrarFinished", "allDownloadsFinished"]
    event_map = {"packageFinished" : "package_startfb",
                 "unrarFinished": "unrar_startfb"}

    def package_startfb(self, pypack):
        folder = self.core.config['general']['download_folder']
        folder = save_join(folder, pypack.folder)
        x=0
        for root, dirs, files in os.walk(folder):
            for name in files:
                if (name.endswith((".avi", ".mkv"))) and x==0:
                    self.core.log.debug("Hier ist eine MKV")
                    x=+1
                    self.Finished(folder)
                else:
                    self.core.log.debug("Keine MKV!!!")

    def unrar_startfb(self, folder, fname):
        x=0
        for root, dirs, files in os.walk(folder):
            for name in files:
                if (name.endswith((".avi", ".mkv"))) and x==0:
                    self.core.log.debug("Hier ist eine MKV")
                    x=+1
                    self.Finished(folder)
                else:
                    self.core.log.debug("Keine MKV!!!")

    def Finished(self, folder):

        args = []

        if self.getConfig('filebot'):
            args.append(self.getConfig('filebot'))
        else:
            args.append('filebot')

        args.append('-script')
        args.append('fn:amc')

        args.append('-non-strict')

        args.append('--log-file')
        args.append('amc.log')

        args.append('-r')

        args.append('--conflict')
        args.append(self.getConfig('conflict'))

        args.append('--action')
        args.append(self.getConfig('action'))

        if self.getConfig('destination'):
            args.append('--output')
            args.append(self.getConfig('destination'))
        else:
            args.append('--output')
            args.append(folder)

        if self.getConfig('lang'):
            args.append('--lang')
            args.append(self.getConfig('lang'))

        # start with all definitions:
        args.append('--def')

        if self.getConfig('exec'):
            args.append('exec=' + self.getConfig('exec'))

        if self.getConfig('clean'):
            args.append('clean=' + self.getConfig('clean'))

        args.append('skipExtract=y')

        if self.getConfig('excludeList'):
            args.append('excludeList=' + self.getConfig('excludeList'))

        if self.getConfig('reperror'):
            args.append('reportError=' + self.getConfig('reperror'))

        if self.getConfig('artwork'):
            args.append('artwork=' + self.getConfig('artwork'))

        if self.getConfig('subtitles'):
            args.append('subtitles=' + self.getConfig('subtitles'))

        if self.getConfig('ignore'):
            args.append('ignore=' + self.getConfig('ignore'))

        if self.getConfig('pushover'):
            args.append('pushover=' + self.getConfig('pushover'))

        if self.getConfig('movie'):
            args.append('movieFormat=' + self.getConfig('movie'))

        if self.getConfig('series'):
            args.append('seriesFormat=' + self.getConfig('series'))

        args.append(folder)

        try:
            subprocess.Popen(args, bufsize=-1)
            self.logInfo('executed')
        except Exception, e:
            self.logError(str(e))
