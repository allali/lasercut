
import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
from simplestyle import *

import lc


class HolesEffect(inkex.Effect):    
    def __init__(self):
        inkex.Effect.__init__(self)        
        self.OptionParser.add_option('--length', action = 'store',
          type = 'float', dest = 'length', default = '10',
          help = 'length')        
        self.OptionParser.add_option('--split', action = 'store',
          type = 'int', dest = 'split', default = '3',
          help = 'horizontal splite')
        self.OptionParser.add_option('--thickness', action = 'store',
          type = 'float', dest = 'thickness', default = '3',
          help = 'thickness')
        self.OptionParser.add_option('--gap', action = 'store',
          type = 'float', dest = 'gap', default = '3',
          help = 'thickness')
        self.OptionParser.add_option('--unit', action = 'store',
          type = 'string', dest = 'unit', default = 'mm',
          help = 'unit')        
        self.OptionParser.add_option('--vertical', action = 'store',
          type = 'inkbool', dest = 'vertical', default = 'False',
          help = 'unit')        
    def effect(self):
        length=self.unittouu(str(self.options.length)+self.options.unit)
        thickness=self.unittouu(str(self.options.thickness)+self.options.unit)
        gap=self.unittouu(str(self.options.gap)+self.options.unit)
             
        split=self.options.split * 2+1

        step=length/split
        
        t = 'translate(' + str(self.view_center[0]) + ',' + \
            str(self.view_center[1]) + ')'
        g_attribs = {
            inkex.addNS('label', 'inkscape'): 'Holes' + str(length) + "/"+str(split),
            'transform': t}
        g = inkex.etree.SubElement(self.current_layer, 'g', g_attribs)

        # Create SVG Path for plate
        style = {'stroke': '#000000', 'fill': 'none', 'stroke-width': str(self.unittouu('1px'))}

        # draw the line
        points=[(0,0),(length,0)]
        if self.options.vertical: points=[(b,a) for (a,b) in points]
        path = lc.points_to_svgd(points)        
        
        box_attribs = {
            'style': formatStyle(style),
            'd': path}
        box = inkex.etree.SubElement(
            g, inkex.addNS('path', 'svg'), box_attribs)

        # draw the holes
        y=gap
        x=step
        while x<length:
            points=[(x,y),(x,y+thickness),(x+step,y+thickness),(x+step,y),(x,y)]
            if self.options.vertical: points=[(b,a) for (a,b) in points]
            path = lc.points_to_svgd(points)                
            box_attribs = {
                'style': formatStyle(style),
                'd': path}
            box = inkex.etree.SubElement(
                g, inkex.addNS('path', 'svg'), box_attribs)
            x+=step*2
            

effect = HolesEffect()
effect.affect()
