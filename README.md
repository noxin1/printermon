# printermon
Python Scripts to monitor 3D Printers and change a USB LED color to indicate Status

Hardware Required
A Host - Initial development was done on a Raspberry PiZeroW
A USB Port per printer to be monitored, either a Hub or Direct on Host
A USB Led Module (Adafruit Neo Trinkey, fit-statUSB, or Similar) 
A network connection between the Host and the 3D Printer Management Software

Software Required
Requires the following python3 modules:
ToBeAdded

printers.led is the configuration file

Example stanzas are in printers.led.syntax

Originally written to support the fit-statUSB since I had a number of them available.   They appear to have been End of Life'd.
