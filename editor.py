import tkinter as tk
import random
import math
import copy
from tkinter import ttk
from tkinter import filedialog
from src import decoder, encoder
from src.lib import fs, util, atoms
from src.lib.luts import nodes, typeLists, enums
from src.nitro import nitro
import os

DEBUG = False

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
ACCCOL2 = "#888"
ACCCOL3 = "#3dd9ff"
INSP_WIDTH = 50

class Application(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		
		try:
			tk.Tk.iconbitmap(self, default="bwEdit.ico")
		except:
			try:
				tk.Tk.iconbitmap(self, default="@bwEdit.xbm")
			except:
				pass
		tk.Tk.wm_title(self, "bwEdit")
		
		top = self.winfo_toplevel() #menu bar
		self.menuBar = tk.Menu(top)
		top['menu'] = self.menuBar
		self.subMenu = tk.Menu(self.menuBar, tearoff=0) #file
		self.menuBar.add_cascade(label='File', menu=self.subMenu)
		self.subMenu.add_command(label='Save As', command=self.savefile)
		self.subMenu.add_command(label='Load', command=self.openfile)
		self.subMenu.add_command(label='Export to JSON', command=self.exportfile)
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
			r = readThis.read()
			#self.frames[MainPage].editor.header = r[:24]
			f = decoder.bwDecode(r)
		self.frames[MainPage].editor.load(f)

	def savefile(self):
		self.frames[MainPage].editor.treeifyData()
		with tk.filedialog.asksaveasfile(mode='wb', defaultextension=".bw") as f:
			if f is None: #in case of cancel
				return
			header = self.frames[MainPage].editor.header
			header = header[:11] + '2' + header[12:]
			output = header.encode('utf-8') + encoder.bwEncode(self.frames[MainPage].editor.data)
			f.write(output)

	def exportfile(self): #same as save except it serializes the json instead of encoding it
		self.frames[MainPage].editor.treeifyData()
		with tk.filedialog.asksaveasfile(mode='wb', defaultextension=".bw") as f:
			if f is None: #in case of cancel
				return
			header = self.frames[MainPage].editor.header
			output = ''
			for item in self.frames[MainPage].editor.data:
				output += util.json_encode(atoms.serialize(item))
			output = header + decoder.reformat(output)
			f.write(output.encode("utf-8"))

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
		#self.data_info = {}
		self.header = 'BtWg00010001008d000016a00000000000000000'

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
		#self._new_conn_data = {"start": 0, "end": 0, "type0": '', "type1": '', "port0": '', "port1": ''}
		self._new_conn_data = {}
		self._selected = ''
		self._currentlyConnecting = False
		self.size = 12
		self._dragged = False
		self._inspector_active = False
		self._rclicked = None
		self._manager_active = False
		self._input_active = False
		
		self.canvas.tag_bind("case||name||deco", "<ButtonPress-1>", self._on_atom_press)
		self.canvas.tag_bind("case||name||deco", "<ButtonRelease-1>", self._on_atom_release)
		self.canvas.tag_bind("case||name||deco", "<B1-Motion>", self._on_atom_motion)
		self.canvas.tag_bind("case||name||deco", "<ButtonPress-3>", self.on_atom_rc_press)
		self.canvas.tag_bind("case||name||deco", "<ButtonRelease-3>", self.on_atom_rc_release)
		self.canvas.tag_bind("delete", "<ButtonPress-1>", self._on_del_press)
		self.canvas.tag_bind("delete", "<ButtonRelease-1>", self._on_del_release)
		self.canvas.tag_bind("exportnitro", "<ButtonPress-1>", self._on_export_nitro_press)
		self.canvas.tag_bind("exportnitro", "<ButtonRelease-1>", self._on_export_nitro_release)
		self.canvas.tag_bind("inspector", "<ButtonPress-1>", self.on_inspector_click)
		self.canvas.tag_bind("port", "<ButtonPress-1>", self.on_port_press)
		self.canvas.tag_bind("conn", "<ButtonPress-1>", self.delete_line)
		self.canvas.bind("<Motion>", self.on_move)
		self.canvas.bind("<ButtonPress-1>", self.on_click)
		self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
		self.canvas.bind_all("<ButtonPress-2>", self._on_mc_press)
		self.canvas.bind_all("<B2-Motion>", self._on_mc_motion)
		self.canvas.bind_all("<Return>", self._on_enter)
	
	def _on_mousewheel(self, event):
		self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

	def _on_mc_press(self, event):
		self.canvas.scan_mark(event.x, event.y)
	def _on_mc_motion(self, event):
		self.canvas.scan_dragto(event.x, event.y, gain=1)

	def _add_connections(self):
		for dID in range(len(self.portList)):
			atoms = self.portList[dID]
			if atoms:
				for dPort in range(len(atoms)):
					inports = atoms[dPort]
					if inports:
						sID = inports[0]
						sPort = inports[1]
						fr = self.canvas.coords("id"+str(sID))
						to = self.canvas.coords("id"+str(dID))
						if not fr or not to: #ignores nonexistent nodes
							print("skipped:",dID,sID)
							continue
						name = str(dID) + ':' + str(dPort) + ',' + str(sID) + ':' + str(sPort)
						sCoord = (fr[2], fr[1] + PORT_OFF*(sPort)+TOTAL_OFF)
						dCoord = (to[0], to[1] + PORT_OFF*(dPort)+TOTAL_OFF)
						dist = min(abs(fr[2] - to[0])/4,75) #for curvature
						self.canvas.tag_lower(self.canvas.create_line(sCoord[0], sCoord[1], sCoord[0]+dist, sCoord[1], dCoord[0]-dist, dCoord[1], dCoord[0], dCoord[1],
														activefill = "white", width = LINE_WID, fill = LINE_COL, tags=("grapheditor", name, "conn"), smooth = True))
		return
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
					self.canvas.tag_lower(self.canvas.create_line(inport[0], inport[1], inport[0]+dist, inport[1], outport[0]-dist, outport[1], outport[0], outport[1],
													activefill = "white", width = LINE_WID, fill = LINE_COL, tags=("grapheditor", self.adjList[i][j], "conn"), smooth = True))

	def _draw_inspector(self, obj, eX,eY, overwrite = True):
		#print(self._drag_data)
		clickedOn = self.canvas.find_withtag("current")
		currentTags = self.canvas.gettags(clickedOn)
		#id = int(currentTags[1][2:])
		id = obj.id
		if overwrite:
			self.canvas.delete("inspector")
			self.listList = []
			self.listNum = 0
		self.canvas.delete("manager")
		self._manager_active = False
		self._inspector_active = True
		x,y = self.canvas.canvasx(eX), self.canvas.canvasy(eY)
		inspWind = self.canvas.create_rectangle(x, y, x+10, y+10, outline=LINE_COL, fill=BASECOL, tags=("grapheditor","id"+str(id), "4pt", "inspwind", "inspector")) #id might be problematic for lists
		maxWidth = 5
		print(currentTags)
		if "n_list" in currentTags:
			fieldOffset = 0
			iterate = obj
			print(iterate)
		else:
			fieldOffset = 1
			name = obj.classname
			i = 0
			while i < len(name):
				if name[i] == '.':
					break
				i+=1
			else:
				i = -1;
			name = name[i+1:] + " id: " + str(obj.id)
			canvasText = self.canvas.create_text(x+BORDER,y+BORDER+BOL_FONT[1],fill="white",font=BOL_FONT, text=name, anchor="w", tags=("grapheditor","id"+str(id), "2pt", "text", "inspector",))
			textBounds = self.canvas.bbox(canvasText)
			maxWidth = max(textBounds[2] - textBounds[0], maxWidth)
			iterate = obj.fields
		for fields in iterate: #TODO clean this up
			tags = ("grapheditor","id"+str(id), "2pt", "text",)
			if "n_list" in currentTags:
				if type(fields) in (int, str, float, bool, None,):
					if fields == "code(6264)":
						text = "{" + fields + "}"
					else:
						text = fields
				elif type(fields) in (atoms.Atom,):
					if fields.classname == "float_core.inport_connection(105)":
						text = fields.fields["source_component(248)"].id
					else:
						text = "<" + fields.classname + ">"
					tags+=(fields.id, "nestedInsp",)
				elif type(fields) in (atoms.Reference,):
					if self.atomList[fields.id].classname == "float_core.inport_connection(105)":
						text = self.atomList[fields.id].fields["source_component(248)"].id
					else:
						text = "<" + self.atomList[fields.id].classname + ">"
					tags+=(fields.id, "nestedInsp",)
				elif type(fields) in (list,):
					text = "[" + fields + "]"
					self.listList.append(fields)
					tags+=(str(self.listNum), "nestedInsp", "n_list",)
					self.listNum+=1
				else:
					print(type(fields))
					text = fields + ": invalid"
			else:
				field = obj.fields[fields]
				if type(field) in (int, str, float, bool, None,):
					if fields == "code(6264)":
						text = "{" + fields + "}"
					elif fields in enums.usesUnits:
						text = fields + ": " + str(enums.units[field])
					else:
						text = fields + ": " + str(field)
					tags += ("variable", fields)
				elif type(field) in (atoms.Atom, atoms.Reference):
					text = "<" + fields + ">"
					tags+=(field.id, "nestedInsp",)
				elif type(field) in (list,):
					print(field)
					text = "[" + fields + "]"
					self.listList.append(field)
					tags+=(str(self.listNum), "nestedInsp", "n_list",)
					self.listNum+=1
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
		if "variable" in tags:
			x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
			id = int(tags[1][2:])
			field = tags[5]
			self._draw_modifier(id, x, y, field)
			self._input_active = True
		elif "nestedInsp" in tags:
			#print(self.data_info)
			if "n_list" in tags:
				self._draw_inspector(self.listList[int(tags[4])], event.x, event.y, False)
			else:
				self._draw_inspector(self.atomList[int(tags[4])], event.x, event.y, False)
	
	def _on_enter(self, event):
		print("enter")
		if self._input_active:
			#parse the input
			fieldNum = int(''.join([s for s in self._input_data[1] if s.isdigit()]))
			print(fieldNum)
			type = typeLists.fieldList[fieldNum]
			if type == 1:
				self.atomList[self._input_data[0]].fields[self._input_data[1]] = int(self._input.get())
			elif type == 5:
				new = True
				if self._input.get().tolower() in ('0','f','false','',):
					new = False
				self.atomList[self._input_data[0]].fields[self._input_data[1]] = bool(new)
			elif type == 6 or type == 7:
				self.atomList[self._input_data[0]].fields[self._input_data[1]] = float(self._input.get())
			elif type == 8:
				self.atomList[self._input_data[0]].fields[self._input_data[1]] = str(self._input.get())
			else:
				print("modification of this parameter is not yet permitted")
			self.canvas.delete("input")
			self._input_active = False
			#TODO redraw inspector?
	
	def _draw_modifier(self, id, x, y, field,):
		self.canvas.delete("input")
		self._input = tk.Entry(self.canvas)
		self.canvas.create_window(x, y, window = self._input, anchor = "nw", tags = ("grapheditor","id"+str(id), "2pt", "input",))
		self._input_data = (id, field,)
		#print(id)
		#print("mod", self.atomList[id].fields[field])

	def makeRect(self, className, x, y, id, name = None, w = 0, h = 0, nodesI = None, nodesO = None, b = BORDER, v_offset = TOTAL_OFF, vertical = False, center = False):
		if "vertical" in nodes.list[className]:
			vertical = True
		if "center" in nodes.list[className]:
			center = True
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

	def _on_atom_press(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		self._drag_data["item"] = self.canvas.gettags(self.canvas.find_withtag("current"))[1] #id is tags[1]
		self._dragged = False
		for item in self.canvas.find_withtag(self._drag_data["item"]):
			c = self.canvas.coords(item)
			output = []
			xySelect = True
			for i in c:
				output.append(i-(x if xySelect else y))
				xySelect = not xySelect
			self._drag_data["relPos"][item] = output

	def _on_atom_release(self, event):
		if self._dragged:
			#add layer correction (atoms with a smaller y position should be on a lower canvas layer)
			rPos = self._drag_data["relPos"][self.canvas.find_withtag(self._drag_data["item"]+"&&case")[0]]
			idNum = int(self._drag_data["item"][2:])
			atomX, atomY = self.canvas.canvasx(event.x)+rPos[0], self.canvas.canvasy(event.y)+rPos[1]
			self.atomList[self.atomList[self.atomList[idNum].fields["settings(6194)"].id].fields["desktop_settings(612)"].id].fields["y(18)"] = int(atomX/H_MULT)
			self.atomList[self.atomList[self.atomList[idNum].fields["settings(6194)"].id].fields["desktop_settings(612)"].id].fields["x(17)"] = int(atomY/V_MULT)
		else:
			id = int(self._drag_data["item"][2:])
			self._draw_inspector(self.atomList[id], event.x, event.y)
			#print("clicked")
		self._drag_data["item"] = None
		self._drag_data["x"] = 0
		self._drag_data["y"] = 0

	def _on_atom_motion(self, event):
		self._dragged = True
		eX,eY = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		xOff, yOff = eX-event.x, eY-event.y
		idNum = int(self._drag_data["item"][2:])
		rPos = self._drag_data["relPos"][self.canvas.find_withtag(self._drag_data["item"]+"&&case")[0]]
		w = rPos[2]-rPos[0]
		h = rPos[3]-rPos[1]
		x = min(max(0+xOff,eX+rPos[0]), self.canvas.winfo_width()-w+xOff)
		y = min(max(0+yOff,eY+rPos[1]), self.canvas.winfo_height()-h+yOff)
		if len(self.portList) > idNum:
			for i in range(len(self.portList[idNum])): #redraw incoming connections
				inport = self.portList[idNum][i]
				if inport:
					name = str(idNum) + ':' + str(i) + ',' + str(inport[0]) + ':' + str(inport[1])
					#print("i", name)
					current = self.canvas.coords(name)
					dist = min(abs(current[0] - current[6])/4,75) #for curvature
					newC = (x, y + PORT_OFF*(i)+TOTAL_OFF)
					self.canvas.coords(name, current[0], current[1], current[0]+dist, current[1], newC[0]-dist, newC[1], newC[0], newC[1])
		if len(self.RortList) > idNum:
			for o in range(len(self.RortList[idNum])): #redraw outgoing connections
				outportList = self.RortList[idNum][o]
				if outportList:
					for outport in outportList:
						name = str(outport[0]) + ':' + str(outport[1]) + ',' + str(idNum) + ':' + str(o)
						#print("o", name)
						current = self.canvas.coords(name)
						dist = min(abs(current[0] - current[6])/4,75) #for curvature
						newC = (x + w, y + PORT_OFF*(o)+TOTAL_OFF)
						self.canvas.coords(name, newC[0], newC[1], newC[0]+dist, newC[1], current[6]-dist, current[7], current[6], current[7])
		for item in self.canvas.find_withtag(self._drag_data["item"]): #redraw cell
			tag = self.canvas.gettags(item)[2]
			localr = self._drag_data["relPos"][item]
			newC = []
			xySelect = True
			for i in localr:
				newC.append((x-rPos[0] if xySelect else y-rPos[1])+i)
				xySelect = not xySelect
			self.canvas.coords(item, *newC)

	def on_atom_rc_press(self, event):
		rclicked = self.canvas.find_withtag("current")
		self._rclicked = rclicked
		print(rclicked)
	
	def on_atom_rc_release(self, event):
		rclicked = self.canvas.find_withtag("current")
		if rclicked == self._rclicked:
			id = int(self.canvas.gettags(rclicked)[1][2:])
			self._draw_manager(self.atomList[id], event.x, event.y)
		self._rclicked = None
		print(rclicked)

	def _on_del_press(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		clicked = self.canvas.find_closest(x, y)
		self._deleting = clicked
	
	def _on_del_release(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		clicked = self.canvas.find_closest(x, y)
		if clicked == self._deleting:
			id = int(self.canvas.gettags(clicked)[1][2:])
			self.delAtom(id)
		self._deleting = None
		
	def _on_export_nitro_press(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		clicked = self.canvas.find_closest(x, y)
		self._exporting_nitro = clicked
	
	def _on_export_nitro_release(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		clicked = self.canvas.find_closest(x, y)
		if clicked == self._exporting_nitro:
			id = int(self.canvas.gettags(clicked)[1][2:])
			output = self.atomList[id].fields["code(6264)"].replace('\\n','\n')
			with tk.filedialog.asksaveasfile(mode='w', defaultextension=".nitro") as f:
				if f is None: #in case of cancel
					self._exporting_nitro = None
					return
				f.write(output)

		self._exporting_nitro = None
	
	def _draw_manager(self, obj, eX,eY):
		clickedOn = self.canvas.find_withtag("current")
		currentTags = self.canvas.gettags(clickedOn)
		id = int(currentTags[1][2:])
		self.canvas.delete("manager")
		self.canvas.delete("inspector")
		self._manager_active = True
		self._inspector_active = True
		self._currently_managed = True
		x,y = self.canvas.canvasx(eX), self.canvas.canvasy(eY)
		manaWind = self.canvas.create_rectangle(x, y, x+10, y+10, outline=ACCCOL3, fill=BASECOL, tags=("grapheditor","id"+str(id), "4pt", "manawind", "manager")) #id might be problematic for lists
		maxWidth = 5
		fieldOffset = 1
		
		#add name
		name = obj.classname
		i = 0
		while i < len(name):
			if name[i] == '.':
				break
			i+=1
		else:
			i = -1;
		name = name[i+1:] + " id: " + str(obj.id)
		canvasText = self.canvas.create_text(x+BORDER,y+BORDER+BOL_FONT[1],fill="white",font=BOL_FONT, text=name, anchor="w",
															tags=("grapheditor","id"+str(id), "2pt", "text", "manager",))
		textBounds = self.canvas.bbox(canvasText)
		maxWidth = max(textBounds[2] - textBounds[0], maxWidth)
		
		#add delete TODO don't render delete button for inports
		text = self.canvas.create_text(x+BORDER,y+MED_FONT[1]*2*fieldOffset+BOL_FONT[1],fill="white",font=MED_FONT, text="DELETE ATOM", anchor="w",
															tags=("grapheditor","id"+str(id), "2pt", "text", "delete", "manager",))
		textBounds = self.canvas.bbox(text)
		maxWidth = max(textBounds[2] - textBounds[0], maxWidth)
		fieldOffset += 1
		
		#add code export for nitro
		if obj.classname == 'float_common_atoms.nitro_atom(1721)':
			text = self.canvas.create_text(x+BORDER,y+MED_FONT[1]*2*fieldOffset+BOL_FONT[1],fill="white",font=MED_FONT, text="Export nitro code", anchor="w",
																tags=("grapheditor","id"+str(id), "2pt", "text", "exportnitro", "manager",))
			textBounds = self.canvas.bbox(text)
			maxWidth = max(textBounds[2] - textBounds[0], maxWidth)
			fieldOffset += 1
		
		#resize manager window to text
		c = self.canvas.coords(manaWind)
		self.canvas.coords(manaWind, c[0], c[1], x+maxWidth+BORDER*2, y+fieldOffset*2*MED_FONT[1] + BORDER + BOL_FONT[1])
		#print(id)
		#print(self.data_info[id])

	def delete_line(self, event): #deletes the connection that is currently being clicked on
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		tags = self.canvas.gettags(self.canvas.find_withtag("current"))
		if "conn" in tags:
			#delete drawn connection
			lineIndex = tags[1]
			self.canvas.delete(tags[1])
			
			#delete from port list
			connData = [int(x) for x in lineIndex.replace(':',',').split(',')]
			self.delPort(*connData)
			self.atomList[self.atomList[self.atomList[connData[0]].fields["settings(6194)"].id].fields["inport_connections(614)"][connData[1]].id].fields["source_component(248)"] = None
			self.atomList[self.atomList[self.atomList[connData[0]].fields["settings(6194)"].id].fields["inport_connections(614)"][connData[1]].id].fields["outport_index(249)"] = 0

	def on_port_press(self, event): #begins or completes a connection
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		if self._currentlyConnecting:
			self._new_conn_data['end'] = self.canvas.find_closest(x, y)
			drainTags = self.canvas.gettags(*self._new_conn_data['end'])
			if 'port' in drainTags:
				#set variables
				self._new_conn_data['typeE'] = drainTags[4]
				self._new_conn_data['portE'] = drainTags[5]
				if self._new_conn_data['typeS'] == self._new_conn_data['typeE']: #check to ensure ports go from in to out
					return
				
				#set all my source and drain variables
				sID, dID = int(self.canvas.gettags(*self._new_conn_data['start'])[1][2:]), int(drainTags[1][2:])
				sPort, dPort = int(self._new_conn_data['portS']), int(self._new_conn_data['portE'])
				sPos, dPos = self.canvas.coords(self._new_conn_data['start']), self.canvas.coords(self._new_conn_data['end'])
				if self._new_conn_data['typeS'] == 'in':
					sID, dID = dID, sID
					sPort, dPort = dPort, sPort
					sPos, dPos = dPos, sPos
				
				if len(self.portList) > dID:
					if len(self.portList[dID]) > dPort:
						if self.portList[dID][dPort]: #check to make sure only one in connection per port
							return
				
				#draw new connection
				self.canvas.delete("connecting")
				sX, sY, dX, dY = (sPos[0] + sPos[2]) / 2, (sPos[1] + sPos[3]) / 2,   (dPos[0] + dPos[2]) / 2, (dPos[1] + dPos[3]) / 2
				dist = min(abs(sX - dX)/4,75) #for curvature
				name = str(dID) + ':' + str(dPort) + ',' + str(sID) + ':' + str(sPort)
				self.canvas.tag_lower(self.canvas.create_line(sX, sY, sX+dist, sY, dX-dist, dY, dX, dY,
												activefill = "white", width = LINE_WID, fill = LINE_COL, smooth=True, tags=('grapheditor', name, "conn")))
				
				self.addPort(dID,dPort,sID,sPort)
				#add stuff to extend the size of the inport conn list in case there arent enough inport conns
				self.atomList[self.atomList[self.atomList[dID].fields["settings(6194)"].id].fields["inport_connections(614)"][dPort].id].fields["source_component(248)"] = atoms.Reference(sID)
				self.atomList[self.atomList[self.atomList[dID].fields["settings(6194)"].id].fields["inport_connections(614)"][dPort].id].fields["outport_index(249)"] = sPort
				self._currentlyConnecting = False
		else:
			self._new_conn_data['start'] = self.canvas.find_closest(x, y)
			tags = self.canvas.gettags(*self._new_conn_data['start'])
			if tags[3] == 'port':
				#set variables
				self._new_conn_data['typeS'] = tags[4]
				self._new_conn_data['portS'] = tags[5]
				
				#find coords
				c = self.canvas.coords(self._new_conn_data['start'])
				nX, nY = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
				mX, mY = x, y
				if self._new_conn_data['typeS'] == 'in':
					nX, nY, mX, mY = mX, mY, nX, nY
				
				#draw pending connection
				dist = min(abs(nX - mX)/4,75) #for curvature
				self.canvas.tag_lower(self.canvas.create_line(nX, nY, nX+dist, nY, mX-dist, mY, mX, mY,
												width=LINE_WID, fill='white', smooth=True, tags=('grapheditor', 'connecting')))
				
				self._currentlyConnecting = True

	def on_move(self, event): #redraws pending connection
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		if (self._currentlyConnecting):
			#find coords
			c = self.canvas.coords(self._new_conn_data['start'])
			nX, nY = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
			mX, mY = x, y
			
			#move pending connection
			dist = min(abs(c[0] - mX)/4,75) #for curvature
			if self._new_conn_data['typeS'] == 'in':
				nX, nY, mX, mY = mX, mY, nX, nY
			self.canvas.coords("connecting", nX, nY, nX+dist, nY, mX-dist, mY, mX, mY)

	def on_click(self, event):
		x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		clickedOn = self.canvas.find_withtag("current")
		if self._currentlyConnecting:
			tags = self.canvas.gettags(*clickedOn)
			if len(clickedOn) == 1 and "port" not in tags:
				self.canvas.delete("connecting")
				self._currentlyConnecting = False
		if clickedOn:
			return
		if self._inspector_active:
			self.canvas.delete("inspector")
			self._inspector_active = False
			self.canvas.delete("input")
		if self._manager_active:
			self.canvas.delete("manager")
			self._manager_active = False

	def load(self, file):
		self.data = file
		self.canvas.delete("all")
		self.size = 0
		self.numLines = 0
		objLocs = []
		objSize = []
		self.linePorts = {}
		self._currentlyConnecting = False
		
		self.buffers = []
		self.inports = []

		self.atomList = []
		self.portList = []
		self.RortList = []
		self.paneList = []
		self.panelMap = [] #index is object, stores list of references

		#flatten data
		for eachField in ("child_components(173)","panels(6213)","proxy_in_ports(177)","proxy_out_ports(178)"):
			for item in range(len(self.data[1].fields[eachField])):
				if isinstance(self.data[1].fields[eachField][item], atoms.Atom):
					self.atomList.append(self.data[1].fields[eachField][item])
		self.flattenData(self.atomList, True)
		
		#draw atoms and add connections
		for item in self.atomList:
			if item:
				self.drawKids(item)
		
		#draw connections
		self._add_connections()
		
		#update scroll region
		self.update()
		sr = self.canvas.bbox("all")
		print(sr)
		p = 600
		sr = (sr[0]-p,sr[1]-p,sr[2]+p,sr[3]+p,)
		self.canvas.config(scrollregion=sr)

	def drawKids(self, child,):
		if isinstance(child, atoms.Atom):
			if "settings(6194)" in child.fields:#if its a regular atom
				self._draw_atom(child)
				kid = self.atomList[child.fields["settings(6194)"].id].fields["inport_connections(614)"]
				inportCount = 0
				for i in kid:
					inportConn = self.atomList[i.id]
					if inportConn.fields["source_component(248)"]:
						obj = self.atomList[inportConn.fields["source_component(248)"].id]
						if isinstance(obj, atoms.Atom):
							if "settings(6194)" in obj.fields:
								self.addPort(child.id, inportCount, obj.id, inportConn.fields["outport_index(249)"])
					inportCount += 1
			elif "layout_settings(6226)" in child.fields:
				if "data_model(6220)" in child.fields and child.fields["data_model(6220)"]:#if it depends on a control
					id = child.fields["data_model(6220)"].id
					while len(self.panelMap) < id+1:
						self.panelMap.append([])
					self.panelMap[id].append(self.atomList.index(child))

	def addPort(self, dID, dPort, sID, sPort,): #d is drain, s is source
		listLengths = max(sID+1,dID+1)
		while len(self.portList) < listLengths:
			self.portList.append([])
		while len(self.portList[dID]) < dPort+1:
			self.portList[dID].append(0)
		self.portList[dID][dPort] = (sID, sPort)
		
		while len(self.RortList) < listLengths:
			self.RortList.append([])
		while len(self.RortList[sID]) < sPort+1:
			self.RortList[sID].append([])
		self.RortList[sID][sPort].append((dID, dPort))
		
	def delPort(self, dID, dPort, sID, sPort,): #d is drain, s is source
		#print(dID, dPort, sID, sPort)
		if self.portList[dID][dPort] == (sID,sPort):
			self.portList[dID][dPort] = 0
		else:
			print("jerror: source doesn't match drain. (400)")
		
		if (dID,dPort) in self.RortList[sID][sPort]:
			self.RortList[sID][sPort].remove((dID, dPort))
		else:
			print("jerror: source doesn't match drain. (400)")
		self.canvas.delete(str(dID) +':'+ str(dPort) +','+ str(sID) +':'+ str(sPort))
	
	def delAtom(self, id):
		#delete the ports
		print(self.RortList)
		if len(self.portList) > id:
			for port in range(len(self.portList[id])):
				if self.portList[id][port]:
					self.delPort(id, port, *self.portList[id][port])
		if len(self.RortList) > id:
			for port in range(len(self.RortList[id])):
				if self.RortList[id][port]:
					for conn in range(len(self.RortList[id][port])):
						if self.RortList[id][port][conn]:
							print(self.RortList[id][port][conn])
							rConn = self.atomList[self.atomList[self.RortList[id][port][conn][0]].fields["settings(6194)"].id].fields["inport_connections(614)"][self.RortList[id][port][conn][1]]
							self.atomList[rConn.id].fields["source_component(248)"] = None
							#print(self.RortList[id][port])
							self.delPort(*self.RortList[id][port][conn], id, port,)
		
		#delete and erase the atom
		self.atomList[id] = None
		self.canvas.delete("id"+str(id))
		
		#delete panel mappings
		if len(self.panelMap) > id:
			for i in self.panelMap[id]:
				self.atomList[i].fields["data_model(6220)"] = None
		
		#delete inport source components
		
		#close manager
		self.canvas.delete("manager")
		print("delete")
	
	def flattenData(self, data, isRoot = False):
		if isinstance(data, list):
			if isRoot:
				self.atomList = []
			output = []
			for eachClass in range(len(data)):
				#self.flattenData(data[eachClass])
				output.append(self.flattenData(data[eachClass])) #automatically checks type in the function
			if isRoot:
				return self.atomList
			return output
		elif isinstance(data, atoms.Atom):
			for eachField in data.fields:
				field = data.fields[eachField]
				data.fields[eachField] =  self.flattenData(field)
			while len(self.atomList) < data.id+1:
				self.atomList.append(None)
			self.atomList[data.id] = data
			data = atoms.Reference(data.id)
		elif (isinstance(data, atoms.Reference)):
			pass
		return data

	def renumberItem(self, element): #renumbers an atom or list of atoms. should eventually be a function of atoms. or maybe not? since i do it on a list?
		if isinstance(element, list):
			output = []
			#mutate = element[:]
			for item in element:
				if not (isinstance(item, atoms.Atom) or isinstance(item, atoms.Reference)):
					return element
				output.append(self.renumberItem(item))
			return output
		elif isinstance(element, atoms.Atom):
			print(element.id, element)
			self.refIDs[element.id] = len(self.refIDs)
			element.setID(self.refIDs[element.id])
			for eachField in element.fields:
				field = element.fields[eachField]
				self.renumberItem(field)
		elif isinstance(element, atoms.Reference):
			if not element.id in self.refIDs:
				print("element not already here")
				return None
			element.setID(self.refIDs[element.id])
		return element
	
	def treeifyData(self): #makes 3 trees: child_components, panels, and outports. outports is a singleton tree, but is used to root the child_components tree.
		self.tempAtomList = copy.deepcopy(self.atomList)
		self.refList = []
		subClasses = {"child_components(173)":[],"panels(6213)":[],"proxy_in_ports(177)":[],"proxy_out_ports(178)":[],}

		#find main roots
		for i in range(len(self.tempAtomList)):
			obj = self.tempAtomList[i]
			if obj == None:
				continue
			if obj.classname == "float_core.proxy_out_port_component(50)":
				subClasses["proxy_out_ports(178)"].append(obj)
				subClasses["child_components(173)"].append(atoms.Reference(self.portList[i][0][0]))
				self.tempAtomList[i] = None
			elif obj.classname == "float_core.panel(1680)":
				subClasses["panels(6213)"].append(obj)
				self.tempAtomList[i] = None

		#find other roots
		for i in range(len(self.tempAtomList)):
			if self.tempAtomList[i] and "settings(6194)" in self.tempAtomList[i].fields and len(self.RortList) > i: #for all atoms that exist
				for j in range(len(self.RortList[i])): #look for an outport
					if self.RortList[i][j]:
						break
				else:	#if there are no outports
					if self.tempAtomList[i].classname == "float_core.proxy_in_port_component(154)":
						type = self.tempAtomList[self.tempAtomList[i].fields["port(301)"].id].classname
						if type == "float_core.audio_port(242)":
							subClasses["proxy_in_ports(177)"].insert(0, self.tempAtomList[i]) #get inport references
						elif type == "float_core.note_port(61)":
							subClasses["proxy_in_ports(177)"].append(self.tempAtomList[i])
						else:
							print("jerror: inport that isnt note or audio 1777")
						self.tempAtomList[i] = None
					elif self.tempAtomList[i].classname == "float_common_atoms.buffer_writer_atom(364)": #prepend buffer writers
						subClasses["child_components(173)"].insert(0,self.tempAtomList[i]) #prepend this root
						self.tempAtomList[i] = None
					else:
						subClasses["child_components(173)"].append(self.tempAtomList[i]) #append this root
						self.tempAtomList[i] = None

		#build trees
		for field in subClasses:
			for i in range(len(subClasses[field])):
				subClasses[field][i] = self.treeify(subClasses[field][i])

		#add the child component reference list
		newRefList = []
		for ref in self.refList:
			if self.atomList[ref.id].classname == "float_core.proxy_in_port_component(154)":
				type = self.atomList[self.atomList[ref.id].fields["port(301)"].id].classname
				if type == "float_core.audio_port(242)":
					subClasses["proxy_in_ports(177)"].insert(0, atoms.Reference(ref.id))
				elif type == "float_core.note_port(61)":
					subClasses["proxy_in_ports(177)"].append(atoms.Reference(ref.id))
				continue
			elif ref.id in [j.id for j in subClasses["child_components(173)"]]: #instead of subClasses[], maybe 'lists for lists in subClasses'?
				continue
			newRefList.append(ref)
		self.refList = newRefList
		subClasses["child_components(173)"].extend(self.refList)

		#set data
		for field in subClasses:
			self.data[1].fields[field] = subClasses[field]
		self.refIDs = {}
		self.renumberItem(self.data)
	
	def treeify(self, component):
		if isinstance(component, atoms.Reference):
			if self.tempAtomList[component.id]:
				component = self.tempAtomList[component.id]
				if "settings(6194)" in component.fields:
					self.refList.append(atoms.Reference(component.id))
				self.tempAtomList[component.id] = None
		elif isinstance(component, list):
			for i in range(len(component)):
				component[i] = self.treeify(component[i])
		if isinstance(component, atoms.Atom):
			for f in component.fields:
				component.fields[f] = self.treeify(component.fields[f])
		return component
	
	'''def reorder(self, list):
		output = []
		totalContained = []
		requirements = []
		contained = []
		#print(list)
		for items in list:
			a,b = self.findRandC(items)
			requirements.append(a)
			contained.append(b)
			#print(items.id)
		#print (requirements,contained)
		while list:
			noneFlag = True
			for item in range(len(list)):
				print(set(totalContained).union(set(contained[item])),list[item].id,", r:",set(requirements[item]),"|",set(totalContained).union(set(contained[item])).intersection(set(requirements[item])) )
				if set(requirements[item]) <= (set(totalContained).union(set(contained[item]))):
					output.append(list[item])
					totalContained.extend(contained[item])
					del list[item]
					del contained[item]
					del requirements[item]
					noneFlag = False
					break
			print("------------------------")
			if noneFlag:
				print (totalContained)
				print ("too long", *list, sep = '\n')
				while list:
					output.append(list[0])
					totalContained.extend(contained[0])
					del list[0]
					del contained[0]
					del requirements[0]
		#for items in output:
			#print(items.id)
		return output
	
	def findRandC(self, obj):
		requirements = []
		contained = []
		if isinstance(obj, atoms.Atom) and obj.classname == "float_core.inport_connection(105)":
			obj = obj.fields["source_component(248)"]
		if isinstance(obj, atoms.Atom):
			contained.append(obj.id)
			#print (obj)
			for eachInport in obj.fields["settings(6194)"].fields["inport_connections(614)"]:
				a,b = self.findRandC(eachInport)
				requirements.extend(a)
				contained.extend(b)
			if "buffer(733)" in obj.fields:
				a,b = self.findRandC(obj.fields["buffer(733)"])
				requirements.extend(a)
				contained.extend(b)
		elif isinstance(obj, atoms.Reference):
			requirements.append(obj.id)
		return requirements, contained

	def checkInports(self, inportList, idList):
		for sources in inportList:
			if isinstance(sources.fields["source_component(248)"], atoms.Reference):
				if sources.fields["source_component(248)"].id in idList:
					continue
				return False
			elif isinstance(sources.fields["source_component(248)"], atoms.Atom):
				print("error: theres an atom in my boots! 484")
		return True'''

	def _draw_atom(self, obj):
		id = obj.id
		#print("id:",id)
		x = H_MULT*self.atomList[self.atomList[obj.fields["settings(6194)"].id].fields["desktop_settings(612)"].id].fields["y(18)"]
		y = V_MULT*self.atomList[self.atomList[obj.fields["settings(6194)"].id].fields["desktop_settings(612)"].id].fields["x(17)"]
		(nodesI, nodesO) = (0,0)
		(w,h) = (50,50)
		v_offset = TOTAL_OFF
		b = BORDER
		className = obj.classname
		
		#values
		if className ==  'float_core.decimal_value_atom(289)':
			name = obj.fields["name(374)"]
			val = self.atomList[obj.fields["value_type(702)"].id].fields["default_value(891)"]
			w,h = 4*b + 8*len(name),32+4*b+MED_FONT[1]
			self.makeRect(className, x, y, id, name=name, w=w, h=h)
			self.canvas.create_rectangle(x+b, y+3*b+MED_FONT[1], x+w-b, y+h-b , outline=ACCCOL2, fill=ACCCOL2, tags=("grapheditor","id"+str(id), "4pt", "deco"))
			#self.canvas.create_text(x+b+DOT_SIZE,y+b,fill="white",font=MED_FONT, text=name, anchor="nw", tags=("grapheditor","id"+str(id), "2pt", "name"))
			self.canvas.create_text(x+b+DOT_SIZE,y+(2*b+MED_FONT[1]+h)/2,fill="white",font=THK_FONT, text=str(val)[:7], anchor="w", tags=("grapheditor","id"+str(id), "2pt", "value"))
		elif className == 'float_core.boolean_value_atom(87)':
			name = obj.fields["name(374)"]
			val = self.atomList[obj.fields["value_type(702)"].id].fields["default_value(6957)"]
			w,h = 4*b + 8*len(name),32+4*b+MED_FONT[1]
			self.makeRect(className, x, y, id, name=name, w=w, h=h)
			self.canvas.create_rectangle(x+b, y+3*b+MED_FONT[1], x+w-b, y+h-b , outline=ACCCOL2, fill=ACCCOL2, tags=("grapheditor","id"+str(id), "4pt", "deco"))
			self.canvas.create_text(x+b+DOT_SIZE,y+(2*b+MED_FONT[1]+h)/2,fill="white",font=THK_FONT, text=str(val), anchor="w", tags=("grapheditor","id"+str(id), "2pt", "value"))
		elif className == 'float_core.indexed_value_atom(180)':
			name = obj.fields["name(374)"]
			val = self.atomList[self.atomList[obj.fields["value_type(702)"].id].fields["items(393)"][0].id].fields["name(651)"]
			vals = self.atomList[obj.fields["value_type(702)"].id].fields["items(393)"]
			(w,h) = (4*b + 8*len(name),50+MED_FONT[1])
			self.canvas.create_rectangle(x, y, x+w, y+h, activeoutline = "white" , outline=ACCCOL2, fill=ACCCOL2, tags=("grapheditor","id"+str(id), "4pt", "case"))
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
			val = self.atomList[obj.fields["value_type(702)"].id].fields["default_value(6956)"]
			w,h = 4*b + 8*len(name),32+4*b+MED_FONT[1]
			self.makeRect(className, x, y, id, name=name, w=w, h=h)
			self.canvas.create_rectangle(x+b, y+3*b+MED_FONT[1], x+w-b, y+h-b , outline=ACCCOL2, fill=ACCCOL2, tags=("grapheditor","id"+str(id), "4pt", "deco"))
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
			val1 = obj.fields["comparison(842)"]
			val2 = obj.fields["comparison_value(843)"]
			self.makeRect(className, x, y, id,)
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+MED_FONT[1],fill="white",font=THK_FONT, text=str(val1), anchor="w",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
			self.canvas.create_text(x+b+DOT_SIZE,y+4*b+2*MED_FONT[1],fill="white",font=THK_FONT, text=str(val2), anchor="w",
											tags=("grapheditor","id"+str(id), "2pt", "value"))
		elif className == 'float_common_atoms.indexed_lookup_table_atom(344)':
			'''vals = obj.fields["row_data(744)"]
			length = obj.fields["row_count(743)"]
			name += '\n'
			for i in range(length):
				name += str(vals[i].fields["cells(726)"][0].fields["value(739)"]) + '|'
			width = 6*(len(name)-6)
			print("dothis.editor.238934")'''
			self.makeRect(className, x, y, id, nodesO=obj.fields["column_count(742)"])

		#math
		elif className in ('float_common_atoms.constant_add_atom(308)', 'float_common_atoms.constant_multiply_atom(303)',):
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
			name = self.atomList[obj.fields["port(301)"].id].fields["decorated_name(499)"]
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
			name = self.atomList[obj.fields["port(301)"].id].fields["decorated_name(499)"]
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