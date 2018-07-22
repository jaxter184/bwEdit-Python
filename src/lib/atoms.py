#Class declarations of atoms and references and special data types that only atoms use (modified from original)
#author: stylemistake https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util
from src.lib.luts import typeLists
import uuid
import struct

idCount = 0
## Serializes all device atoms

def hexPad(data, pad = 8):
	if isinstance(data, bytearray):
		return bytearray.fromhex((pad/2-len(value))*'00') + data
	elif isinstance(data, int):
		value = hex(data)[2:]
		return bytearray.fromhex((pad-len(value))*'0'+value)
	else:
		print("jerror: incorrect input for pad prepend")
		return data

def serialize(obj, state = None):
	if state == None:
		state = []
	if isinstance(obj, Atom):
		'''if obj in state:
			return {
				'object_ref': state.index(obj) + 1,
			}'''
		state.append(obj)
		try:
			obj.classname
		except AttributeError:
			return serialize(obj.fields, state) #maybe not the best way to do this, feels a little hacky
		else:
			return OrderedDict([
				('class', obj.classname),
				('object_id', obj.id),
				('data', serialize(obj.fields, state))
			])
	if isinstance(obj, list):
		return [serialize(x, state) for x in obj]
	if isinstance(obj, dict):
		result = OrderedDict()
		for i, value in obj.items():
			result[i] = serialize(value, state)
		return result
	if isinstance(obj, Reference):
		return obj.serialize()
	if isinstance(obj, Color):
		return serialize(obj.fields, state)
	return obj

def resetId(): #geez this feels so hacky -jaxter184
	global idCount
	idCount = 0

class Reference:
	def __init__(self, id = 0):
		self.id = id

	def __str__(self):
		return "<Reference: " + str(self.id) + '>'
	
	def setID(self, id):
		self.id = id
	
	def serialize(self):
		return {'object_ref': self.id}
	
	def encode(self):
		output = bytearray(b'')
		output += hexPad(self.id,8)
		return output

class Color:
	def __init__(self, rd, gr, bl, al):
		self.fields = {'type': "color", 'data': [rd, gr, bl, al]}
		if (al == 1.0):
			self.fields['data'] = self.fields['data'][:-1]
	
	def encode(self):
		output = bytearray(b'')
		count = 0
		for item in self.fields["data"]:
			flVal = struct.unpack('<I', struct.pack('<f', item))[0]
			output += hexPad(flVal,8)
			count += 1
		if count == 3:
			output += struct.pack('<f', 1.0)
		return output
		
class Atom:

	def __init__(self, classname = '', fields = None,):
		global idCount
		if classname != None:
			self.classname = classname
		if fields != None:
			self.fields = fields
		else:
			self.fields = OrderedDict([])
		self.id = idCount #might need to make a manual override for id number
		idCount+=1
	
	def setID(self, id):
		self.id = id
	
	def __str__(self): #just some debugging tools -jaxter184
		#return self.stringify(0)
		#return self.listFields()
		return "Atom: " +  str(self.classname) + '>'

	def stringify(self, tabs = 0): #just some debugging tools -jaxter184
		output = ''
		output += tabs*'\t' + "class : " +  str(self.classname) + '\n'
		output += tabs*'\t' + "data : " +  '\n'
		for data in self.fields:
			output += (tabs+1)*'\t' + '"' + data + '" : '
			if isinstance(self.fields[data], Atom):
				output += self.fields[data].stringify(tabs+1)
			elif isinstance(self.fields[data], str):
				output += '"' + self.fields[data] + '"'
			else:
				output += str(self.fields[data])
			output += '\n'
		return output
	
	def listFields(self):
		output = ''
		output += "class : " +  str(self.classname) + '\n'
		for data in self.fields:
			output += data + '\n'
		return output
	
	def extractNum(self, text = None):
		if text == None:
			text = self.classname
		if text[-1:] == ')':
			start = len(text)-1
			end = start
			while text[start] != '(':
				start-=1
			return int(str(text[start+1:end]))
		else:
			return text
	
	def encodeField(self, output, data):
		value = self.fields[data]
		fieldNum = self.extractNum(data)
		if value==None:
			output += bytearray.fromhex('0a')
			#print("none")
		else:
			#print(typeLists.fieldList[fieldNum])
			#print(value)
			if fieldNum in typeLists.fieldList:
				if typeLists.fieldList[fieldNum] == 0x01:
					if value <= 127 and value >= -128:
						output += bytearray.fromhex('01')
						if value < 0:
							#print(hex(0xFF + value + 1)[2:])
							output += bytearray.fromhex(hex(0xFF + value + 1)[2:])
						else:
							output += hexPad(value, 2)
					elif value <= 32767 and value >= -32768:
						output += bytearray.fromhex('02')
						if value < 0:
							#print(value)
							#print(hex((value + (1 << 4)) % (1 << 4)))
							output += bytearray.fromhex(hex(0xFFFF + value + 1)[2:])
						else:
							output += hexPad(value, 4)
					elif value <= 2147483647 and value >= -2147483648:
						output += bytearray.fromhex('03')
						if value < 0:
							output += bytearray.fromhex(hex(0xFFFFFFFF + value + 1)[2:])
						else:
							output += hexPad(value, 8)
				elif typeLists.fieldList[fieldNum] == 0x05:
					output += bytearray.fromhex('05')
					output += bytearray.fromhex('01' if value else '00')
				elif typeLists.fieldList[fieldNum] == 0x06:
					flVal = struct.unpack('<I', struct.pack('<f', value))[0]
					output += bytearray.fromhex('06')
					output += hexPad(flVal,8)
				elif typeLists.fieldList[fieldNum] == 0x07:
					dbVal = struct.unpack('<Q', struct.pack('<d', value))[0]
					output += bytearray.fromhex('07')
					output += hexPad(dbVal,16)
				elif typeLists.fieldList[fieldNum] == 0x08:
					output += bytearray.fromhex('08')
					value = value.replace('\\n', '\n')
					try: value.encode("ascii")
					except UnicodeEncodeError:
						output += bytearray.fromhex(hex(0x80000000 + len(value))[2:])
						output.extend(value.encode('utf-16be'))
					else:
						output += hexPad(len(value), 8)
						output.extend(value.encode('utf-8'))
				elif typeLists.fieldList[fieldNum] == 0x09:
					if type(value) == Reference:
						output += bytearray.fromhex('0b')
						output += value.encode()
					elif type(value) == Atom:
						output += bytearray.fromhex('09')
						output += value.encode()
					elif type(value) == NoneType:
						output += bytearray.fromhex('0a')
				elif typeLists.fieldList[fieldNum] == 0x12:
					output += bytearray.fromhex('12')
					for item in value:
						if type(item) == Atom:
							output += item.encode()
						elif type(item) ==  Reference:
							output += bytearray.fromhex('00000001')
							output += item.encode()
						else:
							print("something went wrong in atoms.py. \'not object list\'")
					output += bytearray.fromhex('00000003')
				elif typeLists.fieldList[fieldNum] == 0x14:
					output += bytearray.fromhex('14')
					if '' in value["type"]:
						#print("empty string: this shouldnt happen in devices and presets")
						pass
					else:
						output += bytearray.fromhex('01')
						for key in value["data"]:
							output += hexPad(len(key), 8)
							output.extend(key.encode('utf-8'))
							output += value["data"][key].encode()
					output += bytearray.fromhex('00')
				elif typeLists.fieldList[fieldNum] == 0x15:
					output += bytearray.fromhex('15')
					placeholder = uuid.UUID(value)
					output.extend(placeholder.bytes)
				elif typeLists.fieldList[fieldNum] == 0x16:
					output += bytearray.fromhex('16')
					output += value.encode()
				elif typeLists.fieldList[fieldNum] == 0x17:
					output += bytearray.fromhex('17')
					output += hexPad(len(value), 8)
					for item in value:
						flVal = hex(struct.unpack('<I', struct.pack('<f', item))[0])[2:]
						output += hexPad(flVal,8)
				elif typeLists.fieldList[fieldNum] == 0x19: #string array
					output += bytearray.fromhex('19')
					output += hexPad(len(value), 8)
					for i in value:
						i = i.replace('\\n', '\n')
						output += hexPad(len(i), 8)
						output.extend(i.encode('utf-8'))
				else:
					if typeLists.fieldList[fieldNum] == None:
						#print("atoms.py: 'None' in atom encoder. obj: " + str(fieldNum)) #temporarily disabling this error warning because i have no clue what any of these fields are
						pass
					else:
						print("jaxter stop being a lazy poop and " + hex(typeLists.fieldList[fieldNum]) + " to the atom encoder. obj: " + str(fieldNum))
			else:
				print("missing type in typeLists.fieldList: " + str(fieldNum))
		return output

	def encode(self):
		output = bytearray(b'')
		if self.classname == 'meta':
			output += bytearray.fromhex('00000004')
			output += bytearray.fromhex('00000004')
			output.extend('meta'.encode('utf-8'))
			for data in self.fields:
				output += bytearray.fromhex('00000001')
				output += hexPad(len(data), 8)
				output.extend(data.encode('utf-8'))
				output = self.encodeField(output, data)
			output += bytearray.fromhex('00000000')
		else:
			output += hexPad(self.extractNum(),8)
			for data in self.fields:
				output += hexPad(self.extractNum(data),8)
				output = self.encodeField(output, data)
			output += bytearray.fromhex('00000000')
		return output

	def add_inport(self, atom):
		self.fields['settings'].add_connection(InportConnection(atom))
		return self

	def add_field(self, field, value): #need this to be able to add fields, making this a simpler format -jaxter184
		self.fields[field] = value

	def set_fields(self, fields): #for replacing the entire set of fields. maybe unnecessary.
		self.fields = fields


class Meta(Atom):

	classname = 'meta'

	def __init__(self, name, description = '', type = ''):
		self.fields = OrderedDict([
			('application_version_name', 'none'),
			('branch', 'alex/future'),
			('comment', ''),
			('creator', 'Bitwig'),
			('device_category', 'Control'),
			('device_description', description),
			('device_id', 'modulator:6146bcd7-f813-44c6-96e5-2e9d77093a81'),
			('device_name', name),
			('device_uuid', '6146bcd7-f813-44c6-96e5-2e9d77093a81'),
			('is_polyphonic', False),
			('revision_id', 'b3ddbde8410232c8105778921a53ff99045bd547'),
			('revision_no', 51805),
			('tags', ''),
			('type', type)
		])


class Modulator(Atom):

	classname = 'float_core.modulator_contents'

	def __init__(self, name, description = 'Custom modulator',
			header = 'BtWg000100010088000015e50000000000000000'):
		self.fields = OrderedDict([
			('settings', None),
			('child_components', []),
			('panels', []),
			('proxy_in_ports', []),
			('proxy_out_ports', []),
			('fft_order', 0),
			('context_menu_panel', None),
			('device_UUID', '6146bcd7-f813-44c6-96e5-2e9d77093a81'),
			('device_name', name),
			('description', description),
			('creator', 'Bitwig'),
			('comment', ''),
			('keywords', ''),
			('category', 'Control'),
			('has_been_modified', True),
			('detail_panel', None),
			('can_be_polyphonic', True),
			('should_be_polyphonic_by_default', False),
			('should_enable_perform_mode_by_default', False)
		])
		self.meta = Meta(name, description, 'application/bitwig-modulator')
		self.header = header
		self.set_uuid(util.uuid_from_text(name))

	def add_component(self, atom):
		self.fields['child_components'].append(atom)
		return self

	def add_panel(self, atom):
		self.fields['panels'].append(atom)
		return self

	def add_proxy_in(self, atom):
		self.fields['proxy_in_ports'].append(atom)
		return self

	def add_proxy_out(self, atom):
		self.fields['proxy_out_ports'].append(atom)
		return self

	def set_description(self, value):
		self.meta.fields['device_description'] = value
		self.fields['description'] = value
		return self

	def set_uuid(self, value):
		self.meta.fields['device_uuid'] = value
		self.meta.fields['device_id'] = 'modulator:' + value
		self.fields['device_UUID'] = value
		return self

	def serialize(self):
		return util.serialize_bitwig_device(OrderedDict([
			('header', self.header),
			('meta', serialize(self.meta)),
			('contents', serialize(self))
		]))


class AbstractValue(Atom):

   def __init__(self, name, default = None, tooltip = '', label = ''):
      self.fields = OrderedDict([
         ('settings', Settings()),
         ('channel_count', 0),
         ('oversampling', 0),
         ('name', name),
         ('label', label),
         ('tooltip_text', tooltip),
         ('preset_identifier', name.upper()),
         ('modulations_to_ignore', 'MATH'),
         ('value_type', None),
         ('value', default)
      ])


class DecimalValue(AbstractValue):

   classname = 'float_core.decimal_value_atom'

   def __init__(self, name, default = 0, tooltip = '', label = '',
         min = -1, max = 1, unit = 0, step = -1, precision = -1):
      default = float(default)
      min = float(min)
      max = float(max)
      super().__init__(name, default, tooltip, label)
      self.fields['value_type'] = Atom('float_core.decimal_value_type', OrderedDict([
         ('min', min),
         ('max', max),
         ('default_value', default),
         ('domain', 0),
         ('engine_domain', 0),
         ('value_origin', 0),
         ('pixel_step_size', step),
         ('unit', unit),
         ('decimal_digit_count', precision),
         ('edit_style', 0),
         ('parameter_smoothing', True),
         ('allow_automation_curves', True)
      ]))

   def set_range(self, min, max):
      self.fields['value_type'].fields['min'] = float(min)
      self.fields['value_type'].fields['max'] = float(max)
      return self

   def use_smoothing(self, smoothing = True):
      self.fields['value_type'].fields['parameter_smoothing'] = smoothing
      return self

   def set_decimal_digit_count(self, decimal_digit_count):
      self.fields['value_type'].fields['decimal_digit_count'] = decimal_digit_count
      return self

   def set_step(self, step):
      self.fields['value_type'].fields['pixel_step_size'] = step
      return self


class IndexedValue(AbstractValue):

   classname = 'float_core.indexed_value_atom'

   def __init__(self, name, default = 0, tooltip = '', label = '',
         items = []):
      super().__init__(name, default, tooltip, label)
      self.fields['value_type'] = Atom('float_core.indexed_value_type', OrderedDict([
         ('items', []),
         ('edit_style', 0),
         ('columns', 0),
         ('default_value', default)
      ]))
      for x in items:
         self.add_item(x)

   def add_item(self, name):
      items = self.fields['value_type'].fields['items']
      seq_id = len(items)
      items.append(Atom('float_core.indexed_value_item', OrderedDict([
         ('id', seq_id),
         ('name', name)
      ])))
      return self


class Settings(Atom):

   classname = 'float_core.component_settings'

   def __init__(self):
      self.fields = OrderedDict([
         ('desktop_settings', Atom('float_core.desktop_settings', OrderedDict([
            ('x', 0),
            ('y', 0),
            ('color', OrderedDict([
               ('type', 'color'),
               ('data', [ 0.5, 0.5, 0.5 ])
            ]))
         ]))),
         ('inport_connections', []),
         ('is_polyphonic', True)
      ])

   def add_connection(self, atom):
      self.fields['inport_connections'].append(atom)
      return self


class InportConnection(Atom):

   classname = 'float_core.inport_connection'

   def __init__(self, atom = None):
      self.fields = OrderedDict([
         ('source_component', atom),
         ('outport_index', 0),
         ('high_quality', True),
         ('unconnected_value', 0.0),
      ])

   def set_source(self, atom):
      self.source_component = atom
      return self


class Nitro(Atom):

   classname = 'float_common_atoms.nitro_atom'

   def __init__(self):
      self.fields = OrderedDict([
         ('settings', Settings()),
         ('channel_count', 1),
         ('oversampling', 0),
         ('code', None),
         ('fft_order', 0)
      ])

   def set_source_file(self, file):
      # TODO
      return self

   def set_source(self, code):
      self.fields['code'] = code
      return self


class ModulationSource(Atom):

   classname = 'float_core.modulation_source_atom'

   def __init__(self, name = ''):
      self.fields = OrderedDict([
         ('settings', Settings()),
         ('channel_count', 1),
         ('oversampling', 0),
         ('name', name),
         ('preset_identifier', name.upper()),
         ('display_settings', OrderedDict([
            ('type', 'map<string,object>'),
            ('data', OrderedDict([
               ('abique', Atom('float_core.modulation_source_atom_display_settings', {
                  'is_source_expanded_in_inspector': False,
               })),
            ]))
         ]))
      ])


class PolyphonicObserver(Atom):

   classname = 'float_core.polyphonic_observer_atom'

   def __init__(self):
      self.fields = OrderedDict([
         ('settings', Settings()),
         ('channel_count', 1),
         ('oversampling', 0),
         ('dimensions', 1)
      ])


class AbstractPanel(Atom):

   def __init__(self, tooltip = ''):
      self.fields = OrderedDict([
         ('layout_settings', None),
         ('is_visible', True),
         ('is_enabled', True),
         ('tooltip_text', tooltip)
      ])

   def set_tooltip(self, text):
      self.fields['tooltip_text'] = text
      return self


class AbstractPanelItem(AbstractPanel):

   def __init__(self, tooltip = '', x = 0, y = 0, width = 17, height = 4):
      super().__init__(tooltip)
      self.fields['layout_settings'] = Atom('float_core.grid_panel_item_layout_settings', OrderedDict([
         ('width', width),
         ('height', height),
         ('x', x),
         ('y', y)
      ]))

   def set_size(self, width, height):
      self.fields['layout_settings'].fields['width'] = width
      self.fields['layout_settings'].fields['height'] = height
      return self

   def set_position(self, x, y):
      self.fields['layout_settings'].fields['x'] = x
      self.fields['layout_settings'].fields['y'] = y
      return self

   def set_model(self, atom):
      self.fields['data_model'] = model
      return self


class Panel(AbstractPanel):

   classname = 'float_core.panel'

   def __init__(self, root_item, width = 17, height = 17, name = 'Main',
         tooltip = ''):
      super().__init__(tooltip)
      self.fields['root_item'] = root_item
      self.fields['name'] = name
      self.fields['width'] = width
      self.fields['height'] = height
      self.fields['expressions'] = []


class GridPanel(AbstractPanel):

   classname = 'float_core.grid_panel_item'

   def __init__(self, tooltip = '', title = ''):
      super().__init__(tooltip)
      self.fields['items'] = []
      self.fields['border_style'] = 1
      self.fields['title'] = title
      self.fields['show_title'] = title != ''
      self.fields['title_color'] = 6
      self.fields['brightness'] = 0

   def add_item(self, atom):
      self.fields['items'].append(atom)
      return self


class MappingSourcePanelItem(AbstractPanelItem):

   classname = 'float_core.mapping_source_panel_item'

   def __init__(self, tooltip = '', x = 0, y = 0, width = 17, height = 4,
         model = None):
      super().__init__(tooltip, x, y, width, height)
      self.fields['data_model'] = model
      self.fields['title'] = ''
      self.fields['filename'] = ''


class PopupChooserPanelItem(AbstractPanelItem):

   classname = 'float_core.popup_chooser_panel_item'

   def __init__(self, tooltip = '', x = 0, y = 0, width = 7, height = 4,
         model = None):
      super().__init__(tooltip, x, y, width, height)
      self.fields['data_model'] = model
      self.fields['label_style'] = 0
      self.fields['style'] = 1


class KnobPanelItem(AbstractPanelItem):

   classname = 'float_core.knob_panel_item'

   def __init__(self, tooltip = '', x = 0, y = 0, width = 9, height = 7,
         model = None, size = 1, style = 0):
      super().__init__(tooltip, x, y, width, height)
      self.fields['data_model'] = model
      self.fields['title'] = ''
      self.fields['knob_size'] = size
      self.fields['knob_style'] = style
      self.fields['label_color'] = 999
      self.fields['pie_color'] = 999


class NumberFieldPanelItem(AbstractPanelItem):

   classname = 'float_core.number_field_panel_item'

   def __init__(self, tooltip = '', x = 0, y = 0, width = 13, height = 4,
         model = None, style = 0, show_value_bar = False):
      super().__init__(tooltip, x, y, width, height)
      self.fields['data_model'] = model
      self.fields['title'] = ''
      self.fields['style'] = style
      self.fields['show_value_bar'] = show_value_bar

   def with_value_bar(self):
      self.fields['show_value_bar'] = True
      return self


class ProxyInPort(Atom):

   classname = 'float_core.proxy_in_port_component'

   def __init__(self, atom):
      self.fields = OrderedDict([
         ('settings', Settings()),
         ('port', atom)
      ])


class AudioPort(Atom):

   classname = 'float_core.audio_port'

   def __init__(self):
      self.fields = OrderedDict([
         ('name', ''),
         ('description', ''),
         ('decorated_name', ' Audio out (PARENT)'),
         ('is_inport', False),
         ('is_optional', False),
         ('exclude_from_graph', False),
         ('channel_count', 3)
      ])


class NotePort(Atom):

   classname = 'float_core.note_port'

   def __init__(self):
      self.fields = OrderedDict([
         ('name', ''),
         ('description', ''),
         ('decorated_name', ' Note out'),
         ('is_inport', False),
         ('is_optional', False),
         ('exclude_from_graph', False)
      ])
