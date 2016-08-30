import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
from simplestyle import *

import lc

class FullBoxEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--width', action = 'store',
          type = 'float', dest = 'width', default = '10',
          help = 'width')
        self.OptionParser.add_option('--depth', action = 'store',
          type = 'float', dest = 'depth', default = '10',
          help = 'depth')
        self.OptionParser.add_option('--height', action = 'store',
          type = 'float', dest = 'height', default = '10',
          help = 'height')
        self.OptionParser.add_option('--thickness', action = 'store',
          type = 'float', dest = 'thickness', default = '3',
          help = 'thickness')
        self.OptionParser.add_option('--wsplit', action = 'store',
          type = 'int', dest = 'wsplit', default = '3',
          help = 'number of horizontal splits')
        self.OptionParser.add_option('--dsplit', action = 'store',
          type = 'int', dest = 'dsplit', default = '3',
          help = 'number of depth splits')
        self.OptionParser.add_option('--hsplit', action = 'store',
          type = 'int', dest = 'hsplit', default = '3',
          help = 'number of vertical splits')
        self.OptionParser.add_option('--unit', action = 'store',
          type = 'string', dest = 'unit', default = 'mm',
          help = 'unit')
        self.OptionParser.add_option('--inner', action = 'store',
          type = 'inkbool', dest = 'inner', default = 'True',
          help = 'inner')
        self.OptionParser.add_option('--closebox', action = 'store',
          type = 'inkbool', dest = 'closebox', default = 'True',
          help = 'closebox')

    def effect(self):
        width=self.unittouu(str(self.options.width)+self.options.unit)
        depth=self.unittouu(str(self.options.depth)+self.options.unit)
        height=self.unittouu(str(self.options.height)+self.options.unit)
        thickness=self.unittouu(str(self.options.thickness)+self.options.unit)
        closeBox=self.options.closebox
        innerDim=self.options.inner

        # Create main SVG element
        tr= 'translate(' + str(self.view_center[0]) + ',' + \
            str(self.view_center[1]) + ')'
        g_attribs = {
            inkex.addNS('label', 'inkscape'): 'Box' + str(width) + "x"+str(height),
            'transform': tr }
        g = inkex.etree.SubElement(self.current_layer, 'g', g_attribs)

        # Create SVG Path for plate
        style = formatStyle({ 'stroke': '#000000', \
                              'fill': 'none', \
                              'stroke-width': str(self.unittouu('1px')) })

        lc.insert_box(g,
                      (width, depth, height), 
                      (self.options.wsplit,self.options.dsplit,self.options.hsplit),
                      thickness, innerDim, closeBox, style)

effect = FullBoxEffect()
effect.affect()
