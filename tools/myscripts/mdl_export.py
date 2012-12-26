#!BPY

"""
Name: 'MDL (.mdl)'
Blender: 244
Group: 'Export'
Tooltip: 'Export to Quake file format (.mdl).'
"""

__author__ = 'Andrew Denner'
__version__ = '0.1.3'
__url__ = ["Andrew's site, http://www.btinternet.com/~chapterhonour/",
     "Can also be contacted through http://celephais.net/board", "blender", "elysiun"]
__email__ = ["Andrew Denner, andrew.denner:btinternet*com", "scripts"]
__bpydoc__ = """\
This script Exports a Quake 1 file (MDL).

Based wholesale off the MD2 export by Bob Holcomb, with the help of David Henry's MDL format guide
"""

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C): Andrew Denner(portions Bob Holcomb)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------


import Blender
from Blender import *
from Blender.Draw import *
from Blender.BGL import *
from Blender.Window import *

import struct, string
from types import *
from math import *



######################################################
# GUI Loader
######################################################

# Export globals
g_filename=Create("default.mdl")
g_frame_filename=Create("default")

g_filename_search=Create("")
g_frame_search=Create("default")


user_frame_list=[]

#Globals
g_scale=Create(1.0)
g_fixuvs=Create(0)
g_flags=Create(0)

# Events
EVENT_NOEVENT=1
EVENT_SAVE_MDL=2
EVENT_CHOOSE_FILENAME=3
EVENT_CHOOSE_FRAME=4
EVENT_EXIT=100

######################################################
# Callbacks for Window functions
######################################################
def filename_callback(input_filename):
	global g_filename
	g_filename.val=input_filename

def frame_callback(input_frame):
	global g_frame_filename
	g_frame_filename.val=input_frame

def draw_gui():
	global g_scale
	global g_fixuvs
	global g_flags
	global g_filename
	global g_frame_filename
	global EVENT_NOEVENT,EVENT_SAVE_MDL,EVENT_CHOOSE_FILENAME,EVENT_CHOOSE_FRAME,EVENT_EXIT


	########## Titles
	glClear(GL_COLOR_BUFFER_BIT)
	glRasterPos2d(10, 140)
	Text("MDL Export")

	######### Parameters GUI Buttons
	######### MDL Filename text entry
	g_filename = String("MDL file to save: ", EVENT_NOEVENT, 10, 75, 210, 18,
                            g_filename.val, 255, "MDL file to save")
	########## MDL File Search Button
	Button("Search",EVENT_CHOOSE_FILENAME,220,75,80,18)

	##########  MDL Frame List Text entry
	g_frame_filename = String("Frame List file to load: ", EVENT_NOEVENT, 10, 55, 210, 18,
                                g_frame_filename.val, 255, "Frame List to load-overrides MDL defaults")
	g_flags = Number("Model Flags", EVENT_NOEVENT, 10, 115, 210, 18,
                                g_flags.val, 0, 1<<15, "Specify the combination of flags you desire")
	########## Frame List Search Button
	Button("Search",EVENT_CHOOSE_FRAME,220,55,80,18)
	
	########## Scale slider-default is 1
	g_scale = Slider("Scale Factor: ", EVENT_NOEVENT, 10, 95, 210, 18,
                    g_scale.val, 0.001, 10.0, 1.0, "Scale factor for object Model");
        ########## Fix UVs options
	g_fixuvs = Menu("Fix UV coords %t|Don't Fix UVs%x0|Translate points %x1|Clamp points %x2",
                        EVENT_NOEVENT, 10, 35, 210, 18, g_fixuvs.val, "Method for handling UV's which are outside skin range")
	######### Draw and Exit Buttons
	Button("Export",EVENT_SAVE_MDL , 10, 10, 80, 18)
	Button("Exit",EVENT_EXIT , 170, 10, 80, 18)
	
	

def event(evt, val):	
	if (evt == QKEY and not val):
		Exit()

def bevent(evt):
	global g_filename
	global g_frame_filename
	global EVENT_NOEVENT,EVENT_SAVE_MDL,EVENT_EXIT

	######### Manages GUI events
	if (evt==EVENT_EXIT):
		Blender.Draw.Exit()
	elif (evt==EVENT_CHOOSE_FILENAME):
		FileSelector(filename_callback, "MDL File Selection")
	elif (evt==EVENT_CHOOSE_FRAME):
		FileSelector(frame_callback, "Frame Selection")
	elif (evt==EVENT_SAVE_MDL):
		if (g_filename.val == "model"):
			save_mdl("blender.mdl")
			Blender.Draw.Exit()
			return
		else:
			save_mdl(g_filename.val)
			Blender.Draw.Exit()
			return

Register(draw_gui, event, bevent)

######################################################
# MDL Model Constants
######################################################
MDL_MAX_TRIANGLES=2048
MDL_MAX_VERTICES=1024
MDL_MAX_TEXCOORDS=1024
MDL_MAX_FRAMES=256
MDL_MAX_SKINS=16
MDL_MAX_FRAMESIZE=(MDL_MAX_VERTICES * 4 + 128)

MDL_FRAME_NAME_LIST=(("stand",1,10)),
					#10 frames

#pretty sure these are the same					
MDL_NORMALS=((-0.525731, 0.000000, 0.850651), 
			(-0.442863, 0.238856, 0.864188), 
			(-0.295242, 0.000000, 0.955423), 
			(-0.309017, 0.500000, 0.809017), 
			(-0.162460, 0.262866, 0.951056), 
			(0.000000, 0.000000, 1.000000), 
			(0.000000, 0.850651, 0.525731), 
			(-0.147621, 0.716567, 0.681718), 
			(0.147621, 0.716567, 0.681718), 
			(0.000000, 0.525731, 0.850651), 
			(0.309017, 0.500000, 0.809017), 
			(0.525731, 0.000000, 0.850651), 
			(0.295242, 0.000000, 0.955423), 
			(0.442863, 0.238856, 0.864188), 
			(0.162460, 0.262866, 0.951056), 
			(-0.681718, 0.147621, 0.716567), 
			(-0.809017, 0.309017, 0.500000), 
			(-0.587785, 0.425325, 0.688191), 
			(-0.850651, 0.525731, 0.000000), 
			(-0.864188, 0.442863, 0.238856), 
			(-0.716567, 0.681718, 0.147621), 
			(-0.688191, 0.587785, 0.425325), 
			(-0.500000, 0.809017, 0.309017), 
			(-0.238856, 0.864188, 0.442863), 
			(-0.425325, 0.688191, 0.587785), 
			(-0.716567, 0.681718, -0.147621), 
			(-0.500000, 0.809017, -0.309017), 
			(-0.525731, 0.850651, 0.000000), 
			(0.000000, 0.850651, -0.525731), 
			(-0.238856, 0.864188, -0.442863), 
			(0.000000, 0.955423, -0.295242), 
			(-0.262866, 0.951056, -0.162460), 
			(0.000000, 1.000000, 0.000000), 
			(0.000000, 0.955423, 0.295242), 
			(-0.262866, 0.951056, 0.162460), 
			(0.238856, 0.864188, 0.442863), 
			(0.262866, 0.951056, 0.162460), 
			(0.500000, 0.809017, 0.309017), 
			(0.238856, 0.864188, -0.442863), 
			(0.262866, 0.951056, -0.162460), 
			(0.500000, 0.809017, -0.309017), 
			(0.850651, 0.525731, 0.000000), 
			(0.716567, 0.681718, 0.147621), 
			(0.716567, 0.681718, -0.147621), 
			(0.525731, 0.850651, 0.000000), 
			(0.425325, 0.688191, 0.587785), 
			(0.864188, 0.442863, 0.238856), 
			(0.688191, 0.587785, 0.425325), 
			(0.809017, 0.309017, 0.500000), 
			(0.681718, 0.147621, 0.716567), 
			(0.587785, 0.425325, 0.688191), 
			(0.955423, 0.295242, 0.000000), 
			(1.000000, 0.000000, 0.000000), 
			(0.951056, 0.162460, 0.262866), 
			(0.850651, -0.525731, 0.000000), 
			(0.955423, -0.295242, 0.000000), 
			(0.864188, -0.442863, 0.238856), 
			(0.951056, -0.162460, 0.262866), 
			(0.809017, -0.309017, 0.500000), 
			(0.681718, -0.147621, 0.716567), 
			(0.850651, 0.000000, 0.525731), 
			(0.864188, 0.442863, -0.238856), 
			(0.809017, 0.309017, -0.500000), 
			(0.951056, 0.162460, -0.262866), 
			(0.525731, 0.000000, -0.850651), 
			(0.681718, 0.147621, -0.716567), 
			(0.681718, -0.147621, -0.716567), 
			(0.850651, 0.000000, -0.525731), 
			(0.809017, -0.309017, -0.500000), 
			(0.864188, -0.442863, -0.238856), 
			(0.951056, -0.162460, -0.262866), 
			(0.147621, 0.716567, -0.681718), 
			(0.309017, 0.500000, -0.809017), 
			(0.425325, 0.688191, -0.587785), 
			(0.442863, 0.238856, -0.864188), 
			(0.587785, 0.425325, -0.688191), 
			(0.688191, 0.587785, -0.425325), 
			(-0.147621, 0.716567, -0.681718), 
			(-0.309017, 0.500000, -0.809017), 
			(0.000000, 0.525731, -0.850651), 
			(-0.525731, 0.000000, -0.850651), 
			(-0.442863, 0.238856, -0.864188), 
			(-0.295242, 0.000000, -0.955423), 
			(-0.162460, 0.262866, -0.951056), 
			(0.000000, 0.000000, -1.000000), 
			(0.295242, 0.000000, -0.955423), 
			(0.162460, 0.262866, -0.951056), 
			(-0.442863, -0.238856, -0.864188), 
			(-0.309017, -0.500000, -0.809017), 
			(-0.162460, -0.262866, -0.951056), 
			(0.000000, -0.850651, -0.525731), 
			(-0.147621, -0.716567, -0.681718), 
			(0.147621, -0.716567, -0.681718), 
			(0.000000, -0.525731, -0.850651), 
			(0.309017, -0.500000, -0.809017), 
			(0.442863, -0.238856, -0.864188), 
			(0.162460, -0.262866, -0.951056), 
			(0.238856, -0.864188, -0.442863), 
			(0.500000, -0.809017, -0.309017), 
			(0.425325, -0.688191, -0.587785), 
			(0.716567, -0.681718, -0.147621), 
			(0.688191, -0.587785, -0.425325), 
			(0.587785, -0.425325, -0.688191), 
			(0.000000, -0.955423, -0.295242), 
			(0.000000, -1.000000, 0.000000), 
			(0.262866, -0.951056, -0.162460), 
			(0.000000, -0.850651, 0.525731), 
			(0.000000, -0.955423, 0.295242), 
			(0.238856, -0.864188, 0.442863), 
			(0.262866, -0.951056, 0.162460), 
			(0.500000, -0.809017, 0.309017), 
			(0.716567, -0.681718, 0.147621), 
			(0.525731, -0.850651, 0.000000), 
			(-0.238856, -0.864188, -0.442863), 
			(-0.500000, -0.809017, -0.309017), 
			(-0.262866, -0.951056, -0.162460), 
			(-0.850651, -0.525731, 0.000000), 
			(-0.716567, -0.681718, -0.147621), 
			(-0.716567, -0.681718, 0.147621), 
			(-0.525731, -0.850651, 0.000000), 
			(-0.500000, -0.809017, 0.309017), 
			(-0.238856, -0.864188, 0.442863), 
			(-0.262866, -0.951056, 0.162460), 
			(-0.864188, -0.442863, 0.238856), 
			(-0.809017, -0.309017, 0.500000), 
			(-0.688191, -0.587785, 0.425325), 
			(-0.681718, -0.147621, 0.716567), 
			(-0.442863, -0.238856, 0.864188), 
			(-0.587785, -0.425325, 0.688191), 
			(-0.309017, -0.500000, 0.809017), 
			(-0.147621, -0.716567, 0.681718), 
			(-0.425325, -0.688191, 0.587785), 
			(-0.162460, -0.262866, 0.951056), 
			(0.442863, -0.238856, 0.864188), 
			(0.162460, -0.262866, 0.951056), 
			(0.309017, -0.500000, 0.809017), 
			(0.147621, -0.716567, 0.681718), 
			(0.000000, -0.525731, 0.850651), 
			(0.425325, -0.688191, 0.587785), 
			(0.587785, -0.425325, 0.688191), 
			(0.688191, -0.587785, 0.425325), 
			(-0.955423, 0.295242, 0.000000), 
			(-0.951056, 0.162460, 0.262866), 
			(-1.000000, 0.000000, 0.000000), 
			(-0.850651, 0.000000, 0.525731), 
			(-0.955423, -0.295242, 0.000000), 
			(-0.951056, -0.162460, 0.262866), 
			(-0.864188, 0.442863, -0.238856), 
			(-0.951056, 0.162460, -0.262866), 
			(-0.809017, 0.309017, -0.500000), 
			(-0.864188, -0.442863, -0.238856), 
			(-0.951056, -0.162460, -0.262866), 
			(-0.809017, -0.309017, -0.500000), 
			(-0.681718, 0.147621, -0.716567), 
			(-0.681718, -0.147621, -0.716567), 
			(-0.850651, 0.000000, -0.525731), 
			(-0.688191, 0.587785, -0.425325), 
			(-0.587785, 0.425325, -0.688191), 
			(-0.425325, 0.688191, -0.587785), 
			(-0.425325, -0.688191, -0.587785), 
			(-0.587785, -0.425325, -0.688191), 
			(-0.688191, -0.587785, -0.425325))
COLORMAP=((  0,   0,   0), ( 15,  15,  15), ( 31,  31,  31), ( 47,  47,  47), 
( 63,  63,  63), ( 75,  75,  75), ( 91,  91,  91), (107, 107, 107), 
(123, 123, 123), (139, 139, 139), (155, 155, 155), (171, 171, 171), 
(187, 187, 187), (203, 203, 203), (219, 219, 219), (235, 235, 235), 
( 15,  11,   7), ( 23,  15,  11), ( 31,  23,  11), ( 39,  27,  15), 
( 47,  35,  19), ( 55,  43,  23), ( 63,  47,  23), ( 75,  55,  27), 
( 83,  59,  27), ( 91,  67,  31), ( 99,  75,  31), (107,  83,  31), 
(115,  87,  31), (123,  95,  35), (131, 103,  35), (143, 111,  35), 
( 11,  11,  15), ( 19,  19,  27), ( 27,  27,  39), ( 39,  39,  51), 
( 47,  47,  63), ( 55,  55,  75), ( 63,  63,  87), ( 71,  71, 103), 
( 79,  79, 115), ( 91,  91, 127), ( 99,  99, 139), (107, 107, 151), 
(115, 115, 163), (123, 123, 175), (131, 131, 187), (139, 139, 203), 
(  0,   0,   0), (  7,   7,   0), ( 11,  11,   0), ( 19,  19,   0), 
( 27,  27,   0), ( 35,  35,   0), ( 43,  43,   7), ( 47,  47,   7), 
( 55,  55,   7), ( 63,  63,   7), ( 71,  71,   7), ( 75,  75,  11), 
( 83,  83,  11), ( 91,  91,  11), ( 99,  99,  11), (107, 107,  15), 
(  7,   0,   0), ( 15,   0,   0), ( 23,   0,   0), ( 31,   0,   0), 
( 39,   0,   0), ( 47,   0,   0), ( 55,   0,   0), ( 63,   0,   0), 
( 71,   0,   0), ( 79,   0,   0), ( 87,   0,   0), ( 95,   0,   0), 
(103,   0,   0), (111,   0,   0), (119,   0,   0), (127,   0,   0), 
( 19,  19,   0), ( 27,  27,   0), ( 35,  35,   0), ( 47,  43,   0), 
( 55,  47,   0), ( 67,  55,   0), ( 75,  59,   7), ( 87,  67,   7), 
( 95,  71,   7), (107,  75,  11), (119,  83,  15), (131,  87,  19), 
(139,  91,  19), (151,  95,  27), (163,  99,  31), (175, 103,  35), 
( 35,  19,   7), ( 47,  23,  11), ( 59,  31,  15), ( 75,  35,  19), 
( 87,  43,  23), ( 99,  47,  31), (115,  55,  35), (127,  59,  43), 
(143,  67,  51), (159,  79,  51), (175,  99,  47), (191, 119,  47), 
(207, 143,  43), (223, 171,  39), (239, 203,  31), (255, 243,  27), 
( 11,   7,   0), ( 27,  19,   0), ( 43,  35,  15), ( 55,  43,  19), 
( 71,  51,  27), ( 83,  55,  35), ( 99,  63,  43), (111,  71,  51), 
(127,  83,  63), (139,  95,  71), (155, 107,  83), (167, 123,  95), 
(183, 135, 107), (195, 147, 123), (211, 163, 139), (227, 179, 151), 
(171, 139, 163), (159, 127, 151), (147, 115, 135), (139, 103, 123), 
(127,  91, 111), (119,  83,  99), (107,  75,  87), ( 95,  63,  75), 
( 87,  55,  67), ( 75,  47,  55), ( 67,  39,  47), ( 55,  31,  35), 
( 43,  23,  27), ( 35,  19,  19), ( 23,  11,  11), ( 15,   7,   7), 
(187, 115, 159), (175, 107, 143), (163,  95, 131), (151,  87, 119), 
(139,  79, 107), (127,  75,  95), (115,  67,  83), (107,  59,  75), 
( 95,  51,  63), ( 83,  43,  55), ( 71,  35,  43), ( 59,  31,  35), 
( 47,  23,  27), ( 35,  19,  19), ( 23,  11,  11), ( 15,   7,   7), 
(219, 195, 187), (203, 179, 167), (191, 163, 155), (175, 151, 139), 
(163, 135, 123), (151, 123, 111), (135, 111,  95), (123,  99,  83), 
(107,  87,  71), ( 95,  75,  59), ( 83,  63,  51), ( 67,  51,  39), 
( 55,  43,  31), ( 39,  31,  23), ( 27,  19,  15), ( 15,  11,   7), 
(111, 131, 123), (103, 123, 111), ( 95, 115, 103), ( 87, 107,  95), 
( 79,  99,  87), ( 71,  91,  79), ( 63,  83,  71), ( 55,  75,  63), 
( 47,  67,  55), ( 43,  59,  47), ( 35,  51,  39), ( 31,  43,  31), 
( 23,  35,  23), ( 15,  27,  19), ( 11,  19,  11), (  7,  11,   7), 
(255, 243,  27), (239, 223,  23), (219, 203,  19), (203, 183,  15), 
(187, 167,  15), (171, 151,  11), (155, 131,   7), (139, 115,   7), 
(123,  99,   7), (107,  83,   0), ( 91,  71,   0), ( 75,  55,   0), 
( 59,  43,   0), ( 43,  31,   0), ( 27,  15,   0), ( 11,   7,   0), 
(  0,   0, 255), ( 11,  11, 239), ( 19,  19, 223), ( 27,  27, 207), 
( 35,  35, 191), ( 43,  43, 175), ( 47,  47, 159), ( 47,  47, 143), 
( 47,  47, 127), ( 47,  47, 111), ( 47,  47,  95), ( 43,  43,  79), 
( 35,  35,  63), ( 27,  27,  47), ( 19,  19,  31), ( 11,  11,  15), 
( 43,   0,   0), ( 59,   0,   0), ( 75,   7,   0), ( 95,   7,   0), 
(111,  15,   0), (127,  23,   7), (147,  31,   7), (163,  39,  11), 
(183,  51,  15), (195,  75,  27), (207,  99,  43), (219, 127,  59), 
(227, 151,  79), (231, 171,  95), (239, 191, 119), (247, 211, 139), 
(167, 123,  59), (183, 155,  55), (199, 195,  55), (231, 227,  87), 
(127, 191, 255), (171, 231, 255), (215, 255, 255), (103,   0,   0), 
(139,   0,   0), (179,   0,   0), (215,   0,   0), (255,   0,   0), 
(255, 243, 147), (255, 247, 199), (255, 255, 255), (159,  91,  83))

######################################################
# MDL data structures
######################################################
class mdl_point:
	vertices=[]
	lightnormalindex=0
	binary_format="<3BB"
	def __init__(self):
		self.vertices=[0]*3
		self.lightnormalindex=0
	def save(self, file):
		temp_data=[0]*4
		temp_data[0]=self.vertices[0]
		temp_data[1]=self.vertices[1]
		temp_data[2]=self.vertices[2]
		temp_data[3]=self.lightnormalindex
		data=struct.pack(self.binary_format, temp_data[0], temp_data[1], temp_data[2], temp_data[3])
		file.write(data)
	def dump(self):
		print "MDL Point Structure"
		print "vertex X: ", self.vertices[0]
		print "vertex Y: ", self.vertices[1]
		print "vertex Z: ", self.vertices[2]
		print "lightnormalindex: ",self.lightnormalindex
		print ""
		
class mdl_face:
	facesfront=1
	vertex_index=[]
	binary_format="<i3i"
	def __init__(self):
		self.facesfront = 1
		self.vertex_index = [ 0, 0, 0 ]

	def save(self, file):
		temp_data=[0]*4
		temp_data[0]=self.facesfront
		#reverse order to flip polygons after x transform
		temp_data[1]=self.vertex_index[1]
		temp_data[2]=self.vertex_index[0]
		temp_data[3]=self.vertex_index[2]
		data=struct.pack(self.binary_format,temp_data[0],temp_data[1],temp_data[2],temp_data[3])
		file.write(data)
	def dump (self):
		print "MDL Face Structure"
		print "facesfront: ", self.facesfront
		print "vertex 1 index: ", self.vertex_index[0]
		print "vertex 2 index: ", self.vertex_index[1]
		print "vertex 3 index: ", self.vertex_index[2]
		print ""
		
class mdl_tex_coord:
	onseam=0
	u=0
	v=0
	binary_format="<i2i"
	def __init__(self):
		self.onseam=0
		self.u=0
		self.v=0
	def save(self, file):
		temp_data=[0]*3
		temp_data[0]=self.onseam
		temp_data[1]=self.u
		temp_data[2]=self.v
		data=struct.pack(self.binary_format, temp_data[0], temp_data[1], temp_data[2])
		file.write(data)
	def dump (self):
		print "MDL Texture Coordinate Structure"
		print "onseam: ",self.onseam
		print "texture coordinate u: ",self.u
		print "texture coordinate v: ",self.v
		print ""


class mdl_skin:
	group = 0
	skin=[]
	dim=[]
	binary_format="<i"
	def __init__(self):
		self.group=0
		self.skin=[]
		self.dim=[0]*2
		self.dim[0]=256
		self.dim[1]=256 #defaults
	def save(self, file):
		temp_data=self.group
		data=struct.pack(self.binary_format, temp_data)
		file.write(data)
		#write skin
		for j in range (0,self.dim[1]):
			for i in range(0,self.dim[0]):
				data=struct.pack("<B",skin_data[(i+1)*self.dim[1]-j-1] ) #skin indices
				file.write(data)
	def dump (self):
		print "MDL Skin"
		print "group: ",self.group
		print ""
		
class mdl_frame:
	grouped=0
	bboxmin=[]
	bboxmax=[]
	name=[]
	vertices=[]
	binary_format="<i4B4B16s"

	def __init__(self):
		self.grouped=0
		self.bboxmin=[0]*4
		self.bboxmax=[0]*4
		self.name=""
		self.vertices=[]
	def save(self, file):
		temp_data=[0]*8
		temp_data[0]=self.grouped
		temp_data[1]=self.bboxmin[0]
		temp_data[2]=self.bboxmin[1]
		temp_data[3]=self.bboxmin[2]
		temp_data[4]=self.bboxmax[0]
		temp_data[5]=self.bboxmax[1]
		temp_data[6]=self.bboxmax[2]
		temp_data[7]=self.name
		data=struct.pack(self.binary_format, temp_data[0],temp_data[1],temp_data[2],temp_data[3],0,temp_data[4],temp_data[5],temp_data[6],0,temp_data[7])
		file.write(data)
	def dump (self):
		print "MDL Frame"
		print "min x: ",self.bboxmin[0]
		print "min y: ",self.bboxmin[1]
		print "min z: ",self.bboxmin[2]
		print "max x: ",self.bboxmax[0]
		print "max y: ",self.bboxmax[1]
		print "max z: ",self.bboxmax[2]
		print "name: ",self.name
		print ""
		
class mdl_obj:
	#Header Structure
	ident=0				#int 	This is used to identify the file
	version=0			#int 	The version number of the file (Must be 6)
	scale=[]		#vec_3 global scale
	translate=[]		#vec_3 global offset
	boundingradius=0	#float nobody knows
	eyeposition=[]		#vec_3 eye position

	num_skins=0		#int 	The number of skins associated with the model
	skin_width=0		#int 	The skin width in pixels
	skin_height=0		#int 	The skin height in pixels

	num_vertices=0		#int 	The number of vertices (constant for each frame)
	num_faces=0			#int	The number of faces (polygons)
	num_frames=0		#int 	The number of animation frames
	
	synctype=0		#int	sycronised?
	flags=0			#int	effect flags
	size=0			#float  size
	binary_format="<2i10f8if"  #little-endian (<), i ints, f floats etc
	#mdl data objects
	skins=[]
	tex_coords=[]
	faces=[]
	frames=[]
	
	def __init__ (self):
		self.scale=[0.0]*3
		self.translate=[0.0]*3
		self.eyeposition=[0.0]*3
		self.tex_coords=[]
		self.faces=[]
		self.frames=[]
		self.skins=[]
	def save(self, file):
		temp_data=[0]*21
		temp_data[0]=self.ident
		temp_data[1]=self.version
		temp_data[2]=float(self.scale[0])
		temp_data[3]=float(self.scale[1])
		temp_data[4]=float(self.scale[2])
		temp_data[5]=float(self.translate[0])
		temp_data[6]=float(self.translate[1])
		temp_data[7]=float(self.translate[2])
		temp_data[8]=float(self.boundingradius)
		temp_data[9]=float(self.eyeposition[0])
		temp_data[10]=float(self.eyeposition[1])
		temp_data[11]=float(self.eyeposition[2])
		temp_data[12]=self.num_skins
		temp_data[13]=self.skin_width
		temp_data[14]=self.skin_height
		temp_data[15]=self.num_vertices
		temp_data[16]=self.num_faces
		temp_data[17]=self.num_frames
		temp_data[18]=self.synctype
		temp_data[19]=self.flags
		temp_data[20]=float(self.size)
		data=struct.pack(self.binary_format, temp_data[0],temp_data[1],temp_data[2],temp_data[3],temp_data[4],temp_data[5],temp_data[6],temp_data[7],temp_data[8],temp_data[9],temp_data[10],temp_data[11],temp_data[12],temp_data[13],temp_data[14],temp_data[15],temp_data[16],temp_data[17],temp_data[18],temp_data[19],temp_data[20])
		file.write(data)
		#write the skin data
		for skin in self.skins:
			skin.save(file)
		#save the texture coordinates
		for tex_coord in self.tex_coords:
			tex_coord.save(file)
		#save the face info
		for face in self.faces:
			face.save(file)
		#save the frames
		for frame in self.frames:
			frame.save(file)
			for vert in frame.vertices:
				vert.save(file)
	def dump (self):
		print "Header Information"
		print "ident: ", self.ident
		print "version: ", self.version
		print "scale x: ", self.scale[0]
		print "scale y: ", self.scale[1]
		print "scale z: ", self.scale[2]
		print "offset x: ", self.translate[0]
		print "offset y: ", self.translate[1]
		print "offset z: ", self.translate[2]
		print "boundingradius: ",self.boundingradius
		print "eyeposition x: ", self.eyeposition[0]
		print "eyeposition y: ", self.eyeposition[1]
		print "eyeposition z: ", self.eyeposition[2]
		print "number of skins: ", self.num_skins
		print "skin width: ", self.skin_width
		print "skin height: ", self.skin_height
		print "number of vertices: ", self.num_vertices
		print "number of faces: ", self.num_faces
		print "number of frames: ", self.num_frames
		print "synctype: ", self.synctype
		print "flags: ", self.flags
		print "size: ", self.size
		print ""



######################################################
# Validation
######################################################
def FindColorIndex(r, g, b):
	for i in range(0,256):
		if ((COLORMAP[i][0] == r) & (COLORMAP[i][1] == g) & (COLORMAP[i][2] == b)):
			return i
	return -1

def validation(object):
	global user_frame_list


	if object.getEuler('worldspace')!=Blender.Mathutils.Euler(0.0,0.0,0.0):
		print "object.rot: ", object.getEuler('worldspace')
		object.setEuler([0.0,0.0,0.0])
		print "Object is rotated-You should rotate the mesh verts, not the object"
		result=Blender.Draw.PupMenu("Object is rotated-You should rotate the mesh verts, not the object-fixing for you")
	
	#get access to the mesh data
	mesh=object.getData(False, True) #get the object (not just name) and the Mesh, not NMesh

	
	#check it's composed of only tri's	
	result=0
	for face in mesh.faces:
		if len(face.verts)!=3:
			#select the face for future triangulation
			face.sel=1
			if result==0:  #first time we have this problem, don't pop-up a window every time it finds a quad
			  print "Model not made entirely of triangles"
			  result=Blender.Draw.PupMenu("Model not made entirely out of Triangles-Convert?%t|YES|NO")
	
	#triangulate or quit
	if result==1:
		#selecting face mode
		Blender.Mesh.Mode(3)
		editmode = Window.EditMode()    # are we in edit mode?  If so ...
		if editmode: Window.EditMode(0) # leave edit mode before getting the mesh
		mesh.quadToTriangle(0) #use closest verticies in breaking a quad
	elif result==2:
		return False #user will fix (I guess)

	#check it has UV coordinates
	if mesh.vertexUV==True:
		print "Vertex UV not supported"
		result=Blender.Draw.PupMenu("Vertex UV not suppored-Use Sticky UV%t|Quit")
		return False
			
	elif mesh.faceUV==True:
		for face in mesh.faces:
			if(len(face.uv)==3):
				pass
			else:
				print "Model's vertices do not all have UV"
				result=Blender.Draw.PupMenu("Model's vertices do not all have UV%t|Quit")
				return False
	
	else:
		print "Model does not have UV (face or vertex)"
		result=Blender.Draw.PupMenu("Model does not have UV (face or vertex)%t|Quit")
		return False

	#check it has an associated texture map
	last_face=""
	last_face=mesh.faces[0].image
	if last_face=="":
		print "Model does not have a texture Map"
		result=Blender.Draw.PupMenu("Model does not have a texture Map%t|Quit")
		return False

	#check if each face uses the same texture map (only one allowed)
	for face in mesh.faces:
		mesh_image=face.image
		if not mesh_image:
			print "Model has a face without a texture Map"
			result=Blender.Draw.PupMenu("Model has a face without a texture Map%t|Quit")
			return False
		if mesh_image!=last_face:
			print "Model has more than 1 texture map assigned"
			result=Blender.Draw.PupMenu("Model has more than 1 texture map assigned%t|Quit")
			return False
		

	size=mesh_image.getSize()
	#is this really what the user wants
	#	if (size[0]!=256 or size[1]!=256):
	#	print "Texture map size is non-standard (not 256x256), it is: ",size[0],"x",size[1]
	#	result=Blender.Draw.PupMenu("Texture map size is non-standard (not 256x256), it is: "+str(size[0])+"x"+str(size[1])+": Continue?%t|YES|NO")
	#	if(result==2):
	#		return False
	print "Texture map size is: ",size[0],"x",size[1]
	global skin_data
	p = size[0]*size[1]
	warned = 0
	skin_data = [0]*p
	for i in range(0,size[0]):
		for j in range (0,size[1]):
			pixel = mesh_image.getPixelI(i,j)
			color_index = FindColorIndex(pixel[0],pixel[1],pixel[2])
			if color_index == -1:
				skin_data[i*size[1]+j] = 0
				if warned == 0:
					print "Texture is not in Q1 palette"
					warned = 1
			else:
				skin_data[i*size[1]+j] = color_index

	#verify frame list data
	user_frame_list=get_frame_list()	
	temp=user_frame_list[len(user_frame_list)-1]
	temp_num_frames=temp[2]
	
	#verify tri/vert/frame counts are within MDL standard
	face_count=len(mesh.faces)
	vert_count=len(mesh.verts)	
	frame_count=temp_num_frames
	
	if face_count>MDL_MAX_TRIANGLES:
		print "Number of triangles exceeds MDL standard: ", face_count,">",MDL_MAX_TRIANGLES
		result=Blender.Draw.PupMenu("Number of triangles exceeds MDL standard: Continue?%t|YES|NO")
		if(result==2):
			return False
	if vert_count>MDL_MAX_VERTICES:
		print "Number of verticies exceeds MDL standard: ",vert_count,">",MDL_MAX_VERTICES
		result=Blender.Draw.PupMenu("Number of verticies exceeds MDL standard: Continue?%t|YES|NO")
		if(result==2):
			return False
	if frame_count>MDL_MAX_FRAMES:
		print "Number of frames exceeds MDL standard: ",frame_count,">",MDL_MAX_FRAMES
		result=Blender.Draw.PupMenu("Number of frames exceeds MDL standard: Continue?%t|YES|NO")
		if(result==2):
			return False
	#model is OK
	return True

######################################################
# Fill MDL data structure
######################################################
def fill_mdl(mdl, object):
	#global defines
	global user_frame_list
#	global g_texture_path
	global g_fixuvs
	global g_flags
	
	Blender.Window.DrawProgressBar(0.25,"Filling MDL Data")
	
	#get a Mesh, not NMesh
	mesh=object.getData(False, True)	
	
	#load up some intermediate data structures
	tex_list={}
	vt_list={}
	backlist={}
	tex_count=0
	#create the vertex list from the first frame
	Blender.Set("curframe", 1)
	
	#header information
	mdl.ident=1330660425 
	mdl.version=6	
	mdl.num_faces=len(mesh.faces)

	#get the skin information
	#use the first faces' image for the texture information
	mesh_image=mesh.faces[0].image
	size=mesh_image.getSize()
	mdl.skin_width=size[0]
	mdl.skin_height=size[1]

	mdl.num_skins=1
	#add a skin node to the mdl data structure
	mdl.skins.append(mdl_skin())
	mdl.skins[0].group = 0
	mdl.skins[0].dim[0]=size[0]
	mdl.skins[0].dim[1]=size[1]

	#put texture information in the mdl structure
	#build UV coord dictionary (prevents double entries-saves space)
	for face in mesh.faces:
		for i in range(0,3):
			t=(face.uv[i])
			vt=(face.verts[i].co)
			#vertices are merged if occupy same uv coords AND same space in frame 1
			#this might cause undesired merging if models are not carefully designed
			#would take far too long to check every vertex in every frame

			tex_key=(t[0],t[1],vt[0],vt[1],vt[2])
			if not tex_list.has_key(tex_key):
				tex_list[tex_key]=tex_count
				#add a dictionary here of entries for the vertex set
				vt_list[face.index, i]=tex_count
				backlist[tex_count] = face.verts[i].index
				tex_count+=1
			else:
				vt_list[face.index, i]=tex_list[tex_key]
				backlist[tex_count] = face.verts[i].index


	mdl.num_vertices=tex_count
	
	for this_tex in range (0, mdl.num_vertices):
		mdl.tex_coords.append(mdl_tex_coord())
	for coord, index in tex_list.iteritems():
		mdl.tex_coords[index].u=floor(coord[0]*mdl.skin_width)
		mdl.tex_coords[index].v=floor((1-coord[1])*mdl.skin_height)
		if g_fixuvs.val == 1: #shift them 
                        while mdl.tex_coords[index].u < 0:
                                mdl.tex_coords[index].u = mdl.tex_coords[index].u + mdl.skin_width
                        while mdl.tex_coords[index].u >= mdl.skin_width:
                                mdl.tex_coords[index].u = mdl.tex_coords[index].u - mdl.skin_width
                        while mdl.tex_coords[index].v < 0:
                                mdl.tex_coords[index].v = mdl.tex_coords[index].v + mdl.skin_height
                        while mdl.tex_coords[index].v >= mdl.skin_height:
                                mdl.tex_coords[index].v = mdl.tex_coords[index].v - mdl.skin_height
		elif g_fixuvs.val == 2: #clamp them
                        if mdl.tex_coords[index].u < 0:
                                mdl.tex_coords[index].u = 0
                        if mdl.tex_coords[index].u >= mdl.skin_width:# mdl.skin_width:
                                mdl.tex_coords[index].u = mdl.skin_width - 1
                                #print "vertex ", index, " clamped"
                        if mdl.tex_coords[index].v < 0:
                                mdl.tex_coords[index].v = 0
                        if mdl.tex_coords[index].v >= mdl.skin_height:
                                mdl.tex_coords[index].v = mdl.skin_height - 1
                                #print "vertex ", index, " clamped"

	#put faces in the mdl structure
	#for each face in the model
	for this_face in range(0, mdl.num_faces):
		mdl.faces.append(mdl_face())
		for i in range(0,3):
			#blender uses indexed vertexes so this works very well
			mdl.faces[this_face].vertex_index[i]=vt_list[mesh.faces[this_face].index, i]


			
	#get the frame list
	user_frame_list=get_frame_list()
	if user_frame_list=="default":
		mdl.num_frames=10
	else:
		temp=user_frame_list[len(user_frame_list)-1]  #last item
		mdl.num_frames=temp[2] #last frame number
	

	progress=0.5
	progressIncrement=0.25/mdl.num_frames

	# set global scale and translation points
	# maybe add integer options

	mesh_min_x=100000.0
	mesh_max_x=-100000.0
	mesh_min_y=100000.0
	mesh_max_y=-100000.0
	mesh_min_z=100000.0
	mesh_max_z=-100000.0

	for frame_counter in range(0,mdl.num_frames):

		Blender.Set("curframe", frame_counter+1)  #set blender to the correct frame
		mesh.getFromObject(object.name, 1, 0)   #update the mesh to make verts current
		
		for face in mesh.faces:
			for vert in face.verts:					
				if mesh_min_x>vert.co[1]: mesh_min_x=vert.co[1]
				if mesh_max_x<vert.co[1]: mesh_max_x=vert.co[1]
				if mesh_min_y>vert.co[0]: mesh_min_y=vert.co[0]
				if mesh_max_y<vert.co[0]: mesh_max_y=vert.co[0]
				if mesh_min_z>vert.co[2]: mesh_min_z=vert.co[2]
				if mesh_max_z<vert.co[2]: mesh_max_z=vert.co[2]
	
	mesh_scale_x=(mesh_max_x-mesh_min_x)/255
	mesh_scale_y=(mesh_max_y-mesh_min_y)/255
	mesh_scale_z=(mesh_max_z-mesh_min_z)/255

	mdl.scale[0] = mesh_scale_x
	mdl.scale[1] = mesh_scale_y
	mdl.scale[2] = mesh_scale_z

	mdl.translate[0] = mesh_min_x
	mdl.translate[1] = mesh_min_y
	mdl.translate[2] = mesh_min_z



	#fill in each frame with frame info and all the vertex data for that frame
	for frame_counter in range(0,mdl.num_frames):
		
		progress+=progressIncrement
		Blender.Window.DrawProgressBar(progress, "Calculating Frame: "+str(frame_counter+1))
			
		#add a frame
		mdl.frames.append(mdl_frame())


		#update the mesh objects vertex positions for the animation
		Blender.Set("curframe", frame_counter+1)  #set blender to the correct frame
		mesh.getFromObject(object.name, 1, 0)  #update the mesh to make verts current
		
		
		
		frame_min_x=100000
		frame_max_x=-100000
		frame_min_y=100000
		frame_max_y=-100000
		frame_min_z=100000
		frame_max_z=-100000		
		
	
		#now for the vertices
		for vert_counter in range(0, mdl.num_vertices):
			#add a vertex to the mdl structure
			mdl.frames[frame_counter].vertices.append(mdl_point())

			#figure out the new coords based on scale and transform
			#then translates the point so it's not less than 0
			#then scale it so it's between 0..255

			current_vertex = backlist[vert_counter]
			vert = mesh.verts[current_vertex]

			# scale
			# x coord needs flipping
			new_x=255-int((vert.co[1]-mesh_min_x)/mesh_scale_x)
			new_y=int((vert.co[0]-mesh_min_y)/mesh_scale_y)
			new_z=int((vert.co[2]-mesh_min_z)/mesh_scale_z)

			# bbox stuff
			if frame_min_x>new_x: frame_min_x=new_x
			if frame_max_x<new_x: frame_max_x=new_x
			if frame_min_y>new_y: frame_min_y=new_y
			if frame_max_y<new_y: frame_max_y=new_y
			if frame_min_z>new_z: frame_min_z=new_z
			if frame_max_z<new_z: frame_max_z=new_z

			#put them in the structure
			mdl.frames[frame_counter].vertices[vert_counter].vertices=(new_x, new_y, new_z)

			#need to add the lookup table check here
			maxdot = -999999.0;
			maxdotindex = -1;

			
			for j in range(0,162):
				x1=-mesh.verts[current_vertex].no[1]
				y1=mesh.verts[current_vertex].no[0]
				z1=mesh.verts[current_vertex].no[2]
				dot = (x1*MDL_NORMALS[j][0]+
				       y1*MDL_NORMALS[j][1]+
							 z1*MDL_NORMALS[j][2]);
				if (dot > maxdot):
					maxdot = dot;
					maxdotindex = j;
			
			mdl.frames[frame_counter].vertices[vert_counter].lightnormalindex=maxdotindex
			
			del maxdot, maxdotindex
			del new_x, new_y, new_z		

		mdl.frames[frame_counter].bboxmin[0] = frame_min_x
		mdl.frames[frame_counter].bboxmax[0] = frame_max_x
		mdl.frames[frame_counter].bboxmin[1] = frame_min_y
		mdl.frames[frame_counter].bboxmax[1] = frame_max_y
		mdl.frames[frame_counter].bboxmin[2] = frame_min_z
		mdl.frames[frame_counter].bboxmax[2] = frame_max_z

		del frame_min_x,frame_max_x,frame_min_y,frame_max_y,frame_min_z,frame_max_z


	
	#output all the frame names-user_frame_list is loaded during the validation
	for frame_set in user_frame_list:
		for counter in range(frame_set[1]-1, frame_set[2]):
			mdl.frames[counter].name=frame_set[0]+str(counter-frame_set[1]+2)

	ofs = object.getLocation('worldspace')
	sc = object.getSize('worldspace')

	# Rather than warn about these things, just apply the transformations they indicate
	mdl.scale[0] = mdl.scale[0] * sc[1] * g_scale.val
	mdl.scale[1] = mdl.scale[1] * sc[0] * g_scale.val
	mdl.scale[2] = mdl.scale[2] * sc[2] * g_scale.val

	mdl.translate[0] = mdl.translate[0] + ofs[1]
	mdl.translate[1] = mdl.translate[1] + ofs[0]
	mdl.translate[2] = mdl.translate[2] + ofs[2]




	mdl.boundingradius = (mesh_max_x-mesh_min_x+mesh_max_y-mesh_min_y+mesh_max_z-mesh_min_z)/2 
		# a crude approximation, but when is this used?
	mdl.eyeposition[0] = 0
	mdl.eyeposition[1] = 0
	mdl.eyeposition[2] = mesh_min_z   #ground plane for QMe
	mdl.synctype = 1
	mdl.flags = g_flags.val
	mdl.size = 10.0 #unused?

######################################################
# Get Frame List
######################################################
def get_frame_list():
	global g_frame_filename
	frame_list=[]

	if g_frame_filename.val=="default":
		return MDL_FRAME_NAME_LIST

	else:
	#check for file
		if (Blender.sys.exists(g_frame_filename.val)==1):
			#open file and read it in
			file=open(g_frame_filename.val,"r")
			lines=file.readlines()
			file.close()

			#check header (first line)
			if lines[0].strip()<>"# MDL Frame Name List":
				print "its not a valid file"
				result=Blender.Draw.PupMenu("This is not a valid frame definition file-using default%t|OK")
				return MDL_FRAME_NAME_LIST
			else:
				#read in the data
				num_frames=0
				for counter in range(1, len(lines)):
					current_line=lines[counter].strip()
					if current_line[0]=="#":
						#found a comment
						pass
					else:
						data=current_line.split()
						frame_list.append([data[0],num_frames+1, num_frames+int(data[1])])
						num_frames+=int(data[1])
				return frame_list
		else:
			print "Cannot find file"
			result=Blender.Draw.PupMenu("Cannot find frame definion file-using default%t|OK")
			return MDL_FRAME_NAME_LIST



######################################################
# Save MDL Format
######################################################
def save_mdl(filename):
	print ""
	print "***********************************"
	print "MDL Export"
	print "***********************************"
	print ""
	
	Blender.Window.DrawProgressBar(0.0,"Beginning MDL Export")
	
	mdl=mdl_obj()  #blank mdl object to save

	#get the object
	mesh_objs = Blender.Object.GetSelected()

	#check there is a blender object selected
	if len(mesh_objs)==0:
		print "Fatal Error: Must select a mesh to output as MDL"
		print "Found nothing"
		result=Blender.Draw.PupMenu("Must select an object to export%t|OK")
		return

	mesh_obj=mesh_objs[0] #this gets the first object (should be only one)

	#check if it's a mesh object
	if mesh_obj.getType()!="Mesh":
		print "Fatal Error: Must select a mesh to output as MDL"
		print "Found: ", mesh_obj.getType()
		result=Blender.Draw.PupMenu("Selected Object must be a mesh to output as MDL%t|OK")
		return

	ok=validation(mesh_obj)
	if ok==False:
		return
	
	fill_mdl(mdl, mesh_obj)
	mdl.dump()
	
	Blender.Window.DrawProgressBar(1.0, "Writing to Disk")
	
	#actually write it to disk
	file=open(filename,"wb")
	mdl.save(file)
	file.close()
	
	#cleanup
	mdl=0
	
	print "Closed the file"
