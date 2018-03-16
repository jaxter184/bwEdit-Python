import os
from src import decoder

root_dir = '.\devices'
folder = {0:'.\devices',
			 1:'.\devices\old devices'}

decoder.mode = 3
print ("Heyo I'm Jaxter, thanks for using my little script. Notice how I said 'my'. That's right, this is something that I made, and you should therefore be pretty careful about using it. I won't take responsibility for breaking your Bitwig devices, so make sure you have a copy of them saved somewhere before starting. Also, be cautious in general; just because I trust my own work doesn't mean you should.\nNow, with the fearmongering out of the way, lets get started.\n")
try:
	inputDir = input("Enter the subdirectory that your devices are in. (If this script is in the same folder as them, just press enter)")
except SyntaxError:
	inputDir = ''
inputDir = '.' + inputDir
if not os.path.exists('output'):
	os.mkdir('output')
for file in os.listdir(inputDir):
	if file.endswith(".bwdevice") or file.endswith(".bwproject") or file.endswith(".bwmodulator") or file.endswith(".bwpreset") or file.endswith(".bwclip") or file.endswith(".bwscene"):
		print ('-'+file)
		decoder.magic(file, inputDir)
input("All done. Let me know if you had any issues using this or have suggestions for improving it. [Press Enter to exit]")