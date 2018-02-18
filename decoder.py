from chord import *
import struct
from tables import *

mode = 3
#0:coords,
#1:settings,
#2:classes,
#3:convert

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
	#output = text[:39] #BtWg header
	#output += '1'
	output = 'BtWg00010001008d000016a00000000000000000'
	output += '{\n\t'
	gettingClass = 0
	ignore = 0
	objid = 1
	currentSection = 0
	tabs = 1
	arrayLevels = []
	firstField = 1
	flag = 0
	inMap = 0
	for pick in range(len(text)):
		#print hex(pick)
		if ignore:
			ignore -= 1
			#print 'i'
		elif pick >= 40:
			#print 'p'
			if currentSection == 0:
				if pick < len(text)-8:
					#print(bigOrd(text[pick:pick+4]))
					#print pick
					if bigOrd(text[pick:pick+4]) == 0x4:
						offset = 4 + pick
						parse = bigOrd(text[offset:offset+4])
						offset += 4
						if offset+parse > len(text):
							print("error 801: the parse code says to go further than the end of the file :/")
						output += 'class : "' + text[offset:offset+parse] + '",\n'
						offset += parse
						output += '\t'*tabs + 'object_id : ' + str(objid) + ',\n'
						output += '\t'*tabs + 'data :\n' + '\t'*tabs + '{\n' + '\t'*(tabs + 1)
						objid += 1
						tabs += 1
						ignore += offset - pick - 1
					elif bigOrd(text[pick:pick+4]) == 0x1:
						offset = pick + 4
						parseKey = bigOrd(text[offset:offset+4]) #length of the string
						offset += 4
						key = text[offset:offset+parseKey]
						offset += parseKey
						parse2Type = ord(text[offset])
						offset += 1
						value = ''
						if parse2Type == 0x1: #8 bit int
							val = ord(text[offset])
							if val & 0x80:
								val -= 0x100
								neg = 1
							value += str(val)
							offset += 1
						elif parse2Type == 5: #boolean
							if offset+1 > len(text):
								print("error 502: how did you get here, this should only happen if there is a boolean field at the end of the file")
							if ord(text[offset]): #pick+8 + parse+4 +1 : pick+8 + parse+8 +1
								value = 'true'
							else:
								value += 'false'
							offset += 1
						elif parse2Type == 3: #16 bit int
							value += str(bigOrd(text[offset:offset + 4]))
							offset += 4
						elif parse2Type == 8: #string
							if offset+4 > len(text):
								print("error 802: the parse code says to go further than the end of the file :/")
							parse2 = bigOrd(text[offset:offset+4]) #pick+8 + parse+1 : pick+8 + parse+4 +1
							offset += 4
							value = '"' + text[offset:offset+parse2] + '"' #pick+8 + parse+4 +1 : pick+8 + parse+4 +1 + parse2
							offset += parse2
						elif parse2Type == 21: #hex value
							if pick+offset+16 > len(text):
								print("aw poop")
							value += '"'
							for i in range(16):
								if i in [4,6,8,10]:
									value += '-'
								value += "{0:0{1}x}".format(ord(text[offset+i]),2)
							value += '"'
							offset += 16
						else:
							print "missing type in section 0"
						output += '"' + key + '" : ' + value + ',\n' + '\t'*tabs
						ignore += offset - pick - 1
						#if parse2Type == 21:
						#	print pick + ignore
					elif bigOrd(text[pick:pick+4]) == 0x0:
						#print str(pick) + 'poop'
						tabs -= 1
						output = output[:(tabs + 3)*-1] + '\n' + '\t'*(tabs) + '}\n' + '}\n' + '{' #tabs add offset value might be wrong
						ignore += 4
						objid = 1
						currentSection = 1
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
										print "pesky new class"
								objid += 1
								tabs += 1
								firstField = 1
								gettingClass = 0
							ignore += offset - pick - 1
						else:
							offset = pick
							fieldNum = bigOrd(text[offset:offset+4])
							offset += 4
							if fieldNum:
								if not firstField:
									output += ','
								else:
									firstField = 0
								if fieldNum in params:
									output += '\n' + '\t'*tabs + '"' + params[fieldNum] +  '(' + str(fieldNum) + ')" : '
								else:
									output += '\n' + '\t'*tabs + '"' + "missing_field" +  '(' + str(fieldNum) + ')" : '
									if not fieldNum in [7489, 7490, 7243, 7235]:
										#print tabs										
										print "missing field " + str(fieldNum) + ', ' + hex(pick) + ', ' + str(output.count('\n') + 1)
									else:
										print "pesky new field"
								parseType = ord(text[offset])
								offset += 1
								if flag:
									print 'flag ' + str(fieldNum) + ' - ' + hex(parseType) + ', ' + hex(pick) + ', ' + str(output.count('\n') + 1)
									flag -= 1
								if parseType == 0xa: #null
									output += 'null'
								elif parseType == 0x1: #8 bit int
									val = ord(text[offset])
									if val & 0x80:
										val -= 0x100
										neg = 1
									output += str(val)
									offset += 1
								elif parseType == 0x2: #16 bit int
									val = bigOrd(text[offset:offset + 2])
									if val & 0x8000:
										val -= 0x10000
									output += str(val)
									offset += 2
								elif parseType == 0x3: #32 bit int
									val = bigOrd(text[offset:offset + 4])
									if val & 0x80000000:
										val -= 0x100000000
										neg = 1
									output += str(val)
									offset += 4
								elif parseType == 0x5: #boolean
									if offset + 1 > len(text):
										print("error 502: how did you get here, this should only happen if there is a boolean field at the end of the file")
									if ord(text[offset]): #pick+8 + parse+4 +1 : pick+8 + parse+8 +1
										output += 'true'
									else:
										output += 'false'
									offset += 1
								elif parseType == 0x6: #float
									flVal = struct.unpack('f', struct.pack('L', bigOrd(text[offset:offset + 4])))[0]
									output += str(flVal)
									offset += 4
								elif parseType == 0x7: #double
									dbVal = struct.unpack('d', struct.pack('Q', bigOrd(text[offset:offset + 8])))[0]
									output += str(dbVal)
									offset += 8
								elif parseType == 0x8: #string
									if offset + 1 > len(text):
										print("error 802: the parse code says to go further than the end of the file :/")
									stringLength = bigOrd(text[offset:offset+4]) #pick+8 + parse+1 : pick+8 + parse+4 +1
									offset += 4
									string = ''
									sFormat = 0 #0:utf-8, 1:utf-16
									if (stringLength & 0x80000000):
										#print 'utf-16 string found'
										stringLength &= 0x7fffffff
										sFormat = 1
									#if (stringLength > 10000): #was making some code blocks not convert lol, hopefully i dont need this failsafe anymore
									#	print str(stringLength) + ' string is waaaaay too long' + hex(pick) + ', ' + str(output.count('\n') + 1)
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
									output += '"' + string + '"' #pick+8 + parse+4 +1 : pick+8 + parse+4 +1 + parse2
									offset += stringLength*(sFormat + 1)
								elif parseType == 0x9: #object
									output += '\n' + '\t'*tabs + '{ '
									tabs += 1
									gettingClass = 1
								elif parseType == 0xb: #object reference
									output += '{ object_ref : ' + str(bigOrd(text[offset:offset+4])) + ' }'
									offset += 4
								elif parseType == 0x12: #object array
									arrayLevels.append(tabs)
									output += '\n' + '\t'*tabs + '[\n' + '\t'*(tabs + 1) + '{ '
									tabs += 2
									gettingClass = 1
								elif parseType == 0x14: #map string to object
									output += '\n' + '\t'*tabs + '{\n'
									tabs += 1
									output += '\t'*(tabs) + 'type : "map<string,object>",\n' + '\t'*(tabs) + 'data :\n' + '\t'*tabs + '{\n' 
									tabs += 1
									output += '\t'*(tabs)
									parseType2 = ord(text[offset])
									offset += 1
									if parseType2 == 0x1: 
										stringLength = bigOrd(text[offset:offset+4])
										offset += 4
										output += '"' + text[offset:offset+stringLength] + '" : \n' + '\t'*(tabs) + '{'
										tabs += 1
										offset += stringLength
									inMap = 2
									gettingClass = 1
								elif parseType == 0x15: #hex value
									if offset+16 > len(text):
										print("aw poop")
									output += '"'
									for i in range(16):
										if i in [4,6,8,10]:
											output += '-'
										#print "{0:0{1}x}".format(ord(text[offset+i]),2)
										output += "{0:0{1}x}".format(ord(text[offset+i]),2)
									output += '"'
									offset += 16
								elif parseType == 0x16: #color
									output += '\n' + '\t'*tabs + '{\n' + '\t'*(tabs + 1) + 'type : "color",\n' + '\t'*(tabs + 1) + 'data : [0.5, 0.5, 0.5]\n' + '\t'*tabs + '}'
									offset += 16
								elif parseType == 0x17: #float array
									output += '\n' + '\t'*tabs + '{\n' + '\t'*(tabs + 1) + 'type : "float[]",\n' + '\t'*(tabs + 1) + 'data : ['
									arrayLength = bigOrd(text[offset:offset+4]) #pick+8 + parse+1 : pick+8 + parse+4 +1
									offset += 4
									output += ']\n' + '\t'*tabs + '}'
									offset += arrayLength*4
								else:
									print 'unknown type at ' + hex(offset-1) + ', ' + str(output.count('\n') + 1)
								if inMap == 1:
									offset += 1
									inMap = 0
									tabs -= 1
									output += '\n' + '\t'*tabs + '}' + '\n'
									tabs -= 1
									output += '\t'*(tabs) + '}'
								elif inMap == 2:
									inMap = 1
								ignore += offset - pick - 1
								if parseType == 0x16:
									pass
									#print ignore + pick
							else:
								tabs -= 1
								output += '\n' + '\t'*tabs + '}' + '\n'
								tabs -= 1
								output += '\t'*(tabs) + '}'
								if flag:
									print 'flag2 - ' + str(tabs - 1 in arrayLevels) + ': ' + hex(pick) + ', ' + str(output.count('\n') + 1)
									flag -= 1
								if tabs - 1 in arrayLevels:
									output += ',\n' + '\t'*tabs + '{ '
									tabs += 1
									gettingClass = 1
								#print 'blank ' + hex(offset) + ', ' + str(offset - pick)
								ignore += offset - pick - 1
								#print ignore + pick
	return output

algos = {0:coords,
			1:settings,
			2:classes,
			3:convert
}

def magic(name, directory):
	with open(directory + '\\' + name, 'rb') as f:
		device_data = f.read()
		output = ""
		output = algos[mode](device_data)
		with open(directory + '\output\edited' + name, 'wb') as text_file:
			text_file.write(output)

magic('Amp.bwdevice', '.\devices\old devices')
print('decoder imported')
