#!/usr/bin/env python 

import os

if os.name == 'nt':
    OS_TYPE = 'windows'
    import pywinusb.hid as pyhid 
else:
    print("Could not recognize system or system is not supported.")
    exit

class USBdevice():
    def readData(self, data):
        """
        
        Read the data.

        Parameters
        ----------
        data : TYPE: list
            DESCRIPTION: list containing the data for the instructions
            in write mode.

        Returns
        -------
        None.

        """
        
        if self.debug:
            print("Raw data answer: {0}".format(data))
        self.answer = data

    def __init__(self,vid=0x0451,pid=0xc900):
        self.V_id=vid
        self.P_id=pid
        self.os = OS_TYPE
        filter = pyhid.HidDeviceFilter(vendor_id = self.V_id, product_id = self.P_id)
        devices = filter.get_devices()

        self.answer = [0x00]*65
        self.debug = False

        if devices:
            device = devices[0]
            print("Found the right USB device.")
            self.dev = device
            self.dev.open()
            self.dev.set_raw_data_handler(self.readData)
        else:
            print("Did not finde right USB device.")
            raise Exception()

    def send_command(self,command):
        """
        
        Send a command to the DMD. If debug, prints the command.

        Parameters
        ----------
        command : TYPE: list
            DESCRIPTION. list containing the bytes of the command.

        Returns
        -------
        None.

        """
        
        assert 65 == len(command)
        self.answer = [0x00]*65

        if self.debug:
            print("Final command: " + str(command))
        
        if self.os == 'windows':
            reports = self.dev.find_output_reports()
            reports[0].send(command)

    def create_dmd_command(self,mode,reply,sequencebyte,usb_code,data=[]):
        """
        
        Constructs the desired command according to the programmer's guide
        convention. 

        Parameters
        ----------
        mode : TYPE: string
            DESCRIPTION: Set the mode operation of the DMD. Mode is 'r' for a 
            read operation, 'w' for a write operation.
            
        reply : TYPE: Bool
            DESCRIPTION: True if the host wants a reply from the device, False
            otherwise.
            
        sequencebyte : TYPE: hex int
            DESCRIPTION: Byte of the sequence.
            
        usb_code : TYPE: hex int
            DESCRIPTION: USB code of the desired command. For example, if the
            host wants to flip the image displayed along the short axis, the 
            usb_code will take the value 0x1009
            
        data : TYPE, optional: list
            DESCRIPTION. The default is [].  data appropriate to the commande if
            in write operation. If in read operation, the DLPC900 responds to 
            the Read operation by placing the response data in its internal buffer

        Returns
        -------
        None.

        """
        
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
        # in case of data to long for one transfer(>=255):
        if payload_length > 254:
            payload2_length = (payload_length)/255
            payload_length -= payload2_length
        else:
            payload2_length = 0 
        buffer[i+2] = payload_length
        buffer[i+3] = payload2_length

        #LSB and MSB 
        lsb, msb = self.convert_bytes(usb_code)
        buffer[i+4] = msb
        buffer[i+5] = lsb

        # move data in payload 
        for item in range(len(data)):
            buffer[i+6+item] = data[item]
        
        if OS_TYPE == 'windows':
            self.send_command(buffer)
        else:
            print("Unrecognized OS, no command sent.")

    def raw_command(self,buffer):
        assert 64 == len(buffer)

        if OS_TYPE == 'windows':
            buffer = [0x00] + buffer
            reports = self.dev.find_output_reports()
            reports[0].send(buffer)
        else:
            print("No command send")

    def releaseUSB(self):
        """
        
        Releases the device.

        Returns
        -------
        None.


        """
        self.dev.close()

    def convert_bytes(self, integer):
        return divmod(integer, 0x100)

if __name__ == '__main__':
    test_dev = USBdevice()
    print("Test result: %s" %(test_dev))

    