As I'm not sure of the wiring configuration of the Greenpower car, I've left thermistors and buttons unwired.
Wiring should be as follows (Arduino):

D2: 'left' button
D3: 'right' button
D4: 'select' button

A0: across first battery via the marked voltage divider
A1: across second battery via the marked voltage divider
A2: across motor thermistor
A3: across motor controller thermistor

I've left the SIM800L unwired, as it requires an antenna connected through a short U.FL cable: I'm not sure if the electronics board would be mounted near any potential antenna locations.

The CHIP program requires python3- it can either be started via a cron job or manual execution via 'sudo python GUI.py' while in the code directory