consider this a preview repository for now.  as-is it's incomplete.  in the coming days/weeks it will become less incomplete
> [!WARNING]  
> [Do not attempt to use this until further testing and validation has been done.]  
> [I am not responsible for any damage that occurs because you ignored this warning.]  
only partial testing has been done, as not all the hardware has come in the mail yet.  I'll go over any bugs as I receive the hardware

# Force Curve Meter V2

main.ino is the microcontroller firmware.  it is designed around a teensy 4.0, HX711, and a4988.  it should require minimal modification to run on other microcontrollers, but that's on you  
fdm.py is a minimal command line interface.  usage details are below

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
fdm.py usage
```
TEST MODE
---------
usage: fdm.py test [-h] [--port PORT] --threshold THRESHOLD [--out OUT]
                   [--mock] [--debug] [--calib CALIB]

Run a load-unload force-displacement test.

required arguments:
  --threshold THRESHOLD
                        Force threshold (gf if calibration provided, otherwise raw adc value) that triggers reversal from LOAD to UNLOAD

optional arguments:
  -h, --help            show this help message and exit
  --port PORT           Serial port (default: COM3)
  --out OUT             Output CSV file (default: out.csv)
  --mock                Run without hardware (simulated controller)
  --debug               Print live state updates during execution
  --calib CALIB         Calibration CSV file (gf,counts) used to convert raw readings

  CALIBRATION MODE
----------------
usage: fdm.py calib [-h] [--port PORT] [--out OUT] [--mock]
                    [--samples SAMPLES]

Run interactive calibration routine using known force values.

optional arguments:
  -h, --help         show this help message and exit
  --port PORT        Serial port (default: COM3)
  --out OUT          Output calibration file (default: calib.csv)
  --mock             Run without hardware (simulated controller)
  --samples SAMPLES  Maximum number of calibration points (default: 100)
```

additional data will be uploaded soon.

## TODO ##  
create BOM  
finalize+upload linear stage design  
create data parsing software  






the code in this repository is broadly hardware agnostic and should apply to any force curve machine you might build so long as the featureset lines up.  buy a linear stage off aliexpress, port it to arduino, whatever you want to do.  nothing is non-negotiable, 
