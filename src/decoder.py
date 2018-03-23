import struct
from collections import OrderedDict
from src.lib.luts import tables, backupObjects, backupFields
from src.lib import atoms
import uuid

types = {1:'int8',
			2:'int16',
			3:'int32',
			4:'unknown',
			5:'bool',
			6:'float',
			7:'double',
			8:'string',
			9:'object',
		0x0a:'null',
		0x0d:'nested header',
		0x12:'obj array',
		0x14:'map',
		0x15:'hex16',
		0x16:'color',
		0x17:'float array',
		0x19:'package ref array'
}
stringMode = 0
endFlag = 0
def parseField(text):
	global offset, output, stringMode, endFlag, currentSection
	if endFlag:
		return ''
	parseType = text[offset]
	offset += 1
	'''if parseType in types:
		print (types[parseType])
	else:
		print (hex(parseType))'''
	field = '' #output string
	if parseType == 0x01:	#8 bit int
		val = (text[offset])
		if val & 0x80:
			val -= 0x100
			neg = 1
		offset += 1
		return val
	elif parseType == 0x02:	#16 bit int
		val = intConv(text[offset:offset + 2])
		if val & 0x8000:
			val -= 0x10000
		offset += 2
		return val
	elif parseType == 0x03:	#32 bit int
		val = intConv(text[offset:offset + 4])
		if val & 0x80000000:
			val -= 0x100000000
			neg = 1
		offset += 4
		return val
	elif parseType == 0x05:	#boolean
		offset += 1
		return bool(text[offset-1])
	elif parseType == 0x06:	#float
		flVal = struct.unpack('f', struct.pack('L', intConv(text[offset:offset + 4])))[0]
		offset += 4
		return flVal
	elif parseType == 0x07:	#double
		dbVal = struct.unpack('d', struct.pack('Q', intConv(text[offset:offset + 8])))[0]
		offset += 8
		return dbVal
	elif parseType == 0x08:	#string
		if stringMode == 0:
			stringLength = intConv(text[offset:offset+4])
			offset += 4
			string = ''
			sFormat = 0 #0:utf-8, 1:utf-16
			if (stringLength & 0x80000000):
				stringLength &= 0x7fffffff
				sFormat = 1
			if (stringLength > 100000):
				offset += 4
				return 'too long'
			else:
				if sFormat: #utf-16
					for i in range(stringLength):
						if (text[offset+i*2]): #if the first character is anything other than 0x00
							string += chr(intConv(text[offset+i*2:offset+i*2+2]))
						else:
							if text[offset+i*2 + 1] == '\n':
								string += '\\n'
							else:
								string += chr(text[offset+i*2 + 1])
				else: #utf-8
					for i in range(stringLength):
						if chr(text[offset+i]) == '\n':
							string += '\\n'
						else:
							string += chr(text[offset+i])
			offset += stringLength*(sFormat + 1)
			return string
		elif stringMode == 1:
			while (text[offset]) != 0x00:
				if endFlag:
					break
				field += chr(text[offset])
				offset += 1
			offset += 1
			return field
	elif parseType == 0x09:	#object
		return getClass(text)
	elif parseType == 0x0a:	#null
		return None
	elif parseType == 0x0b:	#object reference
		objNum = intConv(text[offset:offset+4])
		offset += 4
		out = atoms.Reference(objNum)
		return out
	elif parseType == 0x0d: #structure										#not done yet
		object = atoms.Atom()
		headerLength = intConv(text[offset:offset+4])
		offset += 4
		if currentSection == 2:
			offset += 57
			field = intConv(text[offset:offset+headerLength])
			offset += headerLength
		elif headerLength<54:
			print("short header at " + hex(offset))
			offset += 54
			stringMode = 1
			field = getClass(text)
			stringMode = 0
		else:
			field = intConv(text[offset:offset+headerLength])
			offset += headerLength
		return field
	elif parseType == 0x12:	#object array
		tempList = []
		while (intConv(text[offset:offset+4]) != 0x3):
			if endFlag:
				break
			tempList.append(getClass(text))
		offset += 4
		return tempList
	elif parseType == 0x14:	#map string
		#field += 'type : "map<string,object>",\n' + 'data :\n' + '{\n'
		object = atoms.Atom()
		string = ''
		mapping = atoms.Atom()
		parseType2 = (text[offset])
		offset += 1
		if parseType2 == 0x1:
			object.add_field("type", "map<string,object>")
			stringLength = intConv(text[offset:offset+4])
			offset += 4
			string = bigChr(text[offset:offset+stringLength])
			offset += stringLength
			mapping.add_field(string, getClass(text))
			offset+=1
		elif parseType2 == 0x0:
			object.add_field("type", "map<string,object>")
			mapping.add_field('', None)
		else:
			object.add_field("type", "unknown")
		object.add_field("data", mapping)
		return object
	elif parseType == 0x15:	#UUID
		value = str(uuid.UUID(bytes=text[offset:offset+16]))
		offset += 16
		return value
	elif parseType == 0x16:	#color
		flVals = []
		flVals.append(struct.unpack('f', struct.pack('L', intConv(text[offset:offset + 4])))[0])
		offset += 4
		flVals.append(struct.unpack('f', struct.pack('L', intConv(text[offset:offset + 4])))[0])
		offset += 4
		flVals.append(struct.unpack('f', struct.pack('L', intConv(text[offset:offset + 4])))[0])
		offset += 4
		flVals.append(struct.unpack('f', struct.pack('L', intConv(text[offset:offset + 4])))[0])
		offset += 4
		return atoms.Color(flVals[0],flVals[1],flVals[2],flVals[3])
	elif parseType == 0x17:	#float array
		arrayLength = intConv(text[offset:offset+4])
		offset += 4
		offset += arrayLength*4
		return field
	elif parseType == 0x19: #string array
		arrayLength = intConv(text[offset:offset+4])
		offset += 4
		arr = []
		for i in range(arrayLength):
			strLength = intConv(text[offset:offset+4])
			offset += 4
			arr.append(text[offset:offset+strLength].decode("utf-8"))
			offset+=strLength
		return arr
	elif parseType == 0x1a: #fuck if i know								#not done yet
		#print("shit,1a ")
		strLength = 0
		while (text[offset] == 0x00):
			strLength = intConv(text[offset:offset+4])
			offset += 4
			if strLength  == 0x90:
				return ''
		field = text[offset:offset+strLength].decode("utf-8")
		offset += strLength
		return field
		
	else:
		endFlag = 1
		print('unknown type at ' + hex(offset-1) + ', ' + str(parseType))
		return 'end here'

def bigOrd(text):
	output = 0
	for i in range(len(text)):
		#print(len(text)-i - 1)
		output += (256**(len(text)-i - 1))*(text[i])
	return output

def bigChr(chain):
	output = ''
	for i in range(len(chain)):
		#print(len(text)-i - 1)
		output += chr(chain[i])
	return output
	 
def intConv(chain):
	output = 0
	for i in range(len(chain)):
		#print(len(chain)-i - 1)
		output += (256**(len(chain)-i - 1))*chain[i]
	return output

def getParams(text, object):
	global offset, output, stringMode, unClassable, unFieldable, endFlag
	fieldNum = intConv(text[offset:offset+4])
	offset += 4
	#print (fieldNum)
	while (fieldNum):
		if endFlag:
			break
		#print("field: " + hex(offset-4))
		fieldName = ''
		value = 'placeholder'
		if fieldNum > 10:
			if fieldNum in tables.params:
				fieldName = tables.params[fieldNum] +  '(' + str(fieldNum) + ')'
			if fieldNum in backupFields.bparams:
				fieldName = backupFields.bparams[fieldNum] +  '(' + str(fieldNum) + ')'
			else:
				fieldName = "missing_field" +  '(' + str(fieldNum) + ')'
				unFieldable += 1
			value = parseField(text)
		else:
			print("weird field detected at " + hex(offset))
			fieldName = text[offset:offset+fieldNum].decode()
			offset += fieldNum
			value = atoms.Atom(fieldName)
			getParams(text, value)
		object.add_field(fieldName, value)
		fieldNum = intConv(text[offset:offset+4])
		offset += 4
	return
	
def getClass(text):
	global offset, output, stringMode, unClassable, unFieldable, endFlag
	if endFlag:
		return ''
	#print("pos: " + hex(offset))
	classNum = intConv(text[offset:offset+4])
	offset += 4
	if classNum == 0x1: #object references
		objNum = intConv(text[offset:offset+4])
		offset += 4
		return atoms.Reference(objNum)
	else:
		objName = ''
		if classNum in tables.objs:
			objName = tables.objs[classNum] + '(' + str(classNum) + ')'
		elif classNum in backupObjects.bobjs:
			objName = backupObjects.bobjs[classNum] + '(' + str(classNum) + ')'
		else:
			objName = "missing_class" + '(' + str(classNum) + ')'
			unClassable += 1
		object = atoms.Atom(objName)
		getParams(text, object)
		#print ("broke out of object")
		return object

replaceList = ['class', 'object_id', 'data', 'type', 'object_ref']

def reformat(input):
	output = input
	'''
	#optional
	for replaceThese in replaceList:
		output = output.replace('"' + replaceThese + '":', replaceThese + ' :')
	'''
	output = output.replace('  ', '\t')
	output = output.replace('":', '" :') #getting rid of this crashes stuff
	output = output.replace('}{', '}\n{')
	'''
	#optional
	i = 0
	length = len(output)
	while (i < len(output)):
		if (output[i:i+3] == ': {'):
			j = 0
			while(output[i+j+5] == '\t'):
				j+=1
			output = output[:i] + ': \n' + j*'\t' + '{' + output[i+3:]
		elif (output[i:i+3] == ':{'):
			j = 0
			while(output[i+j+4] == '\t'):
				j+=1
			output = output[:i] + ':\n' + j*'\t' + '{' + output[i+3:]
		elif (output[i:i+10] == 'object_ref'):
			j = 0
			while(output[i+j] != '\n'):
				j+=1
			k = 0
			while(output[i-k-1] == '\t'):
				k+=1
			output = output[:i-2*k-2] + '{ ' + output[i:i+j] + ' ' +  output[i+j+k:]
		elif output[i:i+3] == ': [':
			skip = 0
			while(output[i+skip] != '\n'):
				skip+=1
			skip+=1
			j = 0
			while(output[i+j+skip] == '\t'):
				j+=1
			if(output[i+j+skip] == '{'):
				j-=1
			output = output[:i] + ': \n' + (j)*'\t' + '[' + output[i+3:]
			if (output[i+j+4] == ']'):
				output = output[:i+j+4] + '\n' + j*'\t' + output[i+j+4:]
		elif output[i:i+9] == 'data : [\n':
			j=10
			while(output[i+j] == '\t'):
				j+=1
			if (output[i+j:i+j+5] == '0.5,\n'):
				j += 5
				while(output[i+j] == '\t'):
					j+=1
				if (output[i+j:i+j+5] == '0.5,\n'):
					j += 5
					while(output[i+j] == '\t'):
						j+=1
					if (output[i+j:i+j+4] == '0.5\n'):
						j += 4
						while(output[i+j] == '\t'):
							j+=1
						if (output[i+j] == ']'):
							output = output[:i] + 'data :  [0.5, 0.5, 0.5]' + output[i+j + 1:]
							i+=22
		elif output[i:i+16] == '"code(6264)" : "':
			while(output[i:i+2] != '",'):
				#if(output[i:i+2] != '\\\\'):
					#output = output[i:] + output[:i]
				i+=1
		i+=1
	'''
	i = 0
	length = len(output)
	while (i < len(output)):
		if output[i:i+16] == '\"code(6264)" : \"':
			i+=16
			while(output[i:i+2] != '\",'):
				if(output[i] == '\\'):
					output = output[:i] + output[i+1:]
				i+=1
		i+=1
	#output = output.replace('data : ', 'data :') #optional
	return output
		
def bwDecode(text):
	global offset, output, objList, unClassable, unFieldable, idCount, endFlag, currentSection
	if endFlag:
		return ''
	atoms.resetId()
	currentSection = 0
	output = [] #the array of objects that will be output
	objList = [] #for making references
	unClassable = 0
	unFieldable = 0
	textLength = len(text)
	offset = 40
	while offset < textLength:
		#print('p')
		if endFlag:
			break
		if currentSection == 0: #getting the header info
			keyType = intConv(text[offset:offset+4])
			offset += 4
			if keyType == 0x0: #end of array
				output.append(objList[0])
				objid = 1
				currentSection = 1
			elif keyType == 0x1: #parameter
				keyLength = intConv(text[offset:offset+4]) #length of the string
				offset += 4
				key = bigChr(text[offset:offset+keyLength])
				offset += keyLength
				value = parseField(text)
				objList[-1].add_field(key, value)
			elif keyType == 0x4: #object
				stringLength = intConv(text[offset:offset+4])
				offset += 4
				name = bigChr(text[offset:offset+stringLength])
				offset += stringLength
				objList.append(atoms.Atom(name))
		elif currentSection == 1: #intermediary section (whitespaces)
			if (text[offset]) == 0x0a:
				#print(output[0])
				currentSection = 2
				offset+=1
			else:
				offset+=1
		elif currentSection == 2:
			output.append(getClass(text))
	if unClassable or unFieldable:
		print("there are " + (unClassable != 0)*(str(unClassable) + " unknown classes") +
									(unClassable != 0 and unFieldable != 0)*" and " +
									(unFieldable != 0)*(str(unFieldable) + " unknown fields") + " in this file")
	else:
		print("everything probably worked ok. to be honest, i'm not sure.")
	return output