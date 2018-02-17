# bwConvert
Python script for making .bwdevice files readable

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
