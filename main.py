import os
from src import decoder, encoder, extractor
from src.lib import fs, util, atoms, route, dicttobw
from src.lib.luts import typeLists

root_dir = '.\devices'
folder = {0:'.\devices',
			 1:'.\devices\old devices'}

classExtract = 0 #change this to 0 for regular operation and 1 for class extraction. most users won't need class extraction, as it is just a tool I use to make internal files
			 
def magic(name, directory): #decodes then reencodes a single file
	global extractedClasses, extractedFields
	device_data = fs.read_binary(os.path.join(directory, name))
	header = device_data[:40].decode("utf-8") #'BtWg00010001008d000016a00000000000000000'
	if (header[11] == '2'):
		if (classExtract):
			classes,fields = extractor.bwExtract(device_data)
			extractedClasses.append(classes)
			extractedFields.append(fields)
		else:
			#decode
			header = header[:11] + '1' + header[12:]
			output = ''
			gather = decoder.bwDecode(device_data)
			for item in gather: #encodes all of the objects in the output list
				output += util.json_encode(atoms.serialize(item))
			output = header + decoder.reformat(output)
			with open('output\\converted ' + name, 'wb') as file:
				file.write(output.encode("utf-8"))
			
			#reencode
			gather2 = encoder.bwEncode(gather)
			header = header[:11] + '2' + header[12:]
			output2 = header.encode('utf-8') + gather2
			with open('output\\reconverted ' + name, 'wb') as file:
				file.write(output2)
	#elif (device_data[42] == '{'):
	#	print("this file is either already converted or isn't an unreadable file")
	elif (header[11] == '1'):
		device_data = fs.read(os.path.join(directory, name))[40:]
		i = 1
		brackSum = 1
		while brackSum:
			if device_data[i] == '{':
				brackSum += 1
			elif device_data[i] == '}':
				brackSum -= 1
			i += 1
		objectified = [dicttobw.convert(util.json_decode(device_data[:i])),dicttobw.convert(util.json_decode(device_data[i:]))]
		print(objectified)
		gather = encoder.bwEncode(objectified)
		header = header[:11] + '2' + header[12:]
		output2 = header.encode('utf-8') + gather
		with open('output\\jsonconv ' + name, 'wb') as file:
			file.write(output2)
	else:
		print("i don't know what kind of file this is")

def x_in_y(query, base): #got this from online somewhere
    try:
        l = len(query)
    except TypeError:
        l = 1
        query = type(base)((query,))

    for i in range(len(base)):
        if base[i:i+l] == query:
            return True
    return False

def extractClasses():
	global extractedClasses, extractedFields
	collatedClassDict = typeLists.classList
	collatedFieldDict = typeLists.fieldList
	#collatedClassListErrors = {}
	for eachFile in extractedClasses:
		for eachClass in eachFile:
			if eachClass in collatedClassDict:
				###check to see if the class matches the existing class
				#diffkeys = [k for k in collatedClassDict[eachClass] if collatedClassDict[eachClass][k] != eachFile[k]]
				#if diffkeys:
				if collatedClassDict[eachClass] != eachFile[eachClass]:
					if set(eachFile[eachClass])>set(collatedClassDict[eachClass]):
						collatedClassDict[eachClass] = eachFile[eachClass]
					elif set(eachFile[eachClass])<set(collatedClassDict[eachClass]):
						eachFile[eachClass] = collatedClassDict[eachClass]
					if collatedClassDict[eachClass] != eachFile[eachClass]:
						print("oopsie woopsie fucky wucky code is \'conflicting class\'")
						print(eachClass)
						print(collatedClassDict[eachClass])
						print(eachFile[eachClass])
						#collatedClassListErrors[eachClass] = (eachFile[eachClass])
			else:
				#print(eachFile[eachClass])
				collatedClassDict[eachClass] = (eachFile[eachClass])
	for eachFile in extractedFields:
		for eachField in eachFile:
			if eachField in collatedFieldDict:
				###check to see if the class matches the existing class
				#diffkeys = [k for k in collatedFieldDict[eachClass] if collatedFieldDict[eachClass][k] != eachFile[k]]
				#if diffkeys:
				if collatedFieldDict[eachField] != eachFile[eachField]:
					if collatedFieldDict[eachField] == None:
						collatedFieldDict[eachField] = eachFile[eachField]
					elif eachFile[eachField] == None:
						eachFile[eachField] = collatedFieldDict[eachField]
					if collatedFieldDict[eachField] != eachFile[eachField]:
						print("oopsie woopsie fucky wucky code is \'conflicting field\'")
						print(collatedFieldDict[eachField])
						print(eachFile[eachField])
						#collatedClassListErrors[eachField] = (eachFile[eachField])
			else:
				#print(eachFile[eachField])
				collatedFieldDict[eachField] = (eachFile[eachField])
	with open('typeLists.py', 'w') as file:
		output = str(collatedClassDict).replace('], ', '],\n').replace('{', 'classList = {\n').replace('}', '\n}')
		output2 = str(collatedFieldDict).replace(', ', ',\n').replace('{', 'fieldList = {\n').replace('}', '\n}')
		file.write(output + '\n' + output2)

print ("Heyo I'm Jaxter, thanks for using my little script. Notice how I said 'my'. That's right, this is something that I made, and you should therefore be pretty careful about using it. I won't take responsibility for breaking your Bitwig devices, so make sure you have a copy of them saved somewhere before starting. Also, be cautious in general; just because I trust my own work doesn't mean you should.\nNow, with the fearmongering out of the way, lets get started.\n")
try:
	inputDir = input("Enter the subdirectory that your devices are in. (If they're in the 'inputs' folder, just press enter)")
except SyntaxError:
	inputDir = ''
if not inputDir:
	inputDir = 'input'
else:
	inputDir = '.' + inputDir
if not os.path.exists('output'):
	os.mkdir('output')
extractedClasses = []
extractedFields = []
#print(inputDir)
for file in os.listdir(inputDir):
	if file.endswith((".bwdevice",".bwmodulator",".bwpreset",".bwclip",".bwscene",".bwremotecontrols",".bwproject")):
		print ('-'+file)
		#if file != "Phase-4.bwdevice": continue #use this to isolate a file
		magic(file, inputDir)
	elif file.endswith('poop',):
		print ('*skipping '+file)
if classExtract:
	extractClasses()
input("All done. Let me know if you had any issues using this or have suggestions for improving it. [Press Enter to exit]")