from src import decoder
import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.behaviors import DragBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.base import runTouchApp

from kivy.graphics import *
height = 2000
mult = 2

class DragButt(DragBehavior, Label):
	pass

def drawConn(canv,objLocs,objSize, fr,to, inport = 0,outport = 0): #fr is short for from
	x1 = mult*objLocs[fr][0] + inport*10 + 10
	y1 = height-objLocs[fr][1]
	if (objLocs[to][0] == -1 and objLocs[to][1] == -1):
		x2 = x1
		y2 = y1 +10
	else:
		x2 = mult*objLocs[to][0] + outport*10 + 10
		y2 = height-objLocs[to][1]-objSize[to][1]
	diff = abs(y1-y2)/2
	with canv.canvas:
		Color(1., 1., 1.)
		Line(bezier=(x1,y1,x1,y1+diff,x2,y2-diff,x2,y2))

def addAtom(canv,objLocs,objSize, obj):
	x = mult*obj.fields["settings(6194)"].fields["desktop_settings(612)"].fields["x(17)"]
	y = height - obj.fields["settings(6194)"].fields["desktop_settings(612)"].fields["y(18)"]
	flag = 0
	name = ''
	if (len(objLocs) < obj.id):
		for i in range(obj.id-len(objLocs) + 1):
			objLocs.append((-1,-1))
			objSize.append((-1,-1))
	nameIn = obj.classname
	#values
	if nameIn == 'float_core.decimal_value_atom(289)':
		name = obj.fields["name(374)"]
		val = obj.fields["value_type(702)"].fields["default_value(891)"]
		width = 15 + 6*len(name)
		name += '\n' + str(val)[:6]
		objSize[obj.id] = (width,40)
		flag = 1
	elif nameIn == 'float_core.boolean_value_atom(87)':
		name = obj.fields["name(374)"]
		val = obj.fields["value_type(702)"].fields["default_value(6957)"]
		width = 15 + 6*len(name)
		name += '\n' + str(val)
		objSize[obj.id] = (width,40)
		flag = 1
	elif nameIn == 'float_core.indexed_value_atom(180)':
		name = obj.fields["name(374)"]
		width = 15 + 6*len(name)
		vals = obj.fields["value_type(702)"].fields["items(393)"]
		dropdown = DropDown()
		i = 0
		for val in vals:
			 btn = Button(text=val.fields["name(651)"], font_size='12sp', size_hint_y=None, height=20)
			 btn.bind(on_release=lambda btn: dropdown.select(btn.text))
			 dropdown.add_widget(btn)
			 i += 1
		objSize[obj.id] = (width,40)
		mainbutton = Button(text=name + '\n' + vals[0].fields["name(651)"], font_size='12sp', pos=(x,y-40), size_hint=(None, None), size=objSize[obj.id])
		mainbutton.bind(on_release=dropdown.open)
		dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', name + '\n' + x))
		canv.add_widget(mainbutton)
	elif nameIn == 'float_core.integer_value_atom(394)':
		name = obj.fields["name(374)"]
		val = obj.fields["value_type(702)"].fields["default_value(6956)"]
		width = 15 + 6*len(name)
		name += '\n' + str(val)
		objSize[obj.id] = (width,40)
		flag = 1
	elif nameIn == 'float_common_atoms.constant_value_atom(314)':
		name = str(obj.fields["constant_value(750)"])[:5]
		width = 15 + 6*len(name)
		objSize[obj.id] = (width,40)
		flag = 1
	elif nameIn == 'float_common_atoms.constant_integer_value_atom(298)':
		name = str(obj.fields["constant_value(720)"])
		width = 15 + 6*len(name)
		objSize[obj.id] = (width,40)
		flag = 1
	#atoms
	elif nameIn == 'float_common_atoms.nitro_atom(1721)':
		name = 'nitro'
		val = obj.fields["code(6264)"][:19]
		width = 15 + 6*len(val)
		name += '\n' + str(val)
		objSize[obj.id] = (width,40)
		flag = 1
	elif nameIn == 'float_common_atoms.mix_atom(301)':
		name = 'MIX'
		objSize[obj.id] = (30,30)
		flag = 1
	elif nameIn == 'float_common_atoms.polyphonic_note_voice_atom(350)':
		name = 'PolyNoteVoice'
		objSize[obj.id] = (90,30)
		flag = 1
	elif nameIn == 'float_common_atoms.note_delay_compensation_atom(1435)':
		name = 'NoYo'
		objSize[obj.id] = (30,30)
		flag = 1
	elif nameIn == 'float_common_atoms.delay_compensation_atom(1371)':
		name = 'oYo'
		objSize[obj.id] = (30,30)
		flag = 1
	elif nameIn == 'float_core.modulation_source_atom(766)':
		name = obj.fields["name(3639)"] + '\no->'
		width = 15 + 6*(len(name)-4)
		objSize[obj.id] = (width,30)
		flag = 1
	elif nameIn == 'float_core.value_led_atom(189)':
		name = 'led'
		objSize[obj.id] = (20,20)
		flag = 1
	#other atoms
	elif nameIn == 'float_common_atoms.decimal_event_filter_atom(400)':
		name = 'decFilter'
		val1 = obj.fields["comparison(842)"]
		val2 = obj.fields["comparison_value(843)"]
		width = 15 + 6*len(name)
		name += '\n' + str(val1) + '\n' + str(val2)
		objSize[obj.id] = (width,60)
		flag = 1
	elif nameIn == 'float_common_atoms.multiplexer_atom(1188)':
		name = 'MUX'
		val = obj.fields["inputs(4763)"]
		objSize[obj.id] = (10*val+20,30)
		name += ' ' + str(val)
		flag = 1
	elif nameIn == 'float_common_atoms.deinterleave_atom(368)':
		name = 'L/R'
		objSize[obj.id] = (30,30)
		flag = 1
	elif nameIn == 'float_common_atoms.indexed_lookup_table_atom(344)':
		name = 'lookup'
		vals = obj.fields["row_data(744)"]
		length = obj.fields["row_count(743)"]
		name += '\n'
		for i in range(length):
			name += str(vals[i].fields["cells(726)"][0].fields["value(739)"]) + '|'
		width = 6*(len(name)-6)
		objSize[obj.id] = (width,40)
		flag = 1
	#math
	elif nameIn == 'float_common_atoms.constant_add_atom(308)':
		name = '+'
		val = obj.fields["constant_value(750)"]
		name += '\n' + str(val)
		objSize[obj.id] = (40,40)
		flag = 1
	elif nameIn == 'float_common_atoms.constant_multiply_atom(303)':
		name = 'x'
		val = obj.fields["constant_value(750)"]
		name += '\n' + str(val)[:5]
		objSize[obj.id] = (40,40)
		flag = 1
	elif nameIn == 'float_common_atoms.add_atom(337)':
		name = '+'
		objSize[obj.id] = (30,30)
		flag = 1
	elif nameIn == 'float_common_atoms.multiply_atom(367)':
		name = 'x'
		objSize[obj.id] = (30,30)
		flag = 1
	elif nameIn == 'float_common_atoms.subtract_atom(343)':
		name = '-'
		objSize[obj.id] = (30,30)
		flag = 1
	elif nameIn == 'float_common_atoms.multiply_add_atom(304)':
		name = 'x+'
		objSize[obj.id] = (obj.fields["multiplier_pairs(724)"]*20+10,30)
		flag = 1
	elif nameIn == 'float_common_atoms.sum_atom(305)':
		name = '+++'
		val = obj.fields["inputs(725)"]
		name +=  str(val)
		objSize[obj.id] = (val*10+10,40)
		flag = 1
	#DSP
	elif nameIn == 'float_common_atoms.svf_filter_atom(578)':
		name = 'filter'
		objSize[obj.id] = (30,30)
		flag = 1
	elif nameIn == 'float_common_atoms.surge_classic_oscillator_atom(491)':
		name = 'surge osc'
		objSize[obj.id] = (100,30)
		flag = 1
	#components
	elif nameIn == 'float_core.proxy_in_port_component(154)':
		name = 'IN'
		#val = obj.fields["port(301)"].fields["decorated_name(499)"]
		#name += '\n' + val
		objSize[obj.id] = (30,30)
		flag = 1
	elif nameIn == 'float_core.proxy_out_port_component(50)':
		name = 'OUT'
		#val = obj.fields["port(301)"].fields["decorated_name(499)"]
		#name += '\n' + val
		objSize[obj.id] = (30,30)
		y-=300
		flag = 1
	elif nameIn == 'float_core.nested_device_chain_slot(587)':
		name = 'nest'
		val = obj.fields["name(835)"]
		name += '\n' + val
		objSize[obj.id] = (40,40)
		flag = 1
	#everything else
	else:
		dot = 0
		paren = 0
		name = ''
		num = ''
		for i in range(len(nameIn)):
			if nameIn[i] == '(':
				paren = 1
			if dot and not paren:
				if nameIn[i] == '_':
					name += ' '
				else:
					name += nameIn[i]
			elif paren:
				num += nameIn[i]
			if nameIn[i] == '.':
				dot = 1
		if not name:
			name = num
		width = 8*len(name) + 16
		objSize[obj.id] = (width,30)
		flag = 1
	if flag:
		#canv.add_widget(DragButt(text=name, pos = (x,y-objSize[obj.id][1]), font_size='12sp', size_hint=(None, None), size=objSize[obj.id], drag_rectangle=(x, y, objSize[obj.id][0], objSize[obj.id][1]), drag_timeout=10000000, drag_distance=0))
		canv.add_widget(Button(text=name, pos = (x,y-objSize[obj.id][1]), font_size='12sp', size_hint=(None, None), size=objSize[obj.id]))
	objLocs[obj.id] = (x/mult,height-y)

def setSlide(instance, manager, screenName):
	manager.current = screenName

def addKids(canv,objLocs,objSize, child):
	try:
		kids = child.fields["settings(6194)"].fields["inport_connections(614)"]
	except AttributeError:
		pass
		#print(child)
	except:
		pass
		#print(child.fields)
	else:
		item = 0
		while(item < len(kids)):
			try:
				kids[item].fields["source_component(248)"].fields["settings(6194)"].fields["desktop_settings(612)"].fields["x(17)"]
			except AttributeError: #its a reference
				pass
				if kids[item].fields["source_component(248)"]:
					drawConn(canv,objLocs,objSize, child.id, kids[item].fields["source_component(248)"].classNum, item, kids[item].fields["outport_index(249)"])
			except:
				pass
				#print(kids[item].fields)
			else:
				addAtom(canv,objLocs,objSize,kids[item].fields["source_component(248)"])
				drawConn(canv,objLocs,objSize, child.id, kids[item].fields["source_component(248)"].id, item, kids[item].fields["outport_index(249)"])
			addKids(canv,objLocs,objSize,kids[item].fields["source_component(248)"])
			item += 1
			
class Hello(GridLayout):
	def __init__(self,**kwargs):
		global sm, fileNames
		self.rows = 2
		super(Hello,self).__init__(**kwargs)
		sm = ScreenManager(size_hint = (1, 9))
		selector = GridLayout(rows=1, size_hint = (1,1))
		fileNames = {}
		for file in os.listdir('.'):
			opened = []
			if file.endswith(".bwdevice") or file.endswith(".bwproject") or file.endswith(".bwmodulator") or file.endswith(".bwpreset") or file.endswith(".bwclip") or file.endswith(".bwscene"):
				print ('-'+file)
				with open(file, 'rb') as readThis:
					opened = decoder.objectify(readThis.read())
				subWidget = FloatLayout(size_hint=(None,None), size = (5000,height))
				objLocs = []
				objSize = []
				for eachField in ("child_components(173)","proxy_in_ports(177)","proxy_out_ports(178)"):
					children = opened[1].fields[eachField]
					item = 0
					while(item < len(children)):
						try:
							children[item].fields["settings(6194)"].fields["desktop_settings(612)"].fields["x(17)"]
						except AttributeError: #its a reference
							pass
							#print(children[item])
						except:
							pass
							#print(children[item].fields)
						else:
							addAtom(subWidget,objLocs,objSize, children[item])
						addKids(subWidget,objLocs,objSize, children[item])
						item += 1
				screen = Screen(name=file)
				root = ScrollView(size_hint=(1, 1))
				root.add_widget(subWidget)
				screen.add_widget(root)
				#screen.add_widget(subWidget)
				sm.add_widget(screen)
				but = Button(text=file[:-9], font_size='8sp', on_press=self.callback)
				fileNames[but] = file
				selector.add_widget(but)
				#selector.add_widget(Button(text=file))
		sm.current = "Peak Limiter.bwdevice"
		self.add_widget(selector)
		self.add_widget(sm)
		
	def callback(instance, value):
		print('My button <%s> state is <%s>' % (instance, value))
		global sm, fileNames
		sm.current = fileNames[value]

	def newScene(self, event):
		global sm, fileName
		sm.current = fileName

class app1(App):
    def build(self):
        return Hello()
if __name__=="__main__":
	app1().run()
	
	''''sm = ScreenManager(size_hint = (1, 9))
	selector = GridLayout(rows=1, size_hint = (1,1))
	overall = GridLayout(rows=2)
	for file in os.listdir('.'):
		opened = []
		if file.endswith(".bwdevice") or file.endswith(".bwproject") or file.endswith(".bwmodulator") or file.endswith(".bwpreset") or file.endswith(".bwclip") or file.endswith(".bwscene"):
			print ('-'+file)
			with open(file, 'rb') as readThis:
				opened = decoder.objectify(readThis.read())
			subWidget = FloatLayout(size_hint_y=None, size = (2000,height))
			for eachField in ("child_components(173)","proxy_in_ports(177)","proxy_out_ports(178)"):
				children = opened[1].fields[eachField]
				item = 0
				while(item < len(children)):
					try:
						children[item].fields["settings(6194)"].fields["desktop_settings(612)"].fields["x(17)"]
					except AttributeError: #its a reference
						pass
						#print(children[item])
					except:
						pass
						#print(children[item].fields)
					else:
						addAtom(subWidget, children[item])
					addKids(subWidget, children[item])
					item += 1
			screen = Screen(name=file)
			root = ScrollView(size_hint=(1, 1))
			root.add_widget(subWidget)
			screen.add_widget(root)
			sm.add_widget(screen)
			selector.add_widget(Button(text=file, on_press=newScene(name=file)))
	sm.current = "Peak Limiter.bwdevice"
	overall.add_widget(selector)
	overall.add_widget(sm)
	runTouchApp(overall)'''