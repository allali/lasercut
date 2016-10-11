#!/usr/bin/python

import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
import urllib
import json
import os
import re
import tempfile
import zipfile
import shutil

from lc_version import __version__

class UpdateEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--tab', action = 'store',
                                     type = 'string', dest = 'what')

    def effect(self):
        f = urllib.urlopen("https://raw.github.com/renaultd/lasercut/" + \
                           "master/lc_version.py")
        j = f.read()
        if (re.match("__version__ = \([0-9]+,[0-9]+,[0-9]+\)\n",j)):
            vstr = re.findall("[a-z_]+ = \(([0-9]+),([0-9]+),([0-9]+)\)\n",j)[0]
            version = (int(vstr[0]),int(vstr[1]),int(vstr[2]))
            inkex.debug("Current version : " + str(version))
            inkex.debug("Most recent version : " + str(__version__))
            pwd = os.path.dirname(os.path.realpath(__file__))
            fd,zipn = tempfile.mkstemp()
            urllib.urlretrieve("https://api.github.com/repos/" + \
                               "renaultd/lasercut/zipball/", zipn)
            zip = zipfile.ZipFile(zipn)
            ms = [ m for m in zip.namelist() if re.match(".*\.(py|inx)",m) ]
            t = tempfile.mkdtemp()
            for m in ms:
                inkex.debug(m)
                zip.extract(m,t)
                shutil.copy(os.path.join(t,m), pwd)
            os.close(fd)
            os.remove(zipn)
            shutil.rmtree(t)
        else:
            inkex.debug("Unable to fetch distant repository")

effect = UpdateEffect()
effect.affect()
