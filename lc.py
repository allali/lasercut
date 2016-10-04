#!/usr/bin/python
import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
import math

################################################################
# Create a crenelated plate (face for a box)
#
# width, height   : dimensions of the plate
# iwidth, iheight : boolean for inner dimension
# thickness       : dimension for the thickness
# wsplit, hsplit  : number of crenellations
# bottom, top, left, right                     : either 'm', 'f' or '-'
# bottomshift, topshift, leftshift, rightshift : boolean for parity
#
# Returns a list of points
def make_plate(dims, idims,\
               thickness,wsplit,hsplit,\
               bottom,bottomshift,top,topshift,\
               left,leftshift,right,rightshift):
    (width, height)   = dims
    (iwidth, iheight) = idims

    wsplit=wsplit * 2 + 1
    hsplit=hsplit * 2 + 1

    if iwidth==False:
        width-=thickness*2
    if iheight==False:
        height-=thickness*2

    wstep=width/wsplit
    hstep=height/hsplit
    points= [] # the list of points returned
    x=0
    y=0
    direction = 1

    if bottom in "f":
        direction=-1
        y=thickness

    if bottomshift:
        y+=thickness
    if leftshift:
        x-=thickness

    # Draw bottom part
    if bottom=='-':
        points.append((x,y))
        x+=wsplit*wstep
        if leftshift:
            x+=thickness
        if rightshift:
            x+=thickness
        points.append((x,y))
    else:
        for i in range(wsplit):
            points.append((x,y))
            if i==0 and leftshift:
                x=x+wstep+thickness
            elif i==wsplit-1 and rightshift:
                x=x+wstep+thickness
            else:
                x=x+wstep
            points.append((x,y))
            if ((bottom != 'w') and (bottom != 'x')) or \
               ((bottom == 'w') and ((i/2)%2 == 0)) or \
               ((bottom == 'x') and ((i/2)%2 == 1)):
                y=y+direction*thickness
            direction*=-1
        if ((bottom != 'w') and (bottom != 'x')) or \
           ((bottom == 'x') and (wsplit % 4 == 3)) or \
           ((bottom == 'w') and (wsplit % 4 == 1)):
            y=y+direction*thickness
    if (right == bottom):
        direction*=-1

    # Draw right part
    if (bottom=='-'):
        if right=='f':
            direction=-1
        else:
            direction=1
    if right == '-':
        points.append((x,y))
        y=y-hstep*hsplit
        if bottomshift:
            y-=thickness
        if topshift:
            y-=thickness
        points.append((x,y))
    else:
        for i in range(hsplit):
            points.append((x,y))
            if i==0 and bottomshift:
                y=y-hstep-thickness
            elif i==hsplit-1 and topshift:
                y=y-hstep-thickness
            else:
                y=y-hstep
            points.append((x,y))
            x=x+direction*thickness
            direction*=-1
        x=x+direction*thickness
    if top != right:
        direction*=-1
    if right=='-':
        if top=='m':
            direction=-1
        else:
            direction=1

    # Draw top part
    if top == '-':
        points.append((x,y))
        x=x-wstep*wsplit
        if rightshift:
            x-=thickness
        if leftshift:
            x-=thickness
        points.append((x,y))
    else:
        for i in range(wsplit):
            points.append((x,y))
            if i==0 and rightshift:
                x=x-wstep-thickness
            elif i==wsplit-1 and leftshift:
                x=x-wstep-thickness
            else:
                x=x-wstep
            points.append((x,y))
            if ((top != 'w') and (top != 'x')) or \
               ((top == 'w') and ((i/2)%2 == (1-(wsplit/2)%2))) or \
               ((top == 'x') and ((i/2)%2 == ((wsplit/2)%2))):
                y=y+direction*thickness
            direction*=-1
        y=y+direction*thickness
    if left == top:
        direction*=-1

    # Draw left part
    if top=='-':
        if left=='m':
            direction=-1
        else:
            direction=1
    if left == '-':
        points.append((x,y))
        y=y+hstep*hsplit
        if topshift:
            y+=thickness
        if bottomshift:
            y+=thickness
        points.append((x,y))
    else:
        for i in range(hsplit):
            points.append((x,y))
            if i==0 and topshift:
                y=y+hstep+thickness
            elif i==hsplit-1 and bottomshift:
                y=y+hstep+thickness
            else:
                y=y+hstep
            points.append((x,y))
            x=x+direction*thickness
            direction*=-1

    return points

################################################################
def translate_points(p,x,y):
    return [(a+x,b+y) for (a,b) in p]

################################################################
# Transform a list of coordinates into an acceptable path
def points_to_svgd(ps):
    """
    ps: list of 2 tuples (x, y coordinates)
    """
    f = ps[0]
    p = ps[1:]
    svgd = 'M%.3f,%.3f' % f
    for x in ps:
        svgd += 'L%.3f,%.3f' % x
    return svgd

################################################################
# Insert a circular point into the SVG elem
def insert_point(elem, p, style):
    path = points_to_svgd([(p[0]+5,p[1]+5),
                           (p[0]+5,p[1]-5),
                           (p[0]-5,p[1]-5),
                           (p[0]-5,p[1]+5),
                           (p[0]+5,p[1]+5)])
    box_attribs = {
        'style': style,
        'd': path}
    box = inkex.etree.SubElement(
        elem, inkex.addNS('path', 'svg'), box_attribs)

################################################################
# Insert a circular point into the SVG elem
def insert_text(elem, p, s, style):
    text = inkex.etree.Element(inkex.addNS('text','svg'))
    text.text = s
    text.set('x', str(p[0]))
    text.set('y', str(p[1]))
    text.set('style', style)
    elem.append(text)

################################################################
# Insert a path into the SVG elem
def insert_path(elem, ps, style):
    path = points_to_svgd(ps)
    box_attribs = {
        'style': style,
        'd': path}
    # for p in ps:
    #     insert_point(elem, p, style)
    box = inkex.etree.SubElement(
        elem, inkex.addNS('path', 'svg'), box_attribs)

################################################################
# Insert a full box into the SVG elem
def insert_box(elem, dims, splits, thickness, innerDim, closeBox, style):
    (width, depth, height) = dims
    (wsplit,dsplit,hsplit) = splits

    ################################################################
    # make bottom plate:
    points=make_plate((width,depth),(innerDim,innerDim),
                      thickness,wsplit,dsplit,
                      'm',False,
                      'm',False,
                      'm',False,
                      'm',False)

    insert_path(elem, points, style)

    ################################################################
    # make top plate (only if closeBox)
    if (closeBox):
        points=make_plate((width,depth),(innerDim,innerDim),
                          thickness,wsplit,dsplit,
                          'm',False,
                          'm',False,
                          'm',False,
                          'm',False)

        dx = width+2*thickness if innerDim else width
        dy = depth+2*thickness if innerDim else depth
        points=translate_points(points,dx,dy)
        insert_path(elem, points, style)

    ################################################################
    # make back plate:
    points=make_plate((width,height if innerDim else height+thickness),
                      (innerDim,innerDim),
                      thickness,wsplit,hsplit,
                      'f',True,
                      'f' if closeBox else '-',closeBox,
                      'f',True,
                      'm',False)
    dy = -(depth+2*thickness) if innerDim else -depth
    points=translate_points(points,0,dy)
    insert_path(elem, points, style)

    ################################################################
    # make front plate:
    points=make_plate((width,height if innerDim else height+thickness),
                      (innerDim,innerDim),
                      thickness,wsplit,hsplit,
                      'f' if closeBox else '-',closeBox,
                      'f',True,
                      'm',False,
                      'f',True)
    dy = height if innerDim else height-thickness
    if closeBox==False: # strange translation correction for this plate
        dy += thickness
    points=translate_points(points,0,dy)
    insert_path(elem, points, style)

    ################################################################
    # make left plate:
    points=make_plate((height if innerDim else height+thickness,depth),
                      (innerDim,innerDim),
                      thickness,hsplit,dsplit,
                      'f',True,
                      'm',False,
                      'f' if closeBox else '-',closeBox,
                      'f',True)
    dx = -height-thickness if innerDim else -height
    points=translate_points(points,dx,-thickness)
    insert_path(elem, points, style)

    ################################################################
    # make right plate:
    points=make_plate((height if innerDim else height+thickness,depth),
                      (innerDim,innerDim),
                      thickness,hsplit,dsplit,
                      'm',False,
                      'f',True,
                      'f',True,
                      'f' if closeBox else '-',closeBox)
    dx = width+thickness if innerDim else width-thickness
    points=translate_points(points,dx,0)
    insert_path(elem, points, style)

################################################################
# Insert holes
#
# dx  : width of the holes
# dy  : thickness of the holes
# dir : 'n', 's', 'e', 'w'
def insert_holes(elem, (x,y), (dx,dy),
                 num, dir, style):
    for i in range(num):
        points=[(x-dx/2,y-dy/2),(x+dx/2,y-dy/2),
                (x+dx/2,y+dy/2),(x-dx/2,y+dy/2),
                (x-dx/2,y-dy/2)]
        insert_path(elem, points, style)
        if dir == 'n':
            y += dy*2
        elif dir == 's':
            y -= dy*2
        elif dir == 'e':
            x += dx*2
        elif dir == 'w':
            x -= dx*2
        else:
            raise Exception("lc.insert_holes : Impossible direction (" + str(dir) + ")")

################################################################
# Simple tree class that contains polygons / rectangles on the nodes
class Tree:
    def add_child(self, child):
        self.children.append(child)

    def in_border(self, point):
        for i in range(len(self.contents)):
            (p,q) = (self.contents[i],self.contents[i-1])

class Edge:
    def __init__(self, p_from, p_to, bnd=False):
        self.p_from = p_from # From point geometrically
        self.p_to   = p_to   # To   point geometrically
        self.r_from = None   # Real from of the edge on the plate
        self.r_to   = None   # Real to   of the edge on the plate
        self.dir    = '?'    # Dir in [nsew]
        self.bnd    = bnd    # Is it a border edge ?
        self.touch  = []     # Edges on the extremities
        self.attch  = []     # Other edges touching this one

    def touche(self, e, d):
        self.touch.append((e, d))
    def attach(self, p):
        self.attch.append(p)

    def position(self, p, dir):
        self.r_from = p
        self.dir = dir
        if dir == 'n':
            self.r_to = (self.r_from[0], self.r_from[1]-self.getlen())
        elif dir == 's':
            self.r_to = (self.r_from[0], self.r_from[1]+self.getlen())
        elif dir == 'e':
            self.r_to = (self.r_from[0]+self.getlen(), self.r_from[1])
        elif dir == 'w':
            self.r_to = (self.r_from[0]-self.getlen(), self.r_from[1])
        else:
            raise Exception("lc.edge.position : Impossible direction (" + str(dir) + ")")

    # Test if a point belongs to an edge
    def belongs(self, p):
        v1 = [p[0]-self.p_from[0],p[1]-self.p_from[1]]
        v2 = [self.p_to[0]-self.p_from[0],self.p_to[1]-self.p_from[1]]
        pv = abs(v1[0]*v2[1]-v1[1]*v2[0]) < 0.1
        if pv:
            do = self.distorig(p)
            return (do > 0) and (do < 1)
        else:
            return False

    # Get distance from origin of touching edge
    def distorig(self, p):
        v1  = [p[0]-self.p_from[0],p[1]-self.p_from[1]]
        nv1 = (v1[0]**2. + v1[1]**2.)**0.5
        v2  = [self.p_to[0]-self.p_from[0],self.p_to[1]-self.p_from[1]]
        nv2 = (v2[0]**2. + v2[1]**2.)**0.5
        if (v1[0]*v2[0] + v1[1]*v2[1] < 0):
            return -nv1/nv2
        else:
            return nv1/nv2

    # Get the direction of the edge in [nsew]
    def getdir(self):
        if (abs(self.p_from[0] - self.p_to[0]) < 0.01):
            if (self.p_from[1] > self.p_to[1]):
                dir = 's'
            else:
                dir = 'n'
        else:
            if (self.p_from[0] > self.p_to[0]):
                dir = 'w'
            else:
                dir = 'e'
        return dir

    def getlen(self):
        n = (self.p_from[0]-self.p_to[0])**2 + \
            (self.p_from[1]-self.p_to[1])**2
        return (n**0.5)

    def __str__(self):
        st = "Edge from " + str(self.p_from) + " to " + str(self.p_to)
        if self.r_from:
            st += ", at " + str(self.r_from) + " dir=" + self.dir
        if len(self.touch) > 0:
            st += ", touch [" + ", ".join(map(lambda (e,d): e.str_short(), self.touch)) + "]"
        if len(self.attch) > 0:
            st += ", attach [" + ", ".join(map(str, self.attch)) + "]"
        return st

    def str_short(self):
        st = "Edge from " + str(self.p_from) + " to " + str(self.p_to)
        st += ")"
        return st

def rotatedir(c):
    switcher = {
        'n':'w',
        'w':'s',
        's':'e',
        'e':'n'
    }
    return switcher.get(c, '?')

def decompose(es):
    # Remove additional information from the path
    qs = map(lambda e: (filter(lambda f: len(f) == 2,
                               map(lambda f: f[1], e))),
             es)
    edges = [] # List of edges to be returned

    # Find border
    tops = filter(lambda s: len(s) > 2, qs)
    assert (len(tops) == 1), "Should be only one border"
    bb = tops[0]
    xs = map(lambda x: x[0], bb)
    (xmin,xmax) = (min(xs),max(xs))
    ys = map(lambda x: x[1], bb)
    (ymin,ymax) = (min(ys),max(ys))
    # Create border edges (nsew)
    ne = Edge((xmin,ymax),(xmax,ymax),True)
    edges.append(ne)
    se = Edge((xmax,ymin),(xmin,ymin),True)
    edges.append(se)
    ee = Edge((xmax,ymax),(xmax,ymin),True)
    edges.append(ee)
    we = Edge((xmin,ymin),(xmin,ymax),True)
    edges.append(we)

    # Attach the edges in an acceptable order
    svgs = filter(lambda s: len(s) == 2, qs)
    while len(svgs) > 0:
        e  = svgs[0]
        newe = Edge((e[0][0],e[0][1]),(e[1][0],e[1][1]))
        for f in edges:
            if f.belongs(e[0]):
                newe.touche(f, f.distorig(e[0]))
                f.attach(e[0])
            if f.belongs(e[1]):
                newe.touche(f, f.distorig(e[1]))
                f.attach(e[1])
        edges.append(newe)
        svgs.pop(0)

    # for e in edges:
    #     print e

    return(edges)


################################################################
if __name__ == '__main__':
    # print make_plate((3,2),(True,True),
    #                   0.5,2,2,
    #                   'm',False,
    #                   'm',False,
    #                   'm',False,
    #                   'm',False)
   # decompose([[['M', [-734.28571, 118.07649]], ['L', [-220.0, 118.07649]], ['L', [-220.0, 589.50506]], ['L', [-734.28571, 589.50506]], ['Z', []]], [['M', [-431.42857, 118.07649]], ['L', [-431.42857, 589.50506]]]])
   decompose([[['M', [-662.85714, 183.79077]], ['L', [-662.85714, 866.6479200000001]]], [['M', [-1194.2856, 183.79077]], ['L', [-377.1428199999999, 183.79077]], ['L', [-377.1428199999999, 866.64789]], ['L', [-1194.2856, 866.64789]], ['Z', []]]])
