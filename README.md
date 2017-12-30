# open_fbv

## Introduction
Line6's hardware uses the a so-called asynchronous serial communication over RS-485 to exchange messages between their multi-effect/amp-devices and the pedals like the Shortboard, Shortboard MkII, FBV3, Longboard or the Fbv Express. Unfortunately, sending serial data over RS-485 is not possible using a standard computer. Therefore, an interface for converting the PC's TTL data to the electrical characteristics of the RS-485 standard is necessary. Luckily, RS-485 is a widely used standard and there are plenty of converter modules available. 

Besides RS-485 communication, each pedal needs a suply voltage of 7,5V. In Line6's ecosystem, the multi-effect/amp-device powers the connected board by providing the desired voltage over the Ethernet cable. Since we are going to replace Line6's multi-effect/amp-device in this project, we need to provide the power supply for the pedal as well.

## Building the hardware interface

### Components/Shopping List

1. [USB to RS485 TTL Serial Converter](https://user-images.githubusercontent.com/34777492/34389576-af109118-eb3a-11e7-8934-84c580e42ed4.jpg): There are plenty of those modules available, e.g. at ebay.com. I tested modules with the following description: USB to RS485 TTL Serial Converter Adapter FTDI interface FT232RL 75176 Module.
2. [DC 5V to DC 9V Step up Converter](https://user-images.githubusercontent.com/34777492/34389577-b03c207a-eb3a-11e7-9d03-2a6f2239754e.jpg): Again, there are many modules available online. I just picked one randomly and made good experiences with it.
3. [USB A to B printer/scanner cable](https://user-images.githubusercontent.com/34777492/34389579-b0fd28ec-eb3a-11e7-9c15-5f4ba5016eaa.jpg)
4. [RJ45 Ethernet Cable](https://user-images.githubusercontent.com/34777492/34389574-abcea9cc-eb3a-11e7-84da-a91b5ddbda16.jpg)

### Wiring diagram

Here's the wiring diagram following TIA/EIA 568b's Wiring Color Codes. If your Ethernet cable uses another color coding scheme you have to translate the given colors to TIA/EIA 568b. 

__Please note: First generation of Line6's foot controllers__ didn't work reliable for me using this wiring scheme. I don't have a proven answer why but I guess these controllers can't operate in "half-duplex" mode. My Shortboard (Mk1) runs properly if I don't connect the green/white wire to "A" and leave it unconnected instead.

Successfully tested with: 
- FBV Express Mk2
- Shortboard Mk2
- FBV3

```
                                     _________________________________
(8) brown        ------------------\|                                 |
(6) green        -------------------| P             SERIAL TO         |
                                    |                               -----
(7) brown/white  - - - - - - - - - -| A                 485             USB
(3) green/white  - - - - - - - - - /|                                   USB
                                    |               CONVERTER       -----
                                    | GND                             |
                                    |_________________________________|
                                     _________________________________
(2) orange       ------------------\|                                 |
(5) blue/white   - - - - - - - - - -| 9V             STEP-UP        -----  
                                    |                                   USB
                                    |                                   USB
(1) orange/white - - - - - - - - - -| GND            MODULE         -----    
(4) blue         ------------------/|_________________________________|    
                                    
```

 ### Bringing it all together
- Cut one end of the Ethernet cable, strip the isolation from each wire
- Cut the DC plug from the step-up module and strip the isolation
- Connect the unisolated wires from the Ethernet cable according to the wiring diagram to the serial to RS485 converter as well as the step up module. It is s also possible to use a wall power supply instead of the step up module. Just make sure you're using proper polarity. Every voltage between +7,5V and +9V should be fine.
- Connect the serial to RS485 module to the computer using the USB A to B printer/scanner cable
- Connect the setp up module to the computer. I was worried about damaging my computer by plugging the step-up module into one of the USB ports. However, there have been no problems. If you still worry, you can also plug the step up converter into an external USB power supply, e.g. one that is used for charging mobile devices.
- If you have a voltage measurement device at hand, make sure the 9V operating power (orange-orange/white and blue/white-blue) have proper polarity. The FBV needs 9V, not -9V!
- Finally, connect the Ethernet cable to the FBV. It should start-up by just showing a message in the display. If there is no reaction for more than 2secs remove the Ethernet cable IMMEDIATELY and check your wiring.

## Get the software
Tested on 
- Raspberry Pi 3
- Raspberry Pi Zero 
- various macOS installations.

### Installation instructions
```
git clone --recursive https://github.com/kempline/open_fbv.git
cd open_fbv
pip install pyserial
```
### First run of fbv_tester.py
The python program fbv_tester expects only one parameter: the serial port for the serial to RS485 converter module. On Unix platforms, the interface gets mounted in the operating system's /dev/ derictory. Just connect both USBs to your computer and run the following command in a terminal:
```
ls -l /dev/tty.usb*
```
You should see an output comparable to:
```
mac135:~ sbg$ ls -l /dev/tty.usb*
crw-rw-rw-  1 root  wheel   17,   0 Dec 30 12:59 /dev/tty.usbserial-A93XMWXN
mac135:~ sbg$ 
```
As far as I can tell, each converter has it's own identifier, here A93XMWXN. However, simply copy the full path (/dev/tty.usbserial-A93XMWXN) and start open_fbv_tester.py with it, e.g.:
```
python open_fbv_tester.py /dev/tty.usbserial-A93XMWXN
```
If you're using a pedal with a 16ch display you should see the following message:
```
 123 open fbv rocks!
```
This basically means that the communication between your computer and the FBV works properly. Next, you might want to move the pedal up and down. You should see something like this in the terminal window:
```
2017-12-30 13:06:36 - INFO - pedal: 0 moved: 126
2017-12-30 13:06:36 - INFO - pedal: 0 moved: 121
2017-12-30 13:06:36 - INFO - pedal: 0 moved: 112
2017-12-30 13:06:37 - INFO - pedal: 0 moved: 103
2017-12-30 13:06:37 - INFO - pedal: 0 moved: 94
2017-12-30 13:06:37 - INFO - pedal: 0 moved: 90
2017-12-30 13:06:37 - INFO - pedal: 0 moved: 89
2017-12-30 13:06:37 - INFO - pedal: 0 moved: 91
2017-12-30 13:06:37 - INFO - pedal: 0 moved: 92
```
If you get this output, the communication from the board to your computer works as well. Congratulations :-)

Next, try the basic features 
- switch clicked
```
2017-12-30 13:06:38 - INFO - switch: 97, value: 1
2017-12-30 13:06:38 - INFO - switch: 97, value: 0
```
- switch double clicked
```
2017-12-30 13:06:40 - INFO - switch double clicked: 97
```
- switch hold
```
2017-12-30 13:13:11 - INFO - switch: 48, value: 1
2017-12-30 13:13:14 - INFO - switch hold: 48
```

## What's next?

