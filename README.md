# bwConvert
Python script for making .bwdevice files readable

Changelog v0.2:  
-Added support for modulators  
-Added float parsing  
-Added float array parsing (doesnt actually read values, purely a formatting thing)  
-Added UTF-16 support  
-Fixed formatting  
-Fixed pre-header (not sure if it was broken in the first place, I'll have to test that later)  
-Fixed ints not being parsed in section 0 (Bitwig file description header)  
-Fixed leading zeros not being read in hex parsing  
-Fixed negative ints being read incorrectly  
-Improved feedback when class and field names are unknown  
-Removed profanity  
-Removed .txt extension from output  

Holy moly, it took me like an hour to realize that Python was inserting carriage returns as well as newlines. I hate carriage returns. I didn't even end up figuring it out, someone had to tell me (thanks zezic). On the bright side, Bitwig can now open these files! The visualization is a little janky and some of the devices don't work 100%, so that's next on my list of things to fix. After that, I'll make a better interface (with instructions and waiting and better feedback!).


Previous changelogs:

Changelog v0.1:
-Can convert things. Kinda.  
-New file 'decoder.py': All of the algorithm stuff is in here  
-New file 'crawl.py': Parent function that applies decoder.py to all the files in the .\devices subdirectory  
-New file 'chord.py': Helper functions for applying ord() to longer strings (todo: do the same thing for chr())  
-New file 'reCrawl.py': Goes through the outputs and collates them (todo: rename this)  
-New file 'tables.py': Contains the dictionaries to match integer values with parameter and class names. Data collected using reCrawl.py  
-Converts map<string, object>  
-Strings now support utf-16  

Notes:  
So far it does most .bwdevices fine, there are a couple big issues with the instruments (FM4, Organ, Polysynth, Sampler, and Note MOD). Also, the converted files don't open in Bitwig. I'll have to compare them after I figure out the instrument issue to see whats up.
