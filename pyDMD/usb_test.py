# usb communictaion for linux
"""
import usb.core
import usb.util

V_id=0x0451 
P_id=0xc900

dev = usb.core.find(idVendor=V_id ,idProduct=P_id)
if not dev:
    print("Could not finde correct USB device.")
    exit
else:
    print("Found the right USB device.")
    exit
"""

import os
from msvcrt import kbhit
from time import sleep

if os.name == 'nt':
    OS_TYPE = 'windows'
    import pywinusb.hid as pyhid 
else:
    print("Could not recognize system or system is not supported.")
    exit

V_id=0x0451 
P_id=0xc900

filter = pyhid.HidDeviceFilter(vendor_id = V_id, product_id = P_id)
devices = filter.get_devices()

if devices:
    device = devices[0]
    print("Found the right USB device.")
dev = device
dev.open()

def readData(data): #Print answer from DMD
    print("Raw data: {0}".format(data))
    #return None
dev.set_raw_data_handler(readData)

def send_command(command):
    #sends the final command to dmd
    assert 65 == len(command)
    #print(command)

    if OS_TYPE == 'windows':
        reports = dev.find_output_reports()
        #print(reports[0])
        reports[0].send(command)

def dmd_create_command(mode, reply, sequencebyte, com1, com2, data=[]):
    # builds the desired command
    if OS_TYPE == 'windows':
        buffer = [0x00]*65
        i = 1
    else:
        print("Unrecognized OS, no command sent.")
    
    flagstring =''  # creates flag byte in a string 

    if mode == 'r': # r for read, w for write
        flagstring+='1'
    else:
        flagstring+='0'
    if reply:
        flagstring+='1'
    else:
        flagstring+='0'
    flagstring+='000000'
    buffer[i] = int(flagstring,2)
    buffer[i+1] = sequencebyte # code to connect command and answer from dmd
    
    payload_length = 2+ len(data)
    # in case of data to long for one transfer:
    if payload_length > 254:
        payload2_length = (payload_length)/255
        payload_length -= payload2_length
    else:
        payload2_length = 0 
    buffer[i+2] = payload_length
    buffer[i+3] = payload2_length

    # LSB and MSB 
    buffer[i+4] = com2
    buffer[i+5] = com1 

    # move data in payload 
    for item in range(len(data)):
        buffer[i+6+item] = data[item]
    
    if OS_TYPE == 'windows':
        send_command(buffer)
        print("Command:") 
        print(buffer)
        print("End of command.")
    else:
        print("Unrecognized OS, no command sent.")
    
def set_pattern_on_the_fly_mode():
    # Set the DMD into pattern on the fly mode
    dmd_create_command('w',True,0x22,0x1a,0x1b,data=[0x03])
    print("Setting DMD in pattern-on-the-fly mode.")

def control(cmd):
    #starts, stops and pauses the dmd 
    if cmd == 'start':
        data = [0x02]
    elif cmd == 'stop':
        data = [0x00]
    elif cmd == 'pause':
        data = [0x01]    
    dmd_create_command('w',True,0x22,0x1a,0x24, data)

if __name__ == '__main__':
    while dev.is_plugged() and not kbhit():
        set_pattern_on_the_fly_mode()
        sleep(1)

    #control('stop')
    print("Test started.")
    

