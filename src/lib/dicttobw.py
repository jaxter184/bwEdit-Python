from src.lib import atoms

def convert(inDict):
	if 'class' in inDict:
		output = atoms.Atom(inDict['class'])
		output.setID(inDict['object_id'])
		for i in inDict['data']:
			val = inDict['data'][i]
			if isinstance(val, dict):	
				val = convert(val)
			elif val and isinstance(val, list):
				if isinstance(val[0], dict):
					val = [convert(v) for v in val]
			output.add_field(i, val)
		return output
	elif 'type' in inDict:
		if inDict['type'] == 'color':
			return atoms.Color(*inDict['data'])
	else:
		print(inDict)
		return inDict