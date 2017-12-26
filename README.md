# open_fbv

## Building the hardware interface
### Introduction
Line6's hardware uses the a so-called asynchronous serial communication over RS-485 to exchange messages between their multi-effect/amp-devices and the pedals like the Shortboard, Shortboard MkII, FBV3, Longboard or the Fbv Express. Unfortunately, sending serial data over RS-485 is not possible using a standard computer. Therefore, an interface for converting the PC's TTL data to the electrical characteristics of the RS-485 standard is necessary. Luckily, RS-485 is a widely used standard and there are plenty of converter modules available. 

Besides RS-485 communication, each pedal needs a suply voltage of 7,5V. In Line6's ecosystem, the multi-effect/amp-device powers the connected board by providing the desired voltage over the Ethernet cable. Since we are going to replace Line6's multi-effect/amp-device in this project, we need to provide the power supply for the pedal as well.

### Components

1. [USB to RS485 TTL Serial Converter (left) + DC 5V to DC 9V Step up Converter (right)](https://user-images.githubusercontent.com/34777492/34322801-440f99c8-e832-11e7-92da-da0167ba90af.jpg)
The step up module is just one option to . You can also use a wall power supply delivering 9v DC.

2. [USB cable](https://user-images.githubusercontent.com/34777492/34322802-4428a06c-e832-11e7-8e62-c2bfff472aa1.jpg)

3. [Standard Ethernet Cable](https://user-images.githubusercontent.com/34777492/34322803-44413c94-e832-11e7-9c87-09f73d2281ce.jpg)

Make sure your Ethernet cable utilises the standard colour coding, otherwise the wiring diagrams used here won’t fit

[colour coding](https://user-images.githubusercontent.com/34777492/34322804-445bd252-e832-11e7-99a5-1be2f7590715.jpg)

Cut one end of the Ethernet cable, strip the isolation from each wire. 
Also cut the DC plug from the step-up module and strip the isolation

### Wiring diagram

Here's the wiring diagram following TIA/EIA 568b's Wiring Color Codes. If your Ethernet cable uses another color coding scheme you have to translate the given colors to TIA/EIA 568b.

                                    -----------------------------------
(8) brown        ------------------\|                                 |
(6) green        -------------------| P             SERIAL TO         |
                                    |                               ----- 
(7) brown/white  - - - - - - - - - -| A                 485             USB
(3) green/white  - - - - - - - - - /|                                   USB
                                    |               CONVERTER       -----    
                                    | GND                             |
                                    |                                 |
                                    -----------------------------------


                                    -----------------------------------
(2) orange       ------------------\|                                 |
(5) blue/white   - - - - - - - - - -| 9V             STEP-UP        -----  
                                    |                                   USB
                                    |                                   USB
(1) orange/white - - - - - - - - - -| GND            MODULE         -----    
(4) blue         ------------------/|                                 |    
                                    -----------------------------------


[Link Text](https://user-images.githubusercontent.com/34777492/34322805-44756d5c-e832-11e7-8b26-ca0587022e24.jpg)

[Link Text](https://user-images.githubusercontent.com/34777492/34322806-448eb19a-e832-11e7-8665-59733140c826.jpg)
