import struct
from collections import OrderedDict
from src.lib import atoms

endFlag = 0

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

def bwEncode(objList):
	global output, endFlag, currentSection
	if endFlag:
		return ''
	atoms.resetId()
	currentSection = 0
	output = bytearray(b'')
	for object in objList:
		if endFlag:
			break
		if currentSection == 0:
			#print (object)
			if isinstance(object, atoms.Atom):
				output += object.encode()
		if currentSection == 1:
			output.extend((' '*5000).encode('utf-8'))
			output += bytearray.fromhex('0a')
			if isinstance(object, atoms.Atom):
				output += object.encode()
			else:
				print('something went wrong, but im gonna keep going. For reference, the oopsie woopsie fucky wucky code is \'section 1 in bwEncode\'')
		currentSection+=1
	print("encode complete")
	return output