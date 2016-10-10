import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
from simplestyle import *

import ink2canvas.svg
import simpletransform
import simplepath
import lc

class BoxifyEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--width', action = 'store',
          type = 'float', dest = 'width', default = '3',
          help = 'width')
        self.OptionParser.add_option('--height', action = 'store',
          type = 'float', dest = 'height', default = '3',
          help = 'height')
        self.OptionParser.add_option('--hsplit', action = 'store',
          type = 'int', dest = 'hsplit', default = '3',
          help = 'number of horizontal splits')
        self.OptionParser.add_option('--vsplit', action = 'store',
          type = 'int', dest = 'vsplit', default = '3',
          help = 'number of vertical splits')
        self.OptionParser.add_option('--overcut', action = 'store',
          type = 'float', dest = 'overcut', default = '3',
          help = 'overcut')
        self.OptionParser.add_option('--unit', action = 'store',
          type = 'string', dest = 'unit', default = 'mm',
          help = 'unit')

    def effect(self):
        width=self.unittouu(str(self.options.width)+self.options.unit)
        height=self.unittouu(str(self.options.height)+self.options.unit)
        hsplit=self.options.hsplit
        vsplit=self.options.vsplit
        overcut=self.unittouu(str(self.options.overcut)+self.options.unit)
        
        g_attribs = {
            inkex.addNS('label', 'inkscape'): 'Folding' + str(width) + \
            "x" + str(height) }
        g = inkex.etree.SubElement(self.current_layer, 'g',
                                   g_attribs)
        # Create SVG Path for plate
        style = formatStyle({ 'stroke': '#000000', \
                              'fill': 'none', \
                              'stroke-width': str(self.unittouu('1px')) })

        slen = height / (2*vsplit-1)
        if overcut > slen:
            overcut = slen
        
        for i in range(hsplit):
            x = i*width/(hsplit-1 if hsplit > 1 else 1)
            if (i % 2 == 0):
                for j in range(vsplit):
                    y = j*slen*2
                    l = [(x,(y - overcut if j > 0 else y)),
                         (x,(y + slen + overcut if j < (vsplit-1) else y+slen))]
                    lc.insert_path(g, l, style)
            else:
                for j in range(vsplit-1):
                    y = slen + 2*j*slen
                    l = [(x,y - overcut), (x,y+slen + overcut)]
                    lc.insert_path(g, l, style)        
        
effect = BoxifyEffect()
effect.affect()
