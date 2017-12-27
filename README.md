# open_fbv

## Introduction
Line6's hardware uses the a so-called asynchronous serial communication over RS-485 to exchange messages between their multi-effect/amp-devices and the pedals like the Shortboard, Shortboard MkII, FBV3, Longboard or the Fbv Express. Unfortunately, sending serial data over RS-485 is not possible using a standard computer. Therefore, an interface for converting the PC's TTL data to the electrical characteristics of the RS-485 standard is necessary. Luckily, RS-485 is a widely used standard and there are plenty of converter modules available. 

Besides RS-485 communication, each pedal needs a suply voltage of 7,5V. In Line6's ecosystem, the multi-effect/amp-device powers the connected board by providing the desired voltage over the Ethernet cable. Since we are going to replace Line6's multi-effect/amp-device in this project, we need to provide the power supply for the pedal as well.

## Building the hardware interface

### Components/Shopping List

1. USB to RS485 TTL Serial Converter: There are plenty of those modules available, e.g. ebay.com. I tested modules with the following description: USB to RS485 TTL Serial Converter Adapter FTDI interface FT232RL 75176 Module.
2. DC 5V to DC 9V Step up Converter: Again, there are many different variants of such modules available online. I just picked one randomly and made good experiences with the step up converter.
3. USB A to B printer/scanner cable
4. RJ45 Ethernet Cable

### Wiring diagram

Here's the wiring diagram following TIA/EIA 568b's Wiring Color Codes. If your Ethernet cable uses another color coding scheme you have to translate the given colors to TIA/EIA 568b. I successfully tested the wiring using the following foot controllers: 
- FBV Express Mk2
- Shortboard Mk2
- FBV3

__Please note: First generation of Line6's foot controllers__ didn't work reliable for me using the following wiring scheme. I don't have a proven answer why this happens but I believe these controllers are not able to communicate in "half-duplex" mode. I was able to get my Shortboard (Mk1) to run properly if I simply don't connect the green/white wire to "A" and left it unconnected instead. 

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
- Connect the setp up module to the computer. I was a little bit afraid that I might damage my computer by plugging the step-up module into one of the USB ports. For me it worked very well using the following hardware: Raspberry Pi 3, Rasperry Pi Zero with a USB hub, Mac mini 2011, iMac 2009. If you are still afraid of damaging your hardware, you can also plug the step up converter into an external USB power supply, e.g. one that is used for charging mobile devices.
- If you have a voltage measurement devive at hand, make sure the 9V operating power (orange-orange/white and blue/white-blue) have proper polarity. The FBV needs 9V, not -9V!
- Finally, connect the Ethernet cable to the FBV. It should start-up by just showing a message in the display. If there is no reaction for more than 2secs remove the Ethernet cable IMMEDIATELY and check your wiring.


