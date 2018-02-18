import struct
from tables import *

mode = 3
##:func name,	#description (allowed filetypes)
#0:coords,		#collects the coordinates of modules in the desktop modular environment (plaintext)
#1:settings,	#collects all field numbers used and their respective names (plaintext)
#2:classes, 	#collects all class numbers used and their respective names (plaintext)
#3:convert		#converts files from unreadable to plaintext .bwdevice and .bwmodulator files (unreadable)

def parseField(text, parseType, stringType = 0):
	global offset, tabs, inMap, arrayLevels, output, gettingClass, stringMode #ugh so many global variables
	field = '' #output string
	if parseType == 0x01:		#8 bit int
		val = ord(text[offset])
		if val & 0x80:
			val -= 0x100
			neg = 1
		field += str(val)
		offset += 1
	elif parseType == 0x02:	#16 bit int
		val = bigOrd(text[offset:offset + 2])
		if val & 0x8000:
			val -= 0x10000
		field += str(val)
		offset += 2
	elif parseType == 0x03:	#32 bit int
		val = bigOrd(text[offset:offset + 4])
		if val & 0x80000000:
			val -= 0x100000000
			neg = 1
		field += str(val)
		offset += 4
	elif parseType == 0x05:	#boolean
		if offset + 1 > len(text):
			print("error 502: how did you get here, this should only happen if there is a boolean field at the end of the file")
		if ord(text[offset]):
			field += 'true'
		else:
			field += 'false'
		offset += 1
	elif parseType == 0x06:	#float
		flVal = struct.unpack('f', struct.pack('L', bigOrd(text[offset:offset + 4])))[0]
		field += str(flVal)
		offset += 4
	elif parseType == 0x07:	#double
		dbVal = struct.unpack('d', struct.pack('Q', bigOrd(text[offset:offset + 8])))[0]
		field += str(dbVal)
		offset += 8
	elif parseType == 0x08:	#string
		if stringType == 0:
			if offset + 1 > len(text):
				print("error 802: the parse code says to go further than the end of the file :/")
			stringLength = bigOrd(text[offset:offset+4])
			offset += 4
			string = ''
			sFormat = 0 #0:utf-8, 1:utf-16
			if (stringLength & 0x80000000):
				stringLength &= 0x7fffffff
				sFormat = 1
			else:
				if sFormat: #utf-16
					for i in range(stringLength):
						if ord(text[offset+i*2]): #if the first character is anything other than 0x00
							string += '\u' + hex(bigOrd(text[offset+i*2:offset+i*2+2]))
						else:
							if text[offset+i*2 + 1] == '\n':
								string += '\\n'
							else:
								string += text[offset+i*2 + 1]
				else: #utf-8
					for i in range(stringLength):
						if text[offset+i] == '\n':
							string += '\\n'
						else:
							string += text[offset+i]
			field += '"' + string + '"'
			offset += stringLength*(sFormat + 1)
		elif stringType == 1:
			field += '"'
			while ord(text[offset]) != 0x00:
				field += text[offset]
				offset += 1
			offset += 1
			field += '"'
	elif parseType == 0x09:	#object
		field += '\n' + '\t'*tabs + '{ '
		tabs += 1
		gettingClass = 1
	elif parseType == 0x0a:	#null
		field += 'null'
	elif parseType == 0x0b:	#object reference
		field += '{ object_ref : ' + str(bigOrd(text[offset:offset+4])) + ' }'
		offset += 4
	elif parseType == 0x0d: #nested header
		field += '(' + str(bigOrd(text[offset:offset+4])) + ')'
		offset += 4
		field += text[offset:offset+40]
		offset += 40
		stringLength = bigOrd(text[offset:offset+4])
		offset += 4
		field += '"' + text[offset:offset+stringLength] + '" & placeholder'
		offset += stringLength
		offset += 1
		tabs += 1
		stringMode = 1
	elif parseType == 0x12:	#object array
		arrayLevels.append(tabs)
		field += '\n' + '\t'*tabs + '[\n' + '\t'*(tabs + 1) + '{ '
		tabs += 2
		gettingClass = 1
	elif parseType == 0x14:	#map string to object
		field += '\n' + '\t'*tabs + '{\n'
		tabs += 1
		field += '\t'*(tabs) + 'type : "map<string,object>",\n' + '\t'*(tabs) + 'data :\n' + '\t'*tabs + '{\n' 
		tabs += 1
		field += '\t'*(tabs)
		parseType2 = ord(text[offset])
		offset += 1
		if parseType2 == 0x1: 
			stringLength = bigOrd(text[offset:offset+4])
			offset += 4
			field += '"' + text[offset:offset+stringLength] + '" : \n' + '\t'*(tabs) + '{'
			tabs += 1
			offset += stringLength
		inMap = 1
		gettingClass = 1
	elif parseType == 0x15:	#16 character hex value
		if offset+16 > len(text):
			print("aw poop something messed up")
		field += '"'
		for i in range(16):
			if i in [4,6,8,10]:
				field += '-'
			field += "{0:0{1}x}".format(ord(text[offset+i]),2) #includes leading zeros
		field += '"'
		offset += 16
	elif parseType == 0x16:	#color
		field += '\n' + '\t'*tabs + '{\n' + '\t'*(tabs + 1) + 'type : "color",\n' + '\t'*(tabs + 1) + 'data : ['
		field += parseField(text, 6) + ', ' + parseField(text, 6) + ', ' + parseField(text, 6) + (', ' + str(parseField(text, 6)))*(bigOrd(text[offset-4:offset]) != 0x3f800000)
		field += ']\n' + '\t'*tabs + '}'
	elif parseType == 0x17:	#float array
		field += '\n' + '\t'*tabs + '{\n' + '\t'*(tabs + 1) + 'type : "float[]",\n' + '\t'*(tabs + 1) + 'data : ['
		arrayLength = bigOrd(text[offset:offset+4])
		offset += 4
		field += ']\n' + '\t'*tabs + '}'
		offset += arrayLength*4
	elif parseType == 0x19: #package reference array
		arrayLength = bigOrd(text[offset:offset+4])
		offset += 4
		field += '['
		for i in range(arrayLength):
			field += ord(text[offset+i]) + ', '
		if arrayLength:
			field = field[:-2]
		field += ']'
		offset += arrayLength
	else:
		print 'unknown type at ' + hex(offset-1) + ', ' + str(output.count('\n') + 1)
	return field
	
def bigOrd(text):
    output = 0
    for i in range(len(text)):
        #print(len(text)-i - 1)
        output += (256**(len(text)-i - 1))*ord(text[i])
    return output
	 
def coords(text):
	output = ""
	lastStart = 0
	isX = 0
	findComma = 0
	for pick in range(14, len(text)):
		if text[pick - 10:pick] == '\"x(17)\" : ':
			lastStart = pick
			isX = 1
			findComma = 1
		if text[pick - 10:pick] == '\"y(18)\" : ':
			lastStart = pick
			isX = 0
			findComma = 1
		if text[pick - 14:pick] == '\"name(374)\" : ':
			lastStart = pick
			isX = 0
			findComma = 1
		if findComma and (text[pick] == ','):
			if isX:
				 output += '\n'
			else:
				 output += ','
			findComma = 0
			output += text[lastStart:pick]
	return output[1:]
	 
def settings(text):
	output = ""
	for pick in range(len(text)-5):
		if text[pick:pick + 5] == ')\" : ':
			preIndex = 0
			while text[pick - preIndex] != '(':
				 preIndex += 1
			number = text[pick-preIndex + 1:pick]
			pIndexNum = preIndex
			while text[pick - preIndex] != '\"':
				 preIndex += 1
			parameter = text[pick-preIndex + 1:pick-pIndexNum]
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

def convert(text):
	global offset, tabs, inMap, arrayLevels, output, gettingClass, stringMode
	#output = text[:40] #BtWg header
	output = 'BtWg00010001008d000016a00000000000000000'
	output += '{\n\t'
	gettingClass = 0
	ignore = 0
	objid = 1
	currentSection = 0
	tabs = 1
	arrayLevels = []
	inMap	= 0
	firstField = 1
	flag = 0
	unClassable = 0
	unFieldable = 0
	stringMode = 0
	for pick in range(len(text)): #should probably use a while loop instead so it doesnt have to iterate through ignored characters
		if ignore:
			ignore -= 1
		elif pick >= 40:
			#print 'p'
			if currentSection == 0:
				offset = pick
				keyType = bigOrd(text[offset:offset+4])
				offset += 4
				#print hex(offset), str(keyType)
				if keyType == 0x0: #end of array
					tabs -= 1
					output = output[:(tabs + 3)*-1] + '\n' + '\t'*(tabs) + '}\n' + '}\n' + '{' #tabs add offset value might be wrong
					objid = 1
					currentSection = 1
				elif keyType == 0x1: #parameter
					keyLength = bigOrd(text[offset:offset+4]) #length of the string
					offset += 4
					key = text[offset:offset+keyLength]
					offset += keyLength
					parseType = ord(text[offset])
					offset += 1
					field = parseField(text, parseType)
					output += '"' + key + '" : ' + field + ',\n' + '\t'*tabs
				elif keyType == 0x4: #object
					stringLength = bigOrd(text[offset:offset+4])
					offset += 4
					output += 'class : "' + text[offset:offset+stringLength] + '",\n'
					offset += stringLength
					output += '\t'*tabs + 'object_id : ' + str(objid) + ',\n'
					output += '\t'*tabs + 'data :\n' + '\t'*tabs + '{\n' + '\t'*(tabs + 1)
					objid += 1
					tabs += 1
				ignore += offset - pick - 1
			elif currentSection == 1:
				#print ord(text[pick])
				if ord(text[pick]) == 0x0a:
					currentSection = 2
					gettingClass = 1
			elif currentSection == 2:
				if tabs > 0: #for safety
					#print hex(pick) + ', ' + str(output.count('\n'))
					if pick < len(text):
						#print(bigOrd(text[pick:pick+4]))
						#print pick
						if gettingClass:
							offset = pick
							classNum = bigOrd(text[offset:offset+4])
							offset += 4
							if classNum == 0x3: #end of array
								#print tabs
								output = output[:-1 - tabs]
								if output[-2:] == ',\n': #ugh this is such an ugly way to do this
									output = output[:-1]
								tabs -= 2
								output = output[:-1] + '\n' + '\t'*tabs + ']'
								arrayLevels = arrayLevels[:-1]
								gettingClass = 0
							elif classNum == 0x1: #object references
								output = output[:-1 - tabs]
								if output[-2:] == ',\n':
									output = output[:-1]
								if output[-2:] == '[\n': #im pretty sure there's a nicer way to do this
									output += '\t'*(tabs-1)
								output += '{ object_ref : ' + str(bigOrd(text[offset:offset+4])) + ' },\n' + '\t'*(tabs-1) + '{ '
								offset += 4
							else:
								if classNum in objs:
									if output[-1:] != '{':
										output = output[:-1]
									output += '\n' + '\t'*tabs + 'class : "' + objs[classNum] + '(' + str(classNum) + ')",\n' + '\t'*tabs + 'object_id : ' + str(objid) + ',\n' + '\t'*tabs + 'data :\n' + '\t'*tabs + '{'
								else:
									output = output[:-1] + '\n' + '\t'*tabs + 'class : "' + "missing_class" + '(' + str(classNum) + ')",\n' + '\t'*tabs + 'object_id : ' + str(objid) + ',\n' + '\t'*tabs + 'data :\n' + '\t'*tabs + '{'
									if not classNum in [2050]:
										print "missing class " + str(classNum) + ', ' + hex(pick) + ', ' + str(output.count('\n') + 1)
									else:
										unClassable += 1
								objid += 1
								tabs += 1
								firstField = 1
								gettingClass = 0
							ignore += offset - pick - 1
						else:
							offset = pick
							fieldNum = bigOrd(text[offset:offset+4])
							offset += 4
							if firstField:
								firstField = 0
							else:
								output += ','
							field = ''
							if fieldNum:
								if fieldNum in params:
									output += '\n' + '\t'*tabs + '"' + params[fieldNum] +  '(' + str(fieldNum) + ')" : '
								else:
									output += '\n' + '\t'*tabs + '"' + "missing_field" +  '(' + str(fieldNum) + ')" : '
									if not fieldNum in [7489, 7490, 7243, 7235]:
										print "missing field " + str(fieldNum) + ', ' + hex(pick) + ', ' + str(output.count('\n') + 1)
									else:
										unFieldable += 1
								parseType = ord(text[offset])
								offset += 1
								if inMap == 1:
									offset += 1
									inMap = 0
									tabs -= 1
									field += '\n' + '\t'*tabs + '}' + '\n'
									tabs -= 1
									field += '\t'*(tabs) + '}'
								field += parseField(text, parseType, stringMode)
								ignore += offset - pick - 1
							else:
								tabs -= 1
								field += '\n' + '\t'*tabs + '}' + '\n'
								tabs -= 1
								field += '\t'*(tabs) + '}'
								if tabs - 1 in arrayLevels:
									field += ',\n' + '\t'*tabs + '{ '
									tabs += 1
									gettingClass = 1
								ignore += offset - pick - 1
							output += field
	'''if unClassable or unFieldable:
		#print "holy moly there are " + (unClassable != 0)*(str(unClassable) + " unknown classes") + (unClassable != 0 and unFieldable != 0)*" and " + (unFieldable != 0)*(str(unFieldable) + " unknown fields") + " in this file"
	else:
		print "everything probably worked ok. to be honest, i'm not sure."'''
	return output

algos = {0:coords,
			1:settings,
			2:classes,
			3:convert
}

def magic(name, directory): #applies an algorithm to a single file (which algorithm it is is based on the 'mode' variable)
	with open(directory + '\\' + name, 'rb') as f:
		device_data = f.read()
		output = ""
		if mode == 3:
			if device_data[41] == chr(0x0): #not sure how to implement this yet
				output = algos[mode](device_data)
			elif device_data[41] == '{':
				print "this file is either already converted or isn't an unreadable file"
		with open(directory + '\output\\converted ' + name, 'wb') as text_file:
			text_file.write(output)

#these function calls are for test purposes
#magic('test.bwproject', '.\devices\old devices')
#magic('Amp.bwdevice', '.\devices\old devices')
#print('decoder imported')
