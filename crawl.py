import os
from decoder import *

root_dir = '.\devices'
mode = 1
folder = {0:'.\devices',
			 1:'.\devices\old devices'}

for directory, subdirectories, files in os.walk(root_dir):
	for file in files:
		if directory == folder[mode]:
			#print directory
			#if file == 'Amp.bwdevice':
			print '-'+file
			magic(file, directory)