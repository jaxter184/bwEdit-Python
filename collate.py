import os

root_dir = '.\output'
output = {}

for directory, subdirectories, files in os.walk(root_dir):
	for file in files:
		if directory == root_dir:
			with open(directory + '\\' + file, 'r') as f:
				print '-'+file
				text = f.readlines()
				for lines in text:
					index = 0
					while lines[index] != ',':
						index+=1
					if lines[-1:] != '\n':
						lines += '\n'
					output[int(lines[:index])] = lines[index + 1:]

	with open('collated.txt', 'w') as fileOutput:
		textOutput = ''
		for params in range(output, keys=int):
			if params in output:
				textOutput += str(params) + ':"' + output[params][:-1] + '",\n'
		fileOutput.write(textOutput)
		print "done"
