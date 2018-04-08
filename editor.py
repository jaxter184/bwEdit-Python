import tkinter as tk
import random
from tkinter import ttk
from tkinter import filedialog
from src import decoder
from src.lib import fs, util, atoms
from src.lib.luts import nodes
from src.nitro import nitro
import os
MED_FONT = ("Verdana", 9)
BOL_FONT = ("Verdana bold", 9)
THK_FONT = ("Arial bold", 14)
CODEFONT = ("Consolas", 8)
DOT_SIZE = 5
PORT_OFF = 15
TOTAL_OFF = 25
LINE_WID = 3
LINE_COL = "#fd811a"
H_MULT = 3
V_MULT = 1
BORDER = 6
NODECOL = "#fff"
BASECOL = "#414141"
ACCCOL1 = "#535353"
INSP_WIDTH = 50

class Application(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		
		tk.Tk.iconbitmap(self, default="bitwig.ico")
		tk.Tk.wm_title(self, "poop")
		
		top = self.winfo_toplevel() #menu bar
		self.menuBar = tk.Menu(top)
		top['menu'] = self.menuBar
		self.subMenu = tk.Menu(self.menuBar, tearoff=0) #file
		self.menuBar.add_cascade(label='File', menu=self.subMenu)
		self.subMenu.add_command(label='Save',)
		self.subMenu.add_command(label='Load', command=self.openfile)
		self.subMenu.add_command(label='Other',)
		self.subMenu.add_separator()
		self.subMenu.add_command(label='Exit',)
		self.subMenu = tk.Menu(self.menuBar, tearoff=0) #help
		self.menuBar.add_cascade(label='Help', menu=self.subMenu)
		self.subMenu.add_command(label='About',)
		self.file = ''
		container = tk.Frame(self)
		container.pack(side = "top", fill = "both", expand = True)
		container.grid_rowconfigure(0,weight = 1)
		container.grid_columnconfigure(0,weight = 1)
		self.frames = {}
		for f in (MainPage,):
			frame = f(container, self)
			self.frames[f] = frame
			frame.grid(row=0, column=0, sticky="nsew")
		self.show_frame(MainPage)
		
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()
	
	def openfile(self):
		filename = tk.filedialog.askopenfilename(filetypes = (("All Files", "*.*"),
																				("Bitwig Devices", "*.bwdevice"),
																				("Bitwig Modulators", "*.bwmodulator"),
																				("Bitwig Presets", "*.bwpreset"),
																				))
		f = ''
		print ('-'+filename)
		tk.Tk.wm_title(self, filename)
		with open(filename, 'rb') as readThis:
			f = decoder.bwDecode(readThis.read())
		self.frames[MainPage].editor.load(f)

class MainPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		#label = ttk.Label(self, text="StartPage", font = MED_FONT)
		#label.pack(pady=10, padx=10)
		self.editor = EditorCanvas(self)
		self.editor.pack(fill="both", expand=True)

class EditorCanvas(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.data=0
		self.data_info = {}

		self.canvas = tk.Canvas(self, bg = "#2e2e2e")
		self.hbar=tk.Scrollbar(self,orient='horizontal')
		self.hbar.pack(side='bottom',fill='x')
		self.hbar.config(command=self.canvas.xview)
		self.vbar=tk.Scrollbar(self,orient='vertical')
		self.vbar.pack(side='right',fill='y')
		self.vbar.config(command=self.canvas.yview)
		self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
		self.canvas.pack(side = 'left', fill="both", expand=True)
		self.update()
		self.canvas.config(scrollregion=self.canvas.bbox("all"))
		
		#self.canvas.create_oval(0,0,10,10, activeoutline = "black" , outline=NODECOL, fill=NODECOL ,tags=("poop"))
		# this data is used to keep track of an 
		# item being dragged
		self._drag_data = {"relPos": {}, "item": None}
		self._new_conn_data = {"source": 0, "drain": 0, "type0": '', "type1": '', "port0": '', "port1": ''}
		self._selected = ''
		self._currentlyConnecting = False
		self.size = 12
		self._dragged = False
		self._inspector_active = False
		
		self.canvas.tag_bind("case||name||deco", "<ButtonPress-1>", self.on_token_press)
		self.canvas.tag_bind("case||name||deco", "<ButtonRelease-1>", self.on_token_release)
		self.canvas.tag_bind("case||name||deco", "<B1-Motion>", self.on_token_motion)
		self.canvas.tag_bind("inspector", "<ButtonPress-1>", self.on_inspector_click)
		self.canvas.tag_bind("port", "<ButtonPress-1>", self.on_port_press)
		self.canvas.tag_bind("conn", "<ButtonPress-1>", self.delete_line)
		self.canvas.bind("<Motion>", self.on_move)
		self.canvas.bind("<ButtonPress-1>", self.on_click)
	
	def _add_connections(self):
		for i in range(self.size):
			for j in range(self.size):
				if self.adjList[i][j]: #only the top right triangular half of the matrix
					fr = self.canvas.coords("id"+str(i))
					to = self.canvas.coords("id"+str(j))
					if not fr or not to: #ignores nonexistent nodes
						self.adjList[i][j] = None
						print("skipped:",i,j)
						break
					#print("conn:",i,j)
					w = fr[1]-fr[3]
					portName = str(i) + ',' + str(j)
					inport = (fr[2], fr[1] + PORT_OFF*(self.linePorts[portName][1])+TOTAL_OFF)
					outport = (to[0], to[1] + PORT_OFF*(self.linePorts[portName][0])+TOTAL_OFF)
					dist = min(abs(fr[2] - to[0])/4,75) #for curvature
					self.canvas.tag_lower(self.canvas.create_line(inport[0], inport[1], inport[0]+dist, inport[1], outport[0]-dist, outport[1], outport[0], outport[1], activefill = "white", width = LINE_WID, fill = LINE_COL, tags=("grapheditor", self.adjList[i][j], "conn"), smooth = True))

	def _draw_inspector(self, obj, eX,eY, overwrite = True):
		#print(self._drag_data)
		clickedOn = self.canvas.find_withtag("current")
		currentTags = self.canvas.gettags(clickedOn)
		id = int(currentTags[1][2:])
		if self._inspector_active and overwrite:
			self.canvas.delete("inspector")
		self._inspector_active = True
		x,y = self.canvas.canvasx(eX), self.canvas.canvasy(eY)
		inspWind = self.canvas.create_rectangle(x, y, x+10, y+10, outline=LINE_COL, fill=BASECOL, tags=("grapheditor","id"+str(id), "4pt", "inspwind", "inspector"))
		fieldOffset = 1
		maxWidth = 5
		name = obj.classname
		i = 0
		while i < len(name):
			if name[i] == '.':
				break
			i+=1
		else:
			i = -1;
		name = name[i+1:]
		canvasText = self.canvas.create_text(x+BORDER,y+BORDER+BOL_FONT[1],fill="white",font=BOL_FONT, text=name, anchor="w", tags=("grapheditor","id"+str(id), "2pt", "text", "inspector",))
		textBounds = self.canvas.bbox(canvasText)
		maxWidth = max(textBounds[2] - textBounds[0], maxWidth)
		for fields in obj.fields:
			field = obj.fields[fields]
			tags = ("grapheditor","id"+str(id), "2pt", "text",)
			if type(field) in (int, str, float, bool, None,):
				if fields == "code(6264)":
					text = "{" + fields + "}"
				else:
					text = fields + ": " + str(field)
			elif type(field) in (atoms.Atom,):
				text = "<" + fields + ">"
				tags+=(field.id, "nestedInsp")
			else:
				text = fields + ": invalid"
			tags+=("inspector",)
			canvasText = self.canvas.create_text(x+BORDER,y+BORDER+MED_FONT[1]*2*fieldOffset+MED_FONT[1],fill="white",font=MED_FONT, text=text, anchor="w", tags=tags)
			textBounds = self.canvas.bbox(canvasText)
			maxWidth = max(textBounds[2] - textBounds[0], maxWidth)
			fieldOffset += 1
		c = self.canvas.coords(inspWind)
		self.canvas.coords(inspWind, c[0], c[1], x+maxWidth+BORDER*2, y+fieldOffset*2*MED_FONT[1] + BORDER + MED_FONT[1])
		#print(id)
		#print(self.data_info[id])
	
	def on_inspector_click(self, event):
		clickedOn = self.canvas.find_withtag("current")
		tags = self.canvas.gettags(clickedOn)
		if "nestedInsp" in tags:
			#print(self.data_info)
			self._draw_inspector(self.data_info[int(tags[4])], event.x, event.y, False)

	def makeRect(self, className, x, y, id, name = None, w = 0, h = 0, nodesI = None, nodesO = None, b = BORDER, v_offset = TOTAL_OFF, vertical = False, center = False):
		if not nodesI:
			nodesI = nodes.list[className]['i']
		if not nodesO:
			nodesO = nodes.list[className]['o']
		if not w:
			if vertical:
				w = 30
			else:
				w = nodes.list[className]['w']
		if not h:
			if vertical:
				ports = max(nodesI, nodesO)
				h = (PORT_OFF)*(ports-1)+2*v_offset
			else:
				try:
					h = nodes.list[className]['h']
				except:
					ports = max(nodesI, nodesO)
					h = (PORT_OFF)*(ports-1)+2*v_offset
		if not name:
			if "name" in nodes.list[className]:
				name = nodes.list[className]["name"]
		if "vertical" in nodes.list[className]:
			vertical = True
		if "center" in nodes.list[className]:
			center = True
		if "shape" in nodes.list[className]: #doesnt work yet
			if nodes.list[className]['shape'] == "hex":
				hexOff = round(w/2/1.73205)
				self.canvas.create_polygon(x,y+h/2, x+hexOff,y, x+w-hexOff,y, x+w,y+h/2, x+w-hexOff,y+h, x+hexOff,y+h, activeoutline = "white" , outline=ACCCOL1, fill=ACCCOL1, tags=("grapheditor","id"+str(id), "6pt", "case"))
		else:
			self.canvas.create_rectangle(x, y, x+w, y+h, activeoutline = "white" , outline=ACCCOL1, fill=ACCCOL1, tags=("grapheditor","id"+str(id), "4pt", "case"))
		#self.canvas.create_rectangle(x+b, y+b, x+w-b, y+h-b , outline=ACCCOL1, fill=ACCCOL1, tags=("grapheditor","id"+str(id), "4pt", "deco"))
		if (name):
			if vertical:
				self.canvas.create_text(x+w/2,y+h/2,fill="white",font=MED_FONT, text=name, angle=90, tags=("grapheditor","id"+str(id), "2pt", "name"))
			elif center:
				self.canvas.create_text(x+w/2,y+h/2,fill="white",font=MED_FONT, text=name, tags=("grapheditor","id"+str(id), "2pt", "name"))
			else:
				self.canvas.create_text(x+b+DOT_SIZE,y+b,fill="white",font=MED_FONT, text=name, anchor="nw", tags=("grapheditor","id"+str(id), "2pt", "name"))
		for inports in range(nodesI):
			self.canvas.create_oval(x-DOT_SIZE, y+(PORT_OFF)*(inports)-DOT_SIZE+v_offset, x+DOT_SIZE, y+(PORT_OFF)*(inports)+DOT_SIZE+v_offset, activeoutline = "black" , outline=NODECOL, fill=NODECOL ,tags=("grapheditor","id"+str(id), "4pt", "port", "in", str(inports)))
		for outports in range(nodesO):
			self.canvas.create_oval(x+w-DOT_SIZE, y+(PORT_OFF)*(outports)-DOT_SIZE+v_offset, x+w+DOT_SIZE, y+(PORT_OFF)*(outports)+DOT_SIZE+v_offset, activeoutline = "black" , outline=NODECOL, fill=NODECOL ,tags=("grapheditor","id"+str(id), "4pt", "port", "out", str(outports)))
		#return nodesI, nodesO

	def on_token_press(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		self._drag_data["item"] = self.canvas.gettags(*self.canvas.find_closest(x, y))[1] #id is tags[1]
		self._dragged = False
		for item in self.canvas.find_withtag(self._drag_data["item"]):
			c = self.canvas.coords(item)
			if len(c) == 2:
				self._drag_data["relPos"][item] = [c[0] - x, c[1] - y]
			elif len(c) == 4:
				self._drag_data["relPos"][item] = [c[0] - x, c[1] - y, c[2] - x, c[3] - y]
			elif len(c) == 6:
				self._drag_data["relPos"][item] = [c[0] - x, c[1] - y, c[2] - x, c[3] - y, c[4] - x, c[5] - y]

	def on_token_release(self, event):
		if not self._dragged:
			id = int(self._drag_data["item"][2:])
			self._draw_inspector(self.data_info[id], event.x, event.y)
			print("clicked")
		self._drag_data["item"] = None
		self._drag_data["x"] = 0
		self._drag_data["y"] = 0

	def on_token_motion(self, event):
		self._dragged = True
		eX,eY = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		xOff, yOff = eX-event.x, eY-event.y
		idNum = int(self._drag_data["item"][2:])
		r = self._drag_data["relPos"][self.canvas.find_withtag(self._drag_data["item"]+"&&case")[0]]
		w = r[2]-r[0]
		h = r[3]-r[1]
		x = min(max(0+xOff,eX+r[0]), self.canvas.winfo_width()-w+xOff)
		y = min(max(0+yOff,eY+r[1]), self.canvas.winfo_height()-h+yOff)
		i = 0
		for inport in self.adjList[idNum]: #redraw incoming connections
			if inport:
				current = self.canvas.coords(inport)
				portName = str(idNum) + ',' + str(i)
				#print (inport)
				dist = min(abs(current[0] - current[6])/4,75) #for curvature
				new = (min(max(w+xOff,eX+r[2]), self.canvas.winfo_width()+xOff), y + PORT_OFF*(self.linePorts[portName][1])+TOTAL_OFF)
				self.canvas.coords(inport, new[0], new[1], new[0]+dist, new[1], current[6]-dist, current[7], current[6], current[7])
			i+=1
		i = 0
		for outportLists in self.adjList: #redraw outgoing connections
			outport = outportLists[idNum]
			if outport:
				current = self.canvas.coords(outport)
				portName = str(i) + ',' + str(idNum)
				#print (outport)
				dist = min(abs(current[0] - current[6])/4,75) #for curvature
				new = (x, y + PORT_OFF*(self.linePorts[portName][0])+TOTAL_OFF)
				self.canvas.coords(outport, current[0], current[1], current[0]+dist, current[1], new[0]-dist, new[1], new[0], new[1])
			i+=1
		for item in self.canvas.find_withtag(self._drag_data["item"]): #redraw cell
			tag = self.canvas.gettags(item)[2]
			localr = self._drag_data["relPos"][item]
			if tag == "2pt":
				self.canvas.coords(item, x-r[0]+localr[0], y-r[1]+localr[1])
			elif tag == "4pt":
				self.canvas.coords(item, x-r[0]+localr[0], y-r[1]+localr[1], x-r[0]+localr[2], y-r[1]+localr[3])
			elif tag == "6pt":
				self.canvas.coords(item, x-r[0]+localr[0], y-r[1]+localr[1], x-r[0]+localr[2], y-r[1]+localr[3], x-r[0]+localr[4], y-r[1]+localr[5])

	def delete_line(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		tags = self.canvas.gettags(*self.canvas.find_closest(x, y))
		if tags[1][:4] == "line":
			lineIndex = tags[1][4:]
			self.canvas.delete(tags[1])
			for i in range(self.size):
				if tags[1] in self.adjList[i]:
					for j in range(self.size):
						if self.adjList[i][j] == tags[1]:
							self.adjList[i][j] = None
							return

	def on_port_press(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		if self._currentlyConnecting:
			self._new_conn_data['drain'] = self.canvas.find_closest(x, y)
			drainTags = self.canvas.gettags(*self._new_conn_data['drain'])
			if 'port' in drainTags:
				self._new_conn_data['type1'] = drainTags[4]
				self._new_conn_data['port1'] = drainTags[5]
				if self._new_conn_data['type0'] == self._new_conn_data['type1']:
					return
				self.canvas.delete("connecting")
				c = self.canvas.coords(self._new_conn_data['source'])
				nX, nY = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
				d = self.canvas.coords(self._new_conn_data['drain'])
				toX, toY = (d[0] + d[2]) / 2, (d[1] + d[3]) / 2
				dist = min(abs(nX - toX)/4,75) #for curvature
				self.numLines += 1
				if self._new_conn_data['type0'] == 'in':
					self.canvas.tag_lower(self.canvas.create_line(toX, toY, toX+dist, toY, nX-dist, nY, nX, nY, activefill = "white", width = LINE_WID, fill = LINE_COL, smooth=True, tags=('grapheditor', 'line'+str(self.numLines), "conn")))
				elif self._new_conn_data['type0'] == 'out':
					self.canvas.tag_lower(self.canvas.create_line(nX, nY, nX+dist, nY, toX-dist, toY, toX, toY, activefill = "white", width = LINE_WID, fill = LINE_COL, smooth=True, tags=('grapheditor', 'line'+str(self.numLines), "conn")))
				sourceId = int(self.canvas.gettags(*self._new_conn_data['source'])[1][2:])
				drainId = int(drainTags[1][2:])
				drainPort = int(self._new_conn_data['port0'])
				sourcePort = int(self._new_conn_data['port1'])
				if self._new_conn_data['type0'] == 'in':
					sourceId, drainId = drainId, sourceId
					sourcePort, drainPort = drainPort, sourcePort
				self.adjList[sourceId][drainId] = 'line'+str(self.numLines)
				self.linePorts[str(sourceId) + ',' + str(drainId)] = (sourcePort,drainPort)
				#print(sourceId, drainId)
				self._currentlyConnecting = False
		else:
			self._new_conn_data['source'] = self.canvas.find_closest(x, y)
			tags = self.canvas.gettags(*self._new_conn_data['source'])
			if tags[3] == 'port':
				self._new_conn_data['type0'] = tags[4]
				self._new_conn_data['port0'] = tags[5]
				c = self.canvas.coords(self._new_conn_data['source'])
				nX, nY = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
				mX, mY = x, y
				dist = min(abs(nX - mX)/4,75) #for curvature
				if self._new_conn_data['type0'] == 'in':
					self.canvas.tag_lower(self.canvas.create_line(mX, mY, mX+dist, mY, nX-dist, nY, nX, nY, width=LINE_WID, fill='white', smooth=True, tags=('grapheditor', 'connecting')))
				elif self._new_conn_data['type0'] == 'out':
					self.canvas.tag_lower(self.canvas.create_line(nX, nY, nX+dist, nY, mX-dist, mY, mX, mY, width=LINE_WID, fill='white', smooth=True, tags=('grapheditor', 'connecting')))
				self._currentlyConnecting = True
		#print(self._currentlyConnecting)

	def on_move(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		if (self._currentlyConnecting):
			c = self.canvas.coords(self._new_conn_data['source'])
			nX, nY = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
			mX, mY = x, y
			dist = min(abs(c[0] - mX)/4,75) #for curvature
			if self._new_conn_data['type0'] == 'in':
				self.canvas.coords("connecting", mX, mY, mX+dist, mY, nX-dist, nY, nX, nY)
			elif self._new_conn_data['type0'] == 'out':
				self.canvas.coords("connecting", nX, nY, nX+dist, nY, mX-dist, mY, mX, mY)
			
			'''current = self.canvas.coords(outport)
			portName = str(i) + ',' + str(idNum)
			#print (outport)
			dist = min(abs(current[0] - current[6])/4,75) #for curvature
			new = (min(max(0,event.x+r[0]), self.canvas.winfo_width()-w), min(max(0,event.y+r[1]), self.canvas.winfo_height()-h) + PORT_OFF*(self.linePorts[portName][0])+TOTAL_OFF)
			self.canvas.coords(outport, current[0], current[1], current[0]+dist, current[1], new[0]-dist, new[1], new[0], new[1])'''

	def on_click(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		clickedOn = self.canvas.find_withtag("current")
		if self._currentlyConnecting:
			tags = self.canvas.gettags(*clickedOn)
			#print(clickedOn)
			if len(clickedOn) == 1 and "port" not in tags:
				self.canvas.delete("connecting")
				self._currentlyConnecting = False
		if clickedOn:
			#print("clicked on ",clickedOn)
			return
		#print("debug")
		if self._inspector_active:
			self.canvas.delete("inspector")
			self._inspector_active = False

	def load(self, file):
		self.data = file
		self.canvas.delete("all")
		self.size = 0
		self.numLines = 0
		objLocs = []
		objSize = []
		self.linePorts = {}
		self.adjList = []
		for i in range(self.size):
			self.adjList.append([])
			for j in range(self.size):
				self.adjList[i].append(None)
		#print(self.adjList)
		for eachField in ("child_components(173)","proxy_in_ports(177)","proxy_out_ports(178)"):
			children = self.data[1].fields[eachField]
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
					self._draw_atom(children[item])
					self.data_info[children[item].id] = children[item]
				self.addKids(children[item])
				item += 1
		#print(self.adjList)
		self._add_connections()
		#self.canvas.create_oval(0,0,10,10, activeoutline = "black" , outline=NODECOL, fill=NODECOL ,tags=("poop"))
		self.update()
		self.canvas.config(scrollregion=self.canvas.bbox("all"))

	def addKids(self, child):
		if not child:
			return
		try:
			for field in child.fields:
				if isinstance(child.fields[field], atoms.Atom):
					self.data_info[child.fields[field].id] = child.fields[field]
					self.addKids(child.fields[field])
		except:
			pass
		try:
			kids = child.fields["settings(6194)"].fields["inport_connections(614)"]
		except AttributeError:
			pass
			#print(child)
		except:
			pass
			#print(child.fields)
		else:
			inportConn = 0
			while(inportConn < len(kids)):
				try:
					kids[inportConn].fields["source_component(248)"].fields["settings(6194)"].fields["desktop_settings(612)"].fields["x(17)"]
				except AttributeError: #its a reference
					pass
					if kids[inportConn].fields["source_component(248)"]:
						self.size = max(self.size, max(kids[inportConn].fields["source_component(248)"].classNum,child.id)+1)
						while (len(self.adjList) < self.size):
							self.adjList.append([])
						for i in range(len(self.adjList)):
							while (len(self.adjList[i]) < self.size):
								self.adjList[i].append(None)
						self.adjList[kids[inportConn].fields["source_component(248)"].classNum][child.id] = "line"+str(self.numLines)
						self.linePorts[str(kids[inportConn].fields["source_component(248)"].classNum) + ',' + str(child.id)] = (inportConn, kids[inportConn].fields["outport_index(249)"])
						self.numLines += 1
				except:
					pass
					#print(kids[inportConn].fields)
				else:
					self._draw_atom(kids[inportConn].fields["source_component(248)"])
					self.data_info[kids[inportConn].fields["source_component(248)"].id] = kids[inportConn].fields["source_component(248)"]
					self.size = max(self.size, max(kids[inportConn].fields["source_component(248)"].id,child.id)+1)
					while (len(self.adjList) < self.size):
						self.adjList.append([])
					for i in range(len(self.adjList)):
						while (len(self.adjList[i]) < self.size):
							self.adjList[i].append(None)
					self.adjList[kids[inportConn].fields["source_component(248)"].id][child.id] = "line"+str(self.numLines)
					self.linePorts[str(kids[inportConn].fields["source_component(248)"].id) + ',' + str(child.id)] = (inportConn, kids[inportConn].fields["outport_index(249)"])
					self.numLines += 1
				self.addKids(kids[inportConn].fields["source_component(248)"])
				inportConn += 1

	def _draw_atom(self, obj):
		id = obj.id
		#print("id:",id)
		x = H_MULT*obj.fields["settings(6194)"].fields["desktop_settings(612)"].fields["y(18)"]
		y = V_MULT*obj.fields["settings(6194)"].fields["desktop_settings(612)"].fields["x(17)"]
		(nodesI, nodesO) = (0,0)
		(w,h) = (50,50)
		v_offset = TOTAL_OFF
		b = BORDER
		className = obj.classname
		
		#values
		if className ==  'float_core.decimal_value_atom(289)':
			name = obj.fields["name(374)"]
			val = obj.fields["value_type(702)"].fields["default_value(891)"]
			w,h = 4*b + 8*len(name),32+4*b+MED_FONT[1]
			self.makeRect(className, x, y, id, name=name, w=w, h=h)
			self.canvas.create_rectangle(x+b, y+3*b+MED_FONT[1], x+w-b, y+h-b , outline="#888", fill="#888", tags=("grapheditor","id"+str(id), "4pt", "deco"))
			#self.canvas.create_text(x+b+DOT_SIZE,y+b,fill="white",font=MED_FONT, text=name, anchor="nw", tags=("grapheditor","id"+str(id), "2pt", "name"))
			self.canvas.create_text(x+b+DOT_SIZE,y+(2*b+MED_FONT[1]+h)/2,fill="white",font=THK_FONT, text=str(val)[:7], anchor="w", tags=("grapheditor","id"+str(id), "2pt", "value"))
		elif className == 'float_core.boolean_value_atom(87)':
			name = obj.fields["name(374)"]
			val = obj.fields["value_type(702)"].fields["default_value(6957)"]
			w,h = 4*b + 8*len(name),32+4*b+MED_FONT[1]
			self.makeRect(className, x, y, id, name=name, w=w, h=h)
			self.canvas.create_rectangle(x+b, y+3*b+MED_FONT[1], x+w-b, y+h-b , outline="#888", fill="#888", tags=("grapheditor","id"+str(id), "4pt", "deco"))
			self.canvas.create_text(x+b+DOT_SIZE,y+(2*b+MED_FONT[1]+h)/2,fill="white",font=THK_FONT, text=str(val), anchor="w", tags=("grapheditor","id"+str(id), "2pt", "value"))
		elif className == 'float_core.indexed_value_atom(180)':
			name = obj.fields["name(374)"]
			val = obj.fields["value_type(702)"].fields["items(393)"][0].fields["name(651)"]
			vals = obj.fields["value_type(702)"].fields["items(393)"]
			(w,h) = (4*b + 8*len(name),50+MED_FONT[1])
			self.canvas.create_rectangle(x, y, x+w, y+h, activeoutline = "white" , outline="#888", fill="#888", tags=("grapheditor","id"+str(id), "4pt", "case"))
			self.canvas.create_rectangle(x+b, y+3*b+MED_FONT[1], x+w-b, y+h-b , outline="#aaa", fill="#aaa", tags=("grapheditor","id"+str(id), "4pt", "deco"))
			self.canvas.create_text(x+b+DOT_SIZE,y+b,fill="white",font=MED_FONT, text=name, anchor="nw", tags=("grapheditor","id"+str(id), "2pt", "name"))
			self.canvas.create_text(x+b+DOT_SIZE,y+(2*b+MED_FONT[1]+h)/2,fill="white",font=THK_FONT, text=str(val), anchor="w", tags=("grapheditor","id"+str(id), "2pt", "value"))
			nodesI = nodes.list[className]['i']
			nodesO = nodes.list[className]['o']
			#dropdown = DropDown()
			i = 0
			'''for val in vals:
				 btn = Button(text=val.fields["name(651)"], font_size='12sp', size_hint_y=None, height=20)
				 btn.bind(on_release=lambda btn: dropdown.select(btn.text))
				 dropdown.add_widget(btn)
				 i += 1'''
		elif className == 'float_core.integer_value_atom(394)':
			name = obj.fields["name(374)"]
			val = obj.fields["value_type(702)"].fields["default_value(6956)"]
			self.makeRect(className, x, y, id, name=name, w=4*b + 8*len(name), h=50+MED_FONT[1])
			self.canvas.create_rectangle(x+b, y+3*b+MED_FONT[1], x+w-b, y+h-b , outline="#aaa", fill="#aaa", tags=("grapheditor","id"+str(id), "4pt", "deco"))
			#self.canvas.create_text(x+b+DOT_SIZE,y+b,fill="white",font=MED_FONT, text=name, anchor="nw", tags=("grapheditor","id"+str(id), "2pt", "name"))
			self.canvas.create_text(x+b+DOT_SIZE,y+(2*b+MED_FONT[1]+h)/2,fill="white",font=THK_FONT, text=str(val), anchor="w", tags=("grapheditor","id"+str(id), "2pt", "value"))
		
		#constant values
		elif className == 'float_common_atoms.constant_value_atom(314)':
			val = str(obj.fields["constant_value(750)"])[:5]
			self.makeRect(className, x, y, id, h=50+MED_FONT[1])
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+MED_FONT[1],fill="white",font=THK_FONT, text=str(val), anchor="w",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
			return
		elif className == 'float_common_atoms.constant_integer_value_atom(298)':
			val = str(obj.fields["constant_value(720)"])
			self.makeRect(className, x, y, id, h=50+MED_FONT[1])
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+MED_FONT[1],fill="white",font=THK_FONT, text=str(val), anchor="w",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
			return
		elif className == 'constant_boolean_value_atom(635)':
			val = str(obj.fields["constant_value(2738)"])
			self.makeRect(className, x, y, id, h=50+MED_FONT[1])
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+MED_FONT[1],fill="white",font=THK_FONT, text=str(val), anchor="w",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
			return

		#atoms
		elif className == 'float_common_atoms.nitro_atom(1721)':
			name = 'nitro'
			val = obj.fields["code(6264)"]
			nodesI, nodesO = nitro.countIOs(val)
			if val[0:10] == 'component ':
				name = val[10:]
				i=0
				while name[i] not in ('\\', ' '):
					i+=1
				name = name[:i]
				val=val[16+i:]
			val = val[:20]
			(w,h) = (4*b + 8*len(name),50+MED_FONT[1])
			self.canvas.create_rectangle(x, y, x+w, y+h, activeoutline = "white" , outline="#888", fill="#888",
													tags=("grapheditor","id"+str(id), "4pt", "case"))
			self.canvas.create_rectangle(x+b, y+3*b+MED_FONT[1], x+w-b, y+h-b , outline="#aaa", fill="#aaa",
													tags=("grapheditor","id"+str(id), "4pt", "deco"))
			self.canvas.create_text(x+b+DOT_SIZE,y+b,fill="white",font=MED_FONT, text=name, anchor="nw",
											tags=("grapheditor","id"+str(id), "2pt", "name"))
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+MED_FONT[1],fill="white",font=CODEFONT, text=str(val), anchor="nw",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
		elif className == 'float_common_atoms.note_delay_compensation_atom(1435)':
			self.makeRect(className, x, y, id)
			
			self.canvas.create_oval(x+9,y+10,x+23,y+24, outline="#FAA", fill="#FAA",
											tags=("grapheditor", "id"+str(id), "4pt", "deco"))
			self.canvas.create_oval(x+41,y+10,x+27,y+24, outline="#FAA", fill="#FAA",
											tags=("grapheditor", "id"+str(id), "4pt", "deco"))
			self.canvas.create_oval(x+18,y+26,x+32,y+40, outline="#FAA", fill="#FAA",
											tags=("grapheditor", "id"+str(id), "4pt", "deco"))
			return
		elif className == 'float_common_atoms.delay_compensation_atom(1371)':
			self.makeRect(className, x, y, id)
			
			self.canvas.create_oval(x+9,y+10,x+23,y+24, outline="#FFF", fill="#FFF",
											tags=("grapheditor", "id"+str(id), "4pt", "deco"))
			self.canvas.create_oval(x+41,y+10,x+27,y+24, outline="#FFF", fill="#FFF",
											tags=("grapheditor", "id"+str(id), "4pt", "deco"))
			self.canvas.create_oval(x+18,y+26,x+32,y+40, outline="#FFF", fill="#FFF",
											tags=("grapheditor", "id"+str(id), "4pt", "deco"))
			return
		elif className == 'float_core.modulation_source_atom(766)':
			name = obj.fields["name(3639)"] + '\no->'
			(w,h) = (15 + 6*(len(name)-4),50+MED_FONT[1])
			self.makeRect(className, x, y, id, name, w=w, h=h)
		elif className == 'float_core.value_led_atom(189)':
			self.makeRect(className, x, y, '', id)
			w,h = nodes.list[className]['w'],nodes.list[className]['h']
			self.canvas.create_rectangle(x+b, y+b, x+w-b, y+h-b , outline="#ed5", fill="#ed5",
													tags=("grapheditor","id"+str(id), "4pt", "deco"))
			return

		#other atoms
		elif className == 'float_common_atoms.decimal_event_filter_atom(400)':
			name = 'decFilter'
			val1 = obj.fields["comparison(842)"]
			val2 = obj.fields["comparison_value(843)"]
			(w,h) = (4*b + 8*len(name),50+MED_FONT[1])
			self.makeRect(className, x, y, name, id, w=w, h=h)
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+MED_FONT[1],fill="white",font=THK_FONT, text=str(val1), anchor="w",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+2*MED_FONT[1],fill="white",font=THK_FONT, text=str(val2), anchor="w",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
		elif className == 'float_common_atoms.indexed_lookup_table_atom(344)':
			name = 'lookup'
			vals = obj.fields["row_data(744)"]
			length = obj.fields["row_count(743)"]
			name += '\n'
			for i in range(length):
				name += str(vals[i].fields["cells(726)"][0].fields["value(739)"]) + '|'
			width = 6*(len(name)-6)
			print("dothis.editor.238934")

		#math
		elif className == 'float_common_atoms.constant_add_atom(308)':
			self.makeRect(className, x, y, id)
			val = obj.fields["constant_value(750)"]
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+MED_FONT[1],fill="white",font=THK_FONT, text=str(val), anchor="w",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
			return
		elif className == 'float_common_atoms.constant_multiply_atom(303)':
			self.makeRect(className, x, y, id)
			val = obj.fields["constant_value(750)"]
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+MED_FONT[1],fill="white",font=THK_FONT, text=str(val), anchor="w",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
			return
		elif className == 'float_common_atoms.multiply_add_atom(304)':
			nodesI = obj.fields["multiplier_pairs(724)"]*2 + 1
			self.makeRect(className, x, y, id, nodesI=nodesI)
			return
		elif className == 'float_common_atoms.sum_atom(305)':
			nodesI = obj.fields["inputs(725)"]
			self.makeRect(className, x, y, id, nodesI=nodesI)
			return
			name =  str(val)

		#Buffers
		elif className in ('float_common_atoms.buffer_reader_atom(331)','float_common_atoms.buffer_writer_atom(364)'):
			w = nodes.list[className]['w']
			self.makeRect(className, x, y, id)
			self.canvas.create_text(x+w/2,y+h/2,fill="Yellow",font=THK_FONT, text='B', anchor="n", tags=("grapheditor","id"+str(id), "2pt", "name"))
			return

		#components
		elif className == 'float_core.proxy_in_port_component(154)':
			self.makeRect(className, x, y, id)
			w = nodes.list[className]['w']
			h = nodes.list[className]['h']
			name = obj.fields["port(301)"].fields["decorated_name(499)"]
			self.canvas.create_text(x+w/2,y+h/2,fill="white",font=THK_FONT, text=name[:2], anchor="center", tags=("grapheditor","id"+str(id), "2pt", "name"))
			self.canvas.create_polygon(x+10, y+v_offset, x, y+v_offset-7, x, y+v_offset+7, outline="#eee", fill="#eee",
												tags=("grapheditor","id"+str(id), "6pt", "deco"))
			return
			#val = obj.fields["port(301)"].fields["decorated_name(499)"]
			#name += '\n' + val
		elif className == 'float_core.proxy_out_port_component(50)':
			self.makeRect(className, x, y, id)
			w = nodes.list[className]['w']
			h = nodes.list[className]['h']
			name = obj.fields["port(301)"].fields["decorated_name(499)"]
			self.canvas.create_text(x+w/2,y+h/2,fill="white",font=THK_FONT, text=name[:2], anchor="center", tags=("grapheditor","id"+str(id), "2pt", "name"))
			self.canvas.create_polygon(x+w-10, y+v_offset, x+w, y+v_offset-7, x+w, y+v_offset+7, outline="#eee", fill="#eee",
												tags=("grapheditor","id"+str(id), "6pt", "deco"))
			return
			#val = obj.fields["port(301)"].fields["decorated_name(499)"]
			#name += '\n' + val
		elif className == 'float_core.nested_device_chain_slot(587)':
			name = obj.fields["name(835)"]
			b = BORDER
			(w,h) = (75,40)
			self.canvas.create_rectangle(x, y, x+w, y+h, activeoutline = "white" , outline=BASECOL, fill=BASECOL, tags=("grapheditor","id"+str(id), "4pt", "case"))
			self.canvas.create_rectangle(x+b, y+b, x+w-b, y+h-b , outline="#333", fill="#333", tags=("grapheditor","id"+str(id), "4pt", "deco"))
			self.canvas.create_text(x+b+DOT_SIZE,y+2*b,fill="white",font=THK_FONT, text=name, anchor="nw", tags=("grapheditor","id"+str(id), "2pt", "name"))
			nodesI = nodes.list[className]['i']
			nodesO = nodes.list[className]['o']
		elif className == 'float_core.nested_device_chain_slot(587)':
			name = obj.fields["name(835)"]
			b = BORDER
			(w,h) = (75,40)
			self.canvas.create_rectangle(x, y, x+w, y+h, activeoutline = "white" , outline=BASECOL, fill=BASECOL, tags=("grapheditor","id"+str(id), "4pt", "case"))
			self.canvas.create_rectangle(x+b, y+b, x+w-b, y+h-b , outline="#333", fill="#333", tags=("grapheditor","id"+str(id), "4pt", "deco"))
			self.canvas.create_text(x+b+DOT_SIZE,y+2*b,fill="white",font=THK_FONT, text=name, anchor="nw", tags=("grapheditor","id"+str(id), "2pt", "name"))
			nodesI = nodes.list[className]['i']
			nodesO = nodes.list[className]['o']
		elif className in nodes.list:
			self.makeRect(className, x, y, id)
			return
		else:
			color = "#"+("%06x"%random.randint(0,16777215))
			(w,h) = (100,50)
			self.canvas.create_rectangle(x, y, x+w, y+h, activeoutline = "white" , outline=color, fill=color, tags=("grapheditor","id"+str(id), "4pt", "case"))
			self.canvas.create_text(x+3+DOT_SIZE,y+3,fill="white",font=MED_FONT, text=className+" id:"+str(id), anchor="nw", tags=("grapheditor","id"+str(id), "2pt", "name"))
		for inports in range(nodesI):
			self.canvas.create_oval(x-DOT_SIZE, y+(PORT_OFF)*(inports)-DOT_SIZE+v_offset, x+DOT_SIZE, y+(PORT_OFF)*(inports)+DOT_SIZE+v_offset, activeoutline = "black" , outline=NODECOL, fill=NODECOL ,tags=("grapheditor","id"+str(id), "4pt", "port", "in", str(inports)))
		for outports in range(nodesO):
			self.canvas.create_oval(x+w-DOT_SIZE, y+(PORT_OFF)*(outports)-DOT_SIZE+v_offset, x+w+DOT_SIZE, y+(PORT_OFF)*(outports)+DOT_SIZE+v_offset, activeoutline = "black" , outline=NODECOL, fill=NODECOL ,tags=("grapheditor","id"+str(id), "4pt", "port", "out", str(outports)))
		doth = (PORT_OFF)*(max(nodesI,nodesO))+v_offset #whichever type of port there are more of
		if doth > h:
			current = self.canvas.coords("id"+str(id)+"&&case")
			self.canvas.coords("id"+str(id)+"&&case", current[0], current[1], current[2], y+doth)

app = Application()
app.mainloop()