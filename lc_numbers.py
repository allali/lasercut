#!/usr/bin/python

import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
from simplestyle import *

import simpletransform

import lc
import re

class GridNumbersEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--width', action = 'store',
          type = 'int', dest = 'width', default = '5',
          help = 'width')
        self.OptionParser.add_option('--height', action = 'store',
          type = 'int', dest = 'height', default = '5',
          help = 'height')
        self.OptionParser.add_option('--widthsep', action = 'store',
          type = 'float', dest = 'widthsep', default = '5',
          help = 'width sep')
        self.OptionParser.add_option('--heightsep', action = 'store',
          type = 'float', dest = 'heightsep', default = '5',
          help = 'height sep')
        self.OptionParser.add_option('--fontsize', action = 'store',
          type = 'int', dest = 'fontsize', default = '6',
          help = 'font size')
        self.OptionParser.add_option('--fmtstr', action = 'store',
          type = 'string', dest = 'fmtstr', default = "(%s,%s)",
          help = 'format string')
        self.OptionParser.add_option('--unit', action = 'store',
          type = 'string', dest = 'unit', default = 'mm',
          help = 'unit')

    def effect(self):
        width     = self.options.width
        height    = self.options.height
        widthsep  = self.unittouu(str(self.options.widthsep)+self.options.unit)
        heightsep = self.unittouu(str(self.options.heightsep)+self.options.unit)
        g = inkex.etree.SubElement(self.current_layer, 'g', {})
        style = formatStyle({ 'stroke': '#000000', \
                              'fill': 'none', \
                              'font-size' : str(self.options.fontsize)+"px", \
                              'stroke-width': str(self.unittouu('0.1mm')), \
                              'text-anchor' : 'middle'  })

        x = 0; y = 0
        for i in range(height):
            for j in range(width):
                t = self.options.fmtstr % (i+1,j+1)
                lc.insert_text(g, (x,y), t, style)
                x += widthsep
            y += heightsep
            x = 0

effect = GridNumbersEffect()
effect.affect()
