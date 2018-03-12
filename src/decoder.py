import struct
from collections import OrderedDict
from src import tables
from src.lib import fs
from src.lib import util
from src.lib import atoms

mode = 3
##:func name,	#description (allowed filetypes)
#0:coords,		#collects the coordinates of modules in the desktop modular environment (plaintext)
#1:settings,	#collects all field numbers used and their respective names (plaintext)
#2:classes, 	#collects all class numbers used and their respective names (plaintext)
#3:objectify	#converts files from unreadable to plaintext .bwdevice and .bwmodulator files (unreadable)

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

def parseField(text, stringType = 0):
	global offset, inMap, output, stringMode, objList, objHeir, tempObjList #ugh so many global variables
	parseType = text[offset]
	offset += 1
	'''if parseType in types:
		print (types[parseType])
	else:
		print (hex(parseType))'''
	field = '' #output string
	if parseType == 0x01:		#8 bit int
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
		return bool(text[offset])
	elif parseType == 0x06:	#float
		flVal = struct.unpack('f', struct.pack('L', intConv(text[offset:offset + 4])))[0]
		offset += 4
		return flVal
	elif parseType == 0x07:	#double
		dbVal = struct.unpack('d', struct.pack('Q', intConv(text[offset:offset + 8])))[0]
		offset += 8
		return dbVal
	elif parseType == 0x08:	#string
		if stringType == 0:
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
							string += ('\\u' + hex(intConv(text[offset+i*2:offset+i*2+2])))
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
		elif stringType == 1:
			while (text[offset]) != 0x00:
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
		#objList.append(out)
		return out
	elif parseType == 0x0d: #nested header
		headerLength = intConv(text[offset:offset+4])
		offset += 4
		field += '"'
		print(headerLength)
		while(headerLength > 0):
			field += chr(text[offset])
			offset+=1
			headerLength-=1
		field += '"'
		return field
	elif parseType == 0x12:	#object array
		tempList = []
		while (intConv(text[offset:offset+4]) != 0x3):
			tempList.append(getClass(text))
		#print (tempList)
		offset += 4
		return tempList
	elif parseType == 0x14:	#map string to object
		field += 'type : "map<string,object>",\n' + 'data :\n' + '{\n' 
		parseType2 = (text[offset])
		offset += 1
		return field
		if parseType2 == 0x1: 
			stringLength = intConv(text[offset:offset+4])
			offset += 4
			field += bigChr(text[offset:offset+stringLength])
			offset += stringLength
		inMap = 1
		getClass(text)
		return field
	elif parseType == 0x15:	#16 character hex value
		for i in range(16):
			if i in [4,6,8,10]:
				field += '-'
			field += "{0:0{1}x}".format((text[offset+i]),2) #includes leading zeros
		offset += 16
		return field
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
	elif parseType == 0x19: #package reference array
		arrayLength = intConv(text[offset:offset+4])
		offset += 4
		field += '['
		for i in range(arrayLength):
			field += (chr(text[offset+i])) + ', '
		if arrayLength:
			field = field[:-2]
		field += ']'
		offset += arrayLength
		return field
	else:
		print('unknown type at ' + hex(offset-1) + ', ' + str(parseType))
		return ''

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
	 
def coords(text):
	output = ""
	lastStart = 0
	isX = 0
	findComma = 0
	for pick in range(14, len(text)):
		if bigChr(text[pick - 10:pick]) == '\"x(17)\" : ':
			lastStart = pick
			isX = 1
			findComma = 1
		if bigChr(text[pick - 10:pick]) == '\"y(18)\" : ':
			lastStart = pick
			isX = 0
			findComma = 1
		if bigChr(text[pick - 14:pick]) == '\"name(374)\" : ':
			lastStart = pick
			isX = 0
			findComma = 1
		if bigChr(findComma and (text[pick]) == ','):
			if isX:
				 output += '\n'
			else:
				 output += ','
			findComma = 0
			output += bigChr(text[lastStart:pick])
	return output[1:]
	 
def settings(text):
	output = ""
	for pick in range(len(text)-5):
		if bigChr(text[pick:pick + 5]) == ')\" : ':
			preIndex = 0
			while bigChr(text[pick - preIndex]) != '(':
				 preIndex += 1
			number = bigChr(text[pick-preIndex + 1:pick])
			pIndexNum = preIndex
			while chr(text[pick - preIndex]) != '\"':
				 preIndex += 1
			parameter = bigChr(text[pick-preIndex + 1:pick-pIndexNum])
			output += '\n' + number + ',' + parameter
	return output[1:]

def classes(text):
	output = ""
	for pick in range(len(text)):
		if pick > 100:
			if text[pick-9:pick] == 'class : \"':
				preIndex = 0
				while text[pick + preIndex] != '(':
				  preIndex += 1
				parameter = text[pick:pick + preIndex]
				'''if parameter[:11] == 'float_core.':
				  parameter = parameter[11:]
				if parameter[:19] == 'float_common_atoms.':
				  parameter = parameter[19:]'''
				pIndexNum = preIndex
				while text[pick + preIndex] != ')':
				  preIndex += 1
				number = text[pick+pIndexNum + 1:pick+preIndex]
				output += '\n' + number + ',' + parameter
				#print(parameter)
	return output[1:]

def getClass(text):
	global offset, inMap, output, stringMode, objList, objHeir, tempObjList, unClassable, unFieldable
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
		else:
			objName = "missing_class" + '(' + str(classNum) + ')'
			unClassable += 1
		object = atoms.Atom(objName)
		fieldNum = intConv(text[offset:offset+4])
		offset += 4
		#print (fieldNum)
		while (fieldNum):
			#print("field: " + hex(offset-4))
			fieldName = ''
			if fieldNum in tables.params:
				fieldName = tables.params[fieldNum] +  '(' + str(fieldNum) + ')'
			else:
				fieldName = "missing_field" +  '(' + str(fieldNum) + ')'
				unFieldable += 1
			'''if inMap == 1: #redo this
				offset += 1
				inMap = 0'''
			value = parseField(text)
			object.add_field(fieldName, value)
			fieldNum = intConv(text[offset:offset+4])
			offset += 4
		#print ("broke out of object")
		#objHeir = objHeir[:-1]
		#tempObjList.append(outObj)
		#objHeir.append(len(objList))
		#objList.append(object)
		return object

replaceList = ['class', 'object_id', 'data', 'type', 'object_ref']

def reformat(input):
	output = input
	#for replaceThese in replaceList: #optional
	#	output = output.replace('"' + replaceThese + '":', replaceThese + ' :')
	output = output.replace('  ', '\t')
	output = output.replace('":', '" :') #getting rid of this crashes stuff
	output = output.replace('}{', '}\n{')
	#i = 0
	#length = len(output)
	'''while (i < len(output)): #all of this is also optional
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
		i+=1'''
	#output = output.replace('data : ', 'data :') #optional
	#output = output.replace('(4433)" : false', '(4433)" : true') #optional
	#output = output.replace('(4434)" : false', '(4434)" : true') #optional
	#output = output.replace('(1943)" : false', '(1943)" : true') #optional
	#output = output.replace('(2435)" : false', '(2435)" : true') #optional
	#output = output.replace('(5769)" : false', '(5769)" : true') #optional
	output = output.replace('(2270)" : false', '(2270)" : true')
	output = output.replace('(6309)" : false', '(6309)" : true')
	output = output.replace('(6310)" : false', '(6310)" : true')
	#output = output.replace('(6255)" : false', '(6255)" : true') #optional
	#output = output.replace('(6582)" : false', '(6582)" : true') #optional
	#output = output.replace('(6888)" : false', '(6888)" : true') #optional
	#output = output.replace('(6889)" : false', '(6889)" : true') #optional
	#output = output.replace('(6714)" : false', '(6714)" : true') #optional
	#output = output.replace('(6499)" : false', '(6499)" : true') #optional
	#output = output.replace('(6730)" : false', '(6730)" : true') #optional
	#output = output.replace('(6731)" : false', '(6731)" : true') #optional
	#output = output.replace('(6243)" : false', '(6243)" : true') #optional
	#output = output.replace('(4847)" : false', '(4847)" : true') #optional
	#output = output.replace('(392)" : false', '(392)" : true') #optional
	#output = output.replace('(6957)" : false', '(6957)" : true') #optional
	return output
		
def objectify(text):
	global offset, inMap, output, stringMode, objList, objHeir, tempObjList, unClassable, unFieldable
	#output = text[:40] #BtWg header
	header = 'BtWg00010001008d000016a00000000000000000'
	#output += '{\n\t'
	currentSection = 0
	#objHeir = [] #will hold the current heirarchy of objects (integer values)
	output = [] #the array of objects that will be output
	objList = [] #for making references
	tempObjList = []
	inMap	= 0
	unClassable = 0
	unFieldable = 0
	stringMode = 0
	firstClass = 0
	textLength = len(text)
	offset = 40
	while offset < textLength:#textLength: #should probably use a while loop instead so it doesnt have to iterate through ignored characters
		#print('p')
		if currentSection == 0: #getting the header info
			keyType = intConv(text[offset:offset+4])
			offset += 4
			if keyType == 0x0: #end of array
				#objHeir = objHeir[:-1]
				output.append(objList[0])
				objid = 1
				currentSection = 1
			elif keyType == 0x1: #parameter
				keyLength = intConv(text[offset:offset+4]) #length of the string
				offset += 4
				key = bigChr(text[offset:offset+keyLength])
				offset += keyLength
				value = parseField(text)
				#print (objHeir[-1:][0])
				#output[objHeir[-1:][0]].add_field(key, value)
				objList[-1].add_field(key, value)
			elif keyType == 0x4: #object
				stringLength = intConv(text[offset:offset+4])
				offset += 4
				name = bigChr(text[offset:offset+stringLength])
				offset += stringLength
				objList.append(atoms.Atom(name))
				#objHeir.append(len(objList))
		elif currentSection == 1: #intermediary section (whitespaces)
			if (text[offset]) == 0x0a:
				currentSection = 2
				offset+=1
			else:
				offset+=1
		elif currentSection == 2:
			print("------------------heyo")
			output.append(getClass(text))
			#output.append(objList)
	if unClassable or unFieldable:
		print("there are " + (unClassable != 0)*(str(unClassable) + " unknown classes") + (unClassable != 0 and unFieldable != 0)*" and " + (unFieldable != 0)*(str(unFieldable) + " unknown fields") + " in this file")
	else:
		print("everything probably worked ok. to be honest, i'm not sure.")
	#output.append(objList)
	finalOutput = ''
	for item in output: #encodes all of the objects in the output list
		finalOutput += util.json_encode(atoms.serialize(item))
	return header + reformat(finalOutput)
	#return header + finalOutput

algos = {0:coords,
			1:settings,
			2:classes,
			3:objectify
}
inputType = [0,0,0,1,1]

def magic(name, directory): #applies an algorithm to a single file (which algorithm it is is based on the 'mode' variable)
	device_data = fs.read_binary(directory + '\\' + name)
	output = ""
	if (device_data[42] == 0) and inputType[mode]: #not sure how to implement this yet
		output = algos[mode](device_data)
	elif (device_data[42] == '{') and not inputType[mode]:
		print("this file is either already converted or isn't an unreadable file")
	else:
		print("i don't know what kind of file this is")
	fs.write_binary(directory + '\output\\converted ' + name, output.encode("utf-8"))

#these function calls are for test purposes
#magic('test.bwproject', '.\devices\old devices')
#magic('Amp.bwdevice', '.\devices\old devices')
#print('decoder imported')
