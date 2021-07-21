# Resistance Tester Programs Repo

These programs run on a test control computer (Raspberry Pi 4)
and are used to control the Tarte-Py and TraceR modules for 
various tests.

## Files

* `rtester.py`

Program to send packets of data to the Tarte-Py over the serial port.
The Tarte-Py board echoes those packets back, and the program checks 
for and tallies errors.

* `rsweep.py`

This program sweeps across a range of resistance values for a TraceR module, 
and takes an oscilloscope screenshot at each setting. 


* `keithley.py`
* `tracer.py`

These are copied from their respective repositories. 
TODO: make these a local library instead of manual copying.

* `source.agc`

This is the corpus of text data used in for serial port testing.
It is a single file made by appending all the source code files 
from the Apollo 11 Lunar Module AGC computer called Luminary 99.

* `logs`

Log files from `rtester.py` are renamed and stored in this directory.

* `sweeps`

Screenshots from `rsweep.py` are renamed and stored in this directory.
