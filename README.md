# eHZ_EDL21_SML_Meter
eHZ EDL21 Energy Meter Reader

The program decodes SML packets from a eHZ EDL21 electricity meter and send any power value to xively.
It is developt and tested under windows in pycharm. I used an infrared detector head http://wiki.volkszaehler.org/doku.php/hardware/controllers/ir-schreib-lesekopf-ttl-ausgang
for the meter.
To figure out the regex key's for parsing I used this tool https://regex101.com/r/dY0lZ5/1 .
I'd brougth the scricp to on a rasbperry pi b+ and could it run after changing the serial port. ('/dev/ttyUSB0') In my case.

