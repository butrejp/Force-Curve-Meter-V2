consider this a preview repository for now.  as-is it's incomplete.  in the coming weeks it will become less incomplete

# Force Curve Meter V2

main.ino is the microcontroller firmware.  it is designed around a teensy 4.0, HX711, and a4988.  it should require minimal modification to run on other microcontrollers, but that's on you

the device firmware is designed to be as dumb as possible.  it essentially just handles serial input and outputs the absolute position (in microsteps) and HX711 data (raw adc output) to serial console in a CSV format.  

firmware controls:
```
S<n>  - step n number of times 
SR<n> - step and read n number of times 
R<n>  - read without moving n number of times
D<n>  - set direction (1 loading, 0 unloading)   
W<n>  - set settle time for SR command  
Z     - tare load cell
```

additional data will be uploaded soon.

## TODO ##  
create BOM  
finalize+upload linear stage design  
create client side control software  
create data parsing software  






the code in this repository is broadly hardware agnostic and should apply to any force curve machine you might build.  buy a linear stage off aliexpress, port it to arduino, whatever you want to do.  nothing is non-negotiable 
