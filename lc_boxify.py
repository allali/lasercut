import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
from simplestyle import *

import ink2canvas.svg
import simpletransform
import simplepath
import random
import lc

class BoxifyEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--thickness', action = 'store',
          type = 'float', dest = 'thickness', default = '3',
          help = 'thickness')
        self.OptionParser.add_option('--height', action = 'store',
          type = 'float', dest = 'height', default = '3',
          help = 'height')
        self.OptionParser.add_option('--iheight', action = 'store',
          type = 'float', dest = 'iheight', default = '3',
          help = 'interior height')
        self.OptionParser.add_option('--unit', action = 'store',
          type = 'string', dest = 'unit', default = 'mm',
          help = 'unit')

    def effect(self):
        thickness=self.unittouu(str(self.options.thickness)+self.options.unit)
        height=self.unittouu(str(self.options.height)+self.options.unit)
        iheight=self.unittouu(str(self.options.iheight)+self.options.unit)
        if len(self.options.ids)!=1:
            print >> sys.stderr,"you must select exactly one object"
            return
        id=self.options.ids[0]
        node=self.selected[id]                   # Element
        (xmin,xmax,ymin,ymax)=simpletransform.computeBBox([node]) # Tuple
        width=xmax-xmin
        depth=ymax-ymin
        nodes=[]
        if (node.tag == inkex.addNS('path','svg')):
            nodes = [simplepath.parsePath(node.get('d'))]
        if (node.tag == inkex.addNS('g','svg')):
            nodes = []
            for n in node.getchildren():
                if (n.tag == inkex.addNS('rect','svg')):
                    x = float(n.get('x'))
                    y = float(n.get('y'))
                    h = float(n.get('height'))
                    w = float(n.get('width'))
                    nodes.append([['M', [x,y]],['L', [x+w,y]],['L', [x+w,y+h]],['L', [x,y+h]]])
                else:
                    nodes.append(simplepath.parsePath(n.get('d')))

        # inkex.debug(nodes)
        if (nodes == []):
            print >> sys.stderr,"selected object must be a path or a group of paths"
            return

        # Create main SVG element
        tr= 'translate(' + str(xmin+thickness) + ',' + str(ymax-thickness) + ')'
        g_attribs = {
            inkex.addNS('label', 'inkscape'): 'Boxify' + str(width) + \
            "x" + str(height) , 'transform': tr }
        g = inkex.etree.SubElement(self.current_layer, 'g', g_attribs)

        # Create SVG Path for plate
        style = formatStyle({ 'stroke': '#000000', \
                              'fill': 'none', \
                              'stroke-width': str(self.unittouu('1px')) })

        # Create main box
        vdivs = max(int(height/(2*thickness))-1,1)
        lc.insert_box(g,
                      (width, depth, height),
                      (int(width/(2*thickness)),
                       int(depth/(2*thickness)),
                       vdivs),
                      thickness, False, False, style)

        # Insert remaining edges
        # inkex.debug(nodes)
        edges = lc.decompose(nodes)

        # Position border edges (*after* having translated)
        e = edges.pop(0);
        e.position((xmax-xmin-thickness,0),'w')
        e = edges.pop(0);
        e.position((-thickness,ymin-ymax+2*thickness),'e')
        e = edges.pop(0);
        e.position((xmax-xmin-2*thickness,ymin-ymax+thickness),'s')
        e = edges.pop(0);
        e.position((0,thickness),'n')

        # Handle remaining edges
        numedges = 0
        for e in edges:
            # inkex.debug("==========================")
            # inkex.debug(str(e) + "\n")
            # style = formatStyle({ 'stroke': "#%06x" % random.randint(0, 0xFFFFFF), \
            #                       'fill': 'none', \
            #                       'stroke-width': str(self.unittouu('3px')) })
            numedges += 1

            # Determine edge direction in the main plate
            dir = e.getdir()

            # Middle holes
            leng = e.getlen()
            for (f,df) in e.touch:
                if not(f.bnd):
                    leng += thickness/2

            num  = int((leng-2*thickness)/(2*thickness))

            if (dir == 's') or (dir == 'n'): # Vertical edge
                dims = (thickness,(leng-2*thickness)/(2*num+1))
                if (dir == 's'):
                    st = (e.p_from[0]-xmin-thickness,
                          e.p_from[1]-ymax-dims[1]/2+thickness)
                else:
                    st = (e.p_from[0]-xmin-thickness,
                          e.p_from[1]-ymax+2*thickness+dims[1]/2)
                if not((abs(e.p_from[1]-ymin) < 0.1) or
                       (abs(e.p_from[1]-ymax) < 0.1)): # Is the start point on the border ?
                    st = (st[0],st[1]-thickness/2)
                else:
                    st = (st[0],st[1])
            else: # Horizontal edge
                dims = ((leng-2*thickness)/(2*num+1),thickness)
                if (dir == 'e'):
                    st = (e.p_from[0]-xmin+dims[0]/2,
                          e.p_from[1]-ymax+thickness)
                else:
                    st = (e.p_from[0]-xmin-2*thickness-dims[0]/2,
                          e.p_from[1]-ymax+thickness)
                if not((abs(e.p_from[0]-xmin) < 0.1) or
                       (abs(e.p_from[0]-xmax) < 0.1)): # Is the start point on the border ?
                    if (dir == 'e'):
                        st = (st[0]-thickness/2,st[1])
                    else:
                        st = (st[0]+thickness/2,st[1])

            lc.insert_holes(g, st, dims, num+1, dir, style)

            # Do we need to split the joins of the edge ?
            tm_from = 0; tm_to = 0
            for (f,df) in e.touch:
                tm_from += len(filter ((lambda q: ((q[0]-e.p_from[0])**2+(q[1]-e.p_from[1]))**2 < 0.1), f.attch))
                tm_to   += len(filter ((lambda q: ((q[0]-e.p_to[0])**2+(q[1]-e.p_to[1]))**2 < 0.1), f.attch))

            vdivs = max(int((height-iheight)/(2*thickness))-1,1)
            points=lc.make_plate((height-thickness-iheight,leng),(True,False),
                              thickness,vdivs,num,
                              'm' if tm_to   <= 1 else ('x' if (e.getdir() == 'w') or (e.getdir() == 'n') else 'w'),False,
                              'm' if tm_from <= 1 else ('x' if (e.getdir() == 'w') or (e.getdir() == 'n') else 'w'),False,
                              '-',False,
                              'f',True)
            (dpx,dpy) = (xmax-xmin-2*thickness+numedges*(height-iheight)+iheight,0)
            points = lc.translate_points(points,dpx,dpy)
            lc.insert_path(g, points, style)
            e.position((xmax-xmin+(height-iheight)*(numedges+1)+iheight-2*thickness,
                        thickness), 'n')

            # Left parts
            for (f,df) in e.touch:
                # inkex.debug("Touch " + str(f) + " -- DIST= " + str(df) + "\n")

                vdir = lc.rotatedir(f.dir)
                if (vdir == 's') or (vdir == 'n'):
                    xdim = thickness
                    ydim = (height-iheight-thickness)/(2*vdivs+1.)
                    dyf  = -2*thickness-3*ydim/2 if vdir == 'n' else +3*ydim/2
                    df   = 1-df
                    stf  = (f.r_from[0]+df*(f.r_to[0]-f.r_from[0]),
                            f.r_from[1]+df*(f.r_to[1]-f.r_from[1])+thickness+dyf)
                    vdir = 's' if vdir == 'n' else 'n'
                else:
                    ydim = thickness
                    xdim = (height-iheight-thickness)/(2*vdivs+1.)
                    df   = 1-df
                    dxf  = 2*thickness+3*xdim/2 if vdir == 'e' else -3*xdim/2
                    stf  = (f.r_from[0]+df*(f.r_to[0]-f.r_from[0])-thickness+dxf,
                            f.r_from[1]+df*(f.r_to[1]-f.r_from[1]))

                lc.insert_holes(g, stf, (xdim,ydim), vdivs, vdir, style)

effect = BoxifyEffect()
effect.affect()
