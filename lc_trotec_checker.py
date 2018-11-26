#!/usr/bin/python

import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
from simplestyle import *

import PIL
from PIL import Image
import base64

import simpletransform

import lc
import re

import tempfile

# List of color codes used by Trotec
acceptable_colors=['#000000','#ff0000','#0000ff','#336699','#00ffff','#00ff00','#009933','#006633','#9900cc','#ff00ff','#ff6600','#ffff00','#999933','#996633','#663300','#660066']

class TrotecChecker(inkex.Effect):    
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--fixstroke', action = 'store',
                                     type = 'inkbool', dest = 'fixstroke', default = 'True',
                                     help = 'fix the stroke width')

        self.OptionParser.add_option('--stroke', action = 'store',
                                     type = 'float', dest = 'stroke', default = '0.1',
                                     help = 'stroke width in mm')
        self.OptionParser.add_option('--clippath', action = 'store',
                                     type = 'inkbool', dest = 'clippath', default = 'True',
                                     help = 'remove clippath from group')
        self.OptionParser.add_option('--fixtransparency', action = 'store',
                                     type = 'inkbool', dest = 'fixtransparency', default = 'True',
                                     help = 'remove transparency')
        self.OptionParser.add_option('--removefilter', action = 'store',
                                     type = 'inkbool', dest = 'removefilter', default = 'True',
                                     help = 'remove filter')
        
    def apply(self,node):
        if node.tag == inkex.addNS('image', 'svg') or node.tag == 'image':
            inkex.debug("image found! ")
            data=node.get(inkex.addNS('href','xlink'))            
            # must check image is embeded
            if data[:5]!='data:':
                inkex.debug("image is not embeded: we skip it!")
            else:
                i=data.find("image/")
                j=data.find(";")
                if i==-1 or j==-1:
                    inkex.debug("image data: failed to find image format!")
                else:
                    img_format=data[i+6:j]
                    img_data_header_pos=data.find(',')
                    img_data=base64.decodestring(data[img_data_header_pos+1:])
                    f=tempfile.NamedTemporaryFile(mode='w+b',suffix="."+img_format,delete=True)
                    f.write(img_data)
                    f.flush()
                    img=PIL.Image.open(f.name)
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        inkex.debug("image has an alpha channel... remove it!")
                        alpha = img.convert('RGBA').split()[-1] # get the alpha channel
                        bg = Image.new("RGB", img.size, (255,255,255)) # create the background
                        bg.paste(img, mask=alpha) # merge background and image
                        bg.show()
                        bg.save(f.name)
                        f.seek(0)
                        ndata=f.read()
                        ndata=base64.encodestring(ndata)
                        ndata=data[:img_data_header_pos]+','+ndata
                        node.set(inkex.addNS('href','xlink'),ndata)
                    f.close()
        if 'style' in node.attrib:
            style=node.get('style') 
            if style!='':
                styles=style.split(';')
                hasStroke=False
                hasFill=False
                for i in range(len(styles)):
                    s=styles[i]
                    v=s.split(':')[1]
                    if s.startswith("opacity"):
                        if float(v)!=1.0:
                            if self.options.fixtransparency:
                                styles[i]="opacity:1"
                                inkex.debug("INFO: opacity of value "+v+" fixed")
                            else:
                                inkex.debug("TODO: error with opacity of value "+v)
                    elif s.startswith("stroke:"):
                        if v!="none":                            
                            hasStroke=True
                            if v not in acceptable_colors:
                                inkex.debug("WANRING: suspicious stoke color:"+v)                            
                    elif s.startswith("fill:"):
                        if v!="none":
                            hasFill=True
                            if v not in acceptable_colors:
                                inkex.debug("WARNING: suspicious fill color:"+v)
                    elif s.startswith("fill-opacity"):
                        if float(v)!=1.0:
                            if self.options.fixtransparency:
                                styles[i]="fill-opacity:1"
                                inkex.debug("INFO: fill transparency fixed")
                            else:
                                inkex.debug("TODO: fill transparency issue")
                    elif s.startswith("stroke-opacity"):
                        if float(v)!=1.0:
                            if self.options.fixtransparency:
                                styles[i]="stoke-opacity:1"
                                inkex.debug("INFO: stoke transparency fixed")
                            else:
                                inkex.debug("TODO: stroke transparency issue")
                    elif s.startswith("filter"):
                        if self.options.removefilter:
                            styles[i]=""
                            inkex.debug("INFO: filter removed")
                        else:
                            inkex.debug("TODO: filter found, should be removed")
                    elif s.startswith("stroke-width:"):
                        if self.options.fixstroke:
                            styles[i]='stroke-width:'+str(self.strokewidth)
                if hasFill and hasStroke:
                    inkex.debug("WARNING: suspicious element that has both fill and stroke!")
                node.set('style',";".join(styles))

    def recursivelyTraverse(self,nodeList):
        result=[]
        for node in nodeList:
            #print(node,node.tag)
            # node is a group...
            if node.tag == inkex.addNS('g', 'svg') or node.tag == 'g':
                if node.get('clip-path')!=None:
                    if self.options.clippath:
                        del node.attrib['clip-path']
                        inkex.debug("INFO: a group have a clipping path: removed")
                    else:
                        inkex.debug("TODO: a group have a clipping path: you must remove it!")
                self.recursivelyTraverse(node)
            else:
                self.apply(node)
        return result
    
    def effect(self):
        self.strokewidth=self.unittouu(str(self.options.stroke)+'mm')
        self.recursivelyTraverse(self.document.getroot())        

effect=TrotecChecker()
effect.affect()
