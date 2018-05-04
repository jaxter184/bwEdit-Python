def countIOs(text):
	length = len(text)
	i = 0
	inports = 0
	outports = 0
	while (i < length):
		if (i < length - len("_inport")):#convert to .find()
			if text[i:i+len("_inport")] == "_inport":
				i+=len("_inport")
				if text[i] == '[':
					if ']' in text[i:i+30]:
						end = text[i:i+30].index(']')
						print(text[i-5:i+end+5])
						arraySize = text[i+1:i+end]
						arraySize.replace('+', ' + ')
						arraySize.replace('*', ' * ')
						arraySize = arraySize.split()
						arraySize = expression(text, arraySize)
						i+= end
						inports += arraySize
				else:
					inports += 1
		if (i < length - len("_outport")):
			if text[i:i+len("_outport")] == "_outport":
				i+=len("_outport")
				if text[i] == '[':
					if ']' in text[i:i+30]:
						end = text[i:i+30].index(']')
						print(text[i-5:i+end+5])
						arraySize = text[i+1:i+end]
						if arraySize.isdigit():
							arraySize = int(arraySize)
						else:
							arraySize.replace('+', ' + ')
							arraySize.replace('*', ' * ')
							arraySize = arraySize.split()
							arraySize = expression(text, arraySize)
						i+= end
						outports += arraySize
				else:
					outports += 1
		i+=1
	return inports, outports
	
def getName(text):
	index = text.find("@name")
	length = 0
	if index != -1:
		index += 7
		while text[index + length] not in ('\\','"',):
			length += 1
	else:
		index = text.find("component ")
		if index != -1:
			index += 10
			while text[index + length] != '\\':
				length += 1
		else:
			return "nameless nitro"
	return text[index:index+length]
	'''if val[0:10] == 'component ':
				name = val[10:]
				i=0
				while name[i] not in ('\\', ' '):
					i+=1
				name = name[:i]
				val=val[16+i:]
			val = val[:20]'''

def expression(text, exp):#exp is a list of terms TODO implement parentheses and subtraction
	variables = {}
	if len(exp) == 1:
		if isinstance(exp[0], int) or exp[0].isdigit():
			return int(exp[0])
		else:#its a variable name
			j = text.find(exp[0]) + len(exp[0])
			while not text[j].isdigit():
				j+=1
			nLen = 0
			while text[j+nLen].isdigit():
				nLen+=1
			return int(text[j:j+nLen])
	while '*' in exp:
		i = exp.index('*')
		exp[i] = int(expression(text, [exp[i-1]])*expression(text, [exp[i+1]]))
		del exp[i+1], exp[i-1]
	while '+' in exp:
		i = exp.index('+')
		exp[i] = int(expression(text, [exp[i-1]])+expression(text, [exp[i+1]]))
		del exp[i+1], exp[i-1]
	if len(exp) == 1:
		if isinstance(exp[0], int) or exp[0].isdigit():
			return int(exp[0])
	print("unknown expression in nitro interpretation")
	return

