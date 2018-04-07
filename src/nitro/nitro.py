def countIOs(text):
	length = len(text)
	i = 0
	inports = 0
	outports = 0
	while (i < length):
		if (i < length - len("inport")):
			if text[i:i+len("inport")] == "inport":
				inports += 1
		if (i < length - len("outport")):
			if text[i:i+len("outport")] == "outport":
				outports += 1
		i+=1
	return inports, outports