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

Here's the wiring diagram following TIA/EIA 568b's Wiring Color Codes. If your Ethernet cable uses another color coding scheme you have to translate the given colors to TIA/EIA 568b.

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
- Cut one end of the Ethernet cable
