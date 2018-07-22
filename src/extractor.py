import struct
from collections import OrderedDict
from src.lib import atoms
import uuid

stringMode = 0
endFlag = 0
def parseField():
	global text, offset, output, stringMode, endFlag, currentSection
	if endFlag:
		return ''
	parseType = text[offset]
	offset += 1
	#print(hex(parseType))
	if parseType == 0x01:	#8 bit int
		offset += 1
	elif parseType == 0x02:	#16 bit int
		offset += 2
		return 1
	elif parseType == 0x03:	#32 bit int
		offset += 4
		return 1
	elif parseType == 0x05:	#boolean
		offset += 1
	elif parseType == 0x06:	#float
		offset += 4
	elif parseType == 0x07:	#double
		offset += 8
	elif parseType == 0x08:	#string
		if stringMode == 0:
			stringLength = intConv(text[offset:offset+4])
			offset += 4
			sFormat = 0 #0:utf-8, 1:utf-16
			if (stringLength & 0x80000000):
				stringLength &= 0x7fffffff
				sFormat = 1
			if (stringLength > 100000):
				offset += 4
				return 'too long'
			offset += stringLength*(sFormat + 1)
		elif stringMode == 1:
			while (text[offset]) != 0x00:
				if endFlag:
					break
				offset += 1
			offset += 1
	elif parseType == 0x09:	#object
		getClass()
	elif parseType == 0x0a:	#null
		return None
	elif parseType == 0x0b:	#object reference
		offset += 4
		return 9
	elif parseType == 0x0d: #structure										#not done yet
		headerLength = intConv(text[offset:offset+4])
		offset += 4
		if currentSection == 2:
			#offset += 57 #not sure when to put this in
			offset += headerLength
		elif headerLength<54:
			print("short header at " + hex(offset))
			offset += 54
			stringMode = 1
			getClass()
			stringMode = 0
		else:
			offset += headerLength
	elif parseType == 0x12:	#object array
		while (intConv(text[offset:offset+4]) != 0x3):
			if endFlag:
				break
			getClass()
		offset += 4
	elif parseType == 0x14:	#map string
		parseType2 = (text[offset])
		offset += 1
		if parseType2 == 0x1:
			stringLength = intConv(text[offset:offset+4])
			offset += 4
			offset += stringLength
			getClass()
			offset+=1
	elif parseType == 0x15:	#UUID
		offset += 16
	elif parseType == 0x16:	#color
		offset += 16
	elif parseType == 0x17:	#float array
		arrayLength = intConv(text[offset:offset+4])
		offset += 4
		offset += arrayLength*4
	elif parseType == 0x19: #string array
		arrayLength = intConv(text[offset:offset+4])
		offset += 4
		for i in range(arrayLength):
			strLength = intConv(text[offset:offset+4])
			offset += 4
			offset+=strLength
	elif parseType == 0x1a: #fuck if i know								#not done yet
		#print("shit,1a ")
		strLength = 0
		while (text[offset] == 0x00):
			strLength = intConv(text[offset:offset+4])
			offset += 4
			if strLength  == 0x90:
				return
		offset += strLength
	else:
		endFlag = 1
		print('unknown type at ' + hex(offset-1) + ', ' + str(parseType))
		return 'end here'
	return parseType

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

def addField(fieldName):
	global text, fieldList
	fieldType = parseField()
	if fieldName not in fieldList:
		fieldList[fieldName] = fieldType
	elif fieldList[fieldName] == None:
		fieldList[fieldName] = fieldType
	else:
		if fieldType and fieldList[fieldName] != fieldType:
			print(fieldType)
			print(type(fieldList[fieldName]))
			print("somethings wrong. oopsie woopsie fucky wucky code is \'different encoder fields\'")
			#print(str(fieldList[fieldName]) + ', ' + str(fieldType))

def getParams():
	global text, offset, classList, fieldList, unClassable, unFieldable, endFlag
	fieldNum = intConv(text[offset:offset+4])
	offset += 4
	output = []
	while (fieldNum):
		if endFlag:
			break
		#print("field: " + hex(offset-4))
		fieldName = ''
		value = 'placeholder'
		if fieldNum > 10:
			#print('f'+hex(fieldNum))
			addField(fieldNum)
		else:
			print("weird field detected at " + hex(offset))
			fieldName = text[offset:offset+fieldNum].decode()
			offset += fieldNum
			value = fieldName
			classList[fieldName] = getParams()
		output.append(fieldNum)
		fieldNum = intConv(text[offset:offset+4])
		offset += 4
	return output
	
def getClass():
	global text, offset, classList, unClassable, endFlag
	if endFlag:
		return
	classNum = intConv(text[offset:offset+4])
	offset += 4
	if classNum == 0x1: #object references
		offset += 4
	else:
		#print(classNum)
		classList[classNum] = getParams()
	return

def reformat(input):
	output = input
	i = 0
	length = len(output)
	while (i < len(output)):
		i+=1
	return output
		
def bwExtract(textIn):
	global text, offset, classList, fieldList, unClassable, unFieldable, endFlag, currentSection
	text = textIn
	endFlag = 0
	atoms.resetId()
	currentSection = 0
	classList = {}
	fieldList = {}
	unClassable = 0
	unFieldable = 0
	textLength = len(text)
	offset = 40
	list = OrderedDict()
	while offset < textLength:
		if endFlag:
			break
		if currentSection == 0: #getting the header info
			keyType = intConv(text[offset:offset+4])
			offset += 4
			if keyType == 0x0: #end of array
				metaList = list
				currentSection = 1
			elif keyType == 0x1: #parameter
				keyLength = intConv(text[offset:offset+4]) #length of the string
				offset += 4
				key = bigChr(text[offset:offset+keyLength])
				offset += keyLength
				addField(key)
			elif keyType == 0x4: #object
				stringLength = intConv(text[offset:offset+4])
				offset += 4
				name = bigChr(text[offset:offset+stringLength])
				offset += stringLength
		elif currentSection == 1: #intermediary section (whitespaces)
			if (text[offset]) == 0x0a:
				currentSection = 2
				offset+=1
			else:
				offset+=1
		elif currentSection == 2:
			getClass()
	if not endFlag:
		print("everything probably worked ok. to be honest, i'm not sure.")
	return (classList, fieldList)