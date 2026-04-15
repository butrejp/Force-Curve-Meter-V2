# Force Curve Meter V2

main.ino is the microcontroller firmware.  it is designed around a teensy 4.0, HX711, and a4988.  it should require minimal modification to run on other microcontrollers

the device firmware is designed to be as dumb as possible.  it essentially just handles serial input and outputs the absolute position (in microsteps) and HX711 data (raw adc output) to serial console in a CSV format.  

firmware controls:
```
S - Move one step (mostly useful for diagnostics or travel commands)  
SR - Move and read  
R - read without moving  
D 1 - set direction: loading  
D 0 - set direction: unloading  
W 200 - set settle time for SR command  
Z - tare load cell
```

additional data will be uploaded soon.

## TODO ##
create BOM
finalize+upload linear stage design
create client side control software
create data parsing software
