# bwEdit
Python3-based GUI application for editing Bitwig files  
To use the editor, just run 'editor.py' and load a file from anywhere on your computer.  
To use the converter, put items in the 'input' folder and run 'convert.py'. Outputs will show up in a folder labelled 'output'.  
collate.py is just there for decoration.

Editor commands:  
-Click an atom to view its data  
-Click an atom's node to start a connection, then click a different atom's corresponding node to complete the connection  
-Click a connection to delete it  
-Drag an atom to move it around

## Changelogs  

Changelog v0.6.2:  
-Fixed Linux and Windows 7 icon loading issues (unconfirmed) 
-Fixed nitro port number counting   
-Fixed FX chain atom (no longer crashes Bitwig)  
-Added nitro code export  

A couple fixes. To be honest, I haven't really been keeping track of what I've been doing. I'll try to document stuff more.

Previous changelogs:

Changelog v0.6.1:  
-Revamped data structures (basically fancy talk for "i organize the numbers differently")  
-Added saving and exporting for edits to the file

Changelog v0.6.0:  
-Added editor  
-Removed viewer  
-Removed dependency: kivy

Changelog v0.5:  
-Added viewer  
-Added dependency: kivy  
-Changed the way data is stored internally (thanks, stylemistake)  

Changelog v0.4:  
-Upgraded to Python 3.6  
-Added support for more filetypes (basically already worked, just had to whitelist their names)  

Changelog v0.3:  
-Improved interface (less minimal, but easier to use in my opinion)  
-Improved .bwproject support (still doesn't work, but lists all the tracks and their names/types)  
-Improved formatting of code and readme (to match how stylemistake does stuff)  
-Fixed some visualizers not loading correctly  
-Changed name of reCrawl.py to collate.py  
-Removed chord.py and moved contents to decoder.py  

Changelog v0.2:  
-Added support for modulators  
-Added float parsing  
-Added float array parsing (doesnt actually read values, purely a formatting thing)  
-Added UTF-16 support  
-Fixed formatting (thanks, zezic)  
-Fixed pre-header (not sure if it was broken in the first place, I'll have to test that later)  
-Fixed ints not being parsed in section 0 (Bitwig file description header)  
-Fixed leading zeros not being read in hex parsing  
-Fixed negative ints being read incorrectly  
-Improved feedback when class and field names are unknown  
-Removed profanity  
-Removed .txt extension from output  

Changelog v0.1:  
-Can convert things. Kinda.  
-New file 'decoder.py': All of the algorithm stuff is in here  
-New file 'crawl.py': Parent function that applies decoder.py to all the files in the .\devices subdirectory  
-New file 'chord.py': Helper functions for applying ord() to longer strings (todo: do the same thing for chr())  
-New file 'reCrawl.py': Goes through the outputs and collates them (todo: rename this)  
-New file 'tables.py': Contains the dictionaries to match integer values with parameter and class names. Data collected using reCrawl.py  
-Converts map<string, object>  
-Strings now support utf-16  

## Contact    
[jaxter184](jaxter184@gmail.com)
