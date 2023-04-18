# DMDControl
This repository contains an application for controlling the LightCrafter6500 DMD from Texas instruments.

# Acknowledgements
This project is based on the work of [A. Mazurenko](https://github.com/mazurenko/Lightcrafter6500DMDControl). Thank you for making the code public!
The following individuals contributed to the project:
- [L. Fischer] (https://github.com/LFischer20)
- L. Malgrey
- [ruben-e11] (https://github.com/ruben-e11) 

# Requirements
The required python packages are:
* pillow
* pywinusb

# Examples
Example scripts:
* example_software_flicker_disable.py: Show usage of the Pattern_on_the_fly class and flicker disable.

# pyDMD package
This package is a direkt fork from [A. Mazurenko](https://github.com/mazurenko/Lightcrafter6500DMDControl).

## USBdevice.py
Builds and hosts the USB connection with the DMD. 
Final command assambly, sending of raw commands for image upload, and handling of answers from the DMD.
## LightCrafter6500.py
Implements commands from the programmer's guid, e.g. mode selection, pattern display LUT configuration, the read error code command. 
We added here an option to disable the 105µs flickering of all mirrors.
This class does not have the USBdevice class as a parent but creates an instance USBdev in the __init__ function which is used for all usb connection handling. 
Contains also the DmdError class which displays all possible errors that can occure when operating the DMD. 
##  DMDPattern.py 
Responsible for mage reading, image header and image compression using run-length-encoding(RLE).
## Pattern_on_the_fly.py
User friendly implementation of the pattern on the fly mode.
The upload_image_sequnece function gets a dictionary of the from: 
pattern_dict = {'patterns': [pattern1, pattern2, pattern3], 'number_of_repeats': 20}
If 'number_of_repeats' is not specified the sequence repeates forever. 
The pattern_on_the_fly class also creates an instance of the LightCrafter6500 class in its __init__ function.


# TCP_IP
WIP for a tcp ip server for ExpWiz integration.