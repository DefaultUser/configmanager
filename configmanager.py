# -*. codig: utf-8 -*-

# Config Manager build on top of python's standard configparser
# Copyright (C) <2015>  <Sebastian Schmidt>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
if sys.version_info < (3, 0, 0):
    from ConfigParser import *
else:
    from configparser import *
import re


class ConfigManager(ConfigParser, object):
    """Config Manager build on top of the standard ConfigParser for a single
    config file"""

    # change regex patterns so that delimiters are not fixed (py2)
    _TMPL_SECT = r'\[(?P<header>[^]]+)\]'
    _TMPL_OPT = r'(?P<option>.*?)\s*(?P<vi>{0})\s*(?P<value>.*)$'
    _TMPL_OPT_NV = r'(?P<option>.*?)\s*(?:(?P<vi>{0})\s*(?P<value>.*))?$'

    def __init__(self, path, delimiters=("=", ":")):
        # only change the regex for python 2
        if sys.version_info < (3, 0, 0):
            d = "|".join(re.escape(d) for d in delimiters)
            self.SECTCRE = re.compile(self._TMPL_SECT)
            self.OPTCRE = re.compile(self._TMPL_OPT.format(d))
            self.OPTCRE_NV = re.compile(self._TMPL_OPT_NV.format(d))
            super(ConfigManager, self).__init__()
        else:
            super(ConfigManager, self).__init__(delimiters=delimiters)
        self._filepath = path
        self.read()

    def read(self):
        """Clear the current state and read again"""
        self._sections = self._dict()
        self._defaults = self._dict()
        super(ConfigManager, self).read(self._filepath)

    def option_set(self, section, option):
        """Check if the option exists and is set"""
        if not self.has_option(section, option):
            return False
        return True if self.get(section, option) else False

    def write(self):
        with open(self._filepath, "w") as f:
            super(ConfigManager, self).write(f)

    def set(self, section, option, value=None):
        self.read()
        if section not in self.sections():
            self.add_section(section)
        super(ConfigManager, self).set(section, option, str(value))
        self.write()

    def add_to_list(self, section, option, value=None):
        """Add a new value to a list"""
        if not self.has_section(section):
            self.add_section(section)
        if self.option_set(section, option):
            l = self.getlist(section, option)
            if str(value) in l:
                return
            l.append(value)
            value = l
        self.set(section, option, str(value))

    def getlist(self, section, option, vtype=str):
        """Return option as a list of userdefined type"""
        l = self.get(section, option).strip("[]").split(",")
        for i, val in enumerate(l):
            l[i] = vtype(val.strip("'\" "))
        return l
