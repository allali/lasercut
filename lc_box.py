import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
from simplestyle import *

import lc


class PlateJoinEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('-w', '--width', action = 'store',
          type = 'float', dest = 'width', default = '10',
          help = 'width')
        self.OptionParser.add_option('-o', '--iwidth', action = 'store',
          type = 'inkbool', dest = 'iwidth', default = 'True',
          help = 'inner width')
        self.OptionParser.add_option('-p', '--height', action = 'store',
          type = 'float', dest = 'height', default = '10',
          help = 'height')
        self.OptionParser.add_option('-l', '--iheight', action = 'store',
          type = 'inkbool', dest = 'iheight', default = 'True',
          help = 'inner height')
        self.OptionParser.add_option('-t', '--thickness', action = 'store',
          type = 'float', dest = 'thickness', default = '3',
          help = 'thickness')
        self.OptionParser.add_option('--bottom', action = 'store',
          type = 'string', dest = 'bottom', default = 'm',
          help = 'bottom type')
        self.OptionParser.add_option('--bottomshift', action = 'store',
          type = 'inkbool', dest = 'bottomshift', default = 'False',
          help = 'bottom shift')
        self.OptionParser.add_option('--right', action = 'store',
          type = 'string', dest = 'right', default = 'm',
          help = 'right type')
        self.OptionParser.add_option('--rightshift', action = 'store',
          type = 'inkbool', dest = 'rightshift', default = 'False',
          help = 'right shift')
        self.OptionParser.add_option('--top', action = 'store',
          type = 'string', dest = 'top', default = 'm',
          help = 'top type')
        self.OptionParser.add_option('--topshift', action = 'store',
          type = 'inkbool', dest = 'topshift', default = 'False',
          help = 'top shift')
        self.OptionParser.add_option('--left', action = 'store',
          type = 'string', dest = 'left', default = 'm',
          help = 'left type')
        self.OptionParser.add_option('--leftshift', action = 'store',
          type = 'inkbool', dest = 'leftshift', default = 'False',
          help = 'left shift')
        self.OptionParser.add_option('-s', '--wsplit', action = 'store',
          type = 'int', dest = 'wsplit', default = '3',
          help = 'horizontal splite')
        self.OptionParser.add_option('-m', '--hsplit', action = 'store',
          type = 'int', dest = 'hsplit', default = '3',
          help = 'vertical splite')
        self.OptionParser.add_option('-u', '--unit', action = 'store',
          type = 'string', dest = 'unit', default = 'mm',
          help = 'unit')
        
    def effect(self):
        width = self.unittouu(str(self.options.width)+self.options.unit)
        height = self.unittouu(str(self.options.height)+self.options.unit)
        thickness = self.unittouu(str(self.options.thickness)+self.options.unit)

        # Create main element
        t = 'translate(' + str(self.view_center[0]) + ',' + \
            str(self.view_center[1]) + ')'
        g_attribs = {
            inkex.addNS('label', 'inkscape'): 'Box' + str(width) + "x"+str(height),
            'transform': t}
        g = inkex.etree.SubElement(self.current_layer, 'g', g_attribs)
        style = {'stroke': '#000000',
                 'fill': 'none',
                 'stroke-width': str(self.unittouu('1px'))}

        # Create path
        points=lc.make_plate((width,height),
                             (self.options.iwidth,self.options.iheight),
                             thickness,self.options.wsplit,self.options.hsplit,
                             self.options.bottom,self.options.bottomshift,
                             self.options.top,self.options.topshift,
                             self.options.left,self.options.leftshift,
                             self.options.right,self.options.rightshift)

        path = lc.points_to_svgd(points)

        
        # Create SVG Path for plate
        box_attribs = {
            'style': formatStyle(style),
            'd': path}
        box = inkex.etree.SubElement(
            g, inkex.addNS('path', 'svg'), box_attribs)    
        
effect = PlateJoinEffect()
effect.affect()
