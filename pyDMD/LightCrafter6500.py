#!/usr/bin/env python

import numpy as np 
import math
import matplotlib.pyplot as plt
from pyDMD.USBdevice import USBdevice
from time import sleep
from pyDMD.DMDPattern import DMDPattern


class LightCrafter6500():
    def __init__(self, device=None):
        if device != None:
            self.USB_dev = device
        else:
            self.USB_dev = USBdevice()
         
        self.vid = self.USB_dev.V_id
        self.pid = self.USB_dev.P_id
        self.os = self.USB_dev.os
        self.set_pattern_on_the_fly_mode()
        self.mode = 'pattern_on_the_fly'

    def pattern_display_start_stop(self,start_stop):
        """
        
        Start, stop or pause the programmed pattern sequence. The DMD has to
        be in pattern_on_the_fly mode.

        Parameters
        ----------
        start_stop : TYPE: string
            DESCRIPTION: start_stop can only take the values 'start', 'stop' or
            'pause'. 
                -If 'stop': Stop Pattern Display Sequence. The next Start command 
            restarts the pattern sequence from the beginning.
                -If 'pause': Pause Pattern Display Sequence. The next Start
            command starts the pattern sequence by re-displaying the current
            pattern in the sequence.
                -If 'start': Start Pattern Display Sequence

        Raises
        ------
        Exception
            DESCRIPTION: If start_stop isn't one of the values, raises error.

        Returns
        -------
        None.

        """
        
        self.display_mode_get()
        if self.mode != 'pattern_on_the_fly':
            print("Cant do '%s' in current mode." %start_stop)
        else:
            command_list = {'start': 0x02,'stop':0x00,'pause':0x01}
            if not start_stop in command_list.keys():
                raise Exception('Allowed arguments are start, stop and pause')
            self.USB_dev.create_dmd_command('w',True,0x12,0x1a24, data=[command_list[start_stop]])
            print("Errors while %sing  the programmed sequence:" %start_stop)
            self.read_error_code(0x12)
            print("Programmed pattern sequence %s"%start_stop) 
    
    def display_mode_selection(self,mode):
        """
        Selects in which mode the DMD should operate

        Parameters
        ----------
        mode : TYPE: string
            DESCRIPTION: can be "video", "pre-stored_pattern", "video_pattern"
            or "pattern_on_the_fly".
                    -If 'video' : Video mode
                    -If 'pre-stored_pattern': Pre-stored pattern mode 
                (Images from flash)
                    -If 'video_pattern': Video pattern mode
                    -If 'pattern_on_the_fly':Pattern On-The-Fly mode 
                (Images loaded through USB/I2C)

        Returns
        -------
        None.

        """
        
        mode_list = {'video':0x00,'pre-stored_pattern':0x01,'video_pattern':0x02,'pattern_on_the_fly':0x03}
        assert mode in mode_list.keys()
        self.USB_dev.create_dmd_command('w',True,0x13,0x1a1b,data=[mode_list[mode]])
        print('Errors in the selection of the displayed mode:')
        self.read_error_code(0x13)
        print('DMD set in %s mode' %mode)
    
    def set_pattern_on_the_fly_mode(self):
        """
        Set the DMD to pattern-on-the-fly mode

        Returns
        -------
        None.

        """
        self.display_mode_selection('pattern_on_the_fly')

    def set_pre_stored_pattern_mode(self):
        """
        Set the DMD to pre-stored pattern mode

        Returns
        -------
        None.

        """
        self.display_mode_selection('pre-stored_pattern')

    def set_video_mode(self):
        """
        Set the DMD to video mode

        Returns
        -------
        None.

        """
        self.display_mode_selection('video')

    def display_mode_get(self):
        data = [0x00]
        self.USB_dev.create_dmd_command('r',True,0x14,0x1a1b, data)
        print("Error while geeting display mode:")
        error_code, answer = self.read_error_code(0x14)
        mode_list = ['video', 'pre-stored_pattern', 'video_pattern', 'pattern_on_the_fly']
        self.mode = mode_list[answer[5]]
        return self.mode

    def long_axis_image_flip(self,on_off):
        """
        

        Flip a displayed image along its long axis.

        Parameters
        ----------
        on_off : TYPE: Bool
            DESCRIPTION: True if one wants to flip the image, False 
            otherwise.

        Returns
        -------
        None.

        """
        
        if on_off:
            data = 0x80
        elif not on_off:
            data = 0x00
        else:
            raise Exception('on_off has to be True or False')
        self.USB_dev.create_dmd_command('w',True,0x22,0x1008,[data])
        print("Errors while setting long axis flip to %s:"%on_off)
        self.read_error_code(0x22)
        print("Long axis flip %s"%on_off)
        

    def short_axis_image_flip(self,on_off):
        """
        
        Up-down image flip.

        Parameters
        ----------
        on_off : TYPE: Bool
            DESCRIPTION: True if one wants to flip the image, False 
            otherwise.

        Returns
        -------
        None.

        """
        
        if on_off:
            data1 = 0x80
        elif not on_off:
            data1 = 0x00
        else:
            raise Exception('on_off has to be True or False')
        self.USB_dev.create_dmd_command('w',True,0x23,0x1009,data=[data1])
        print("Errors while setting short axis flip to %s:"%on_off)
        self.read_error_code(0x23)
        print("Short axis flip %s"%on_off)
        
    def park_unpark(self, mode):
        
        mode_dict = {'park' : 0x01, 'unpark' : 0x00}
        assert mode in mode_dict.keys()
        self.USB_dev.create_dmd_command('w', True, 0x37, 0x069, [mode_dict[mode]])
        print('Errors while '%mode)
        self.read_error_code(0x37)
        print("DMD  %s" %mode)
        
    def power_mode(self,mode):
        
        mode_dict = {'normal' : 0x00, 'standby' : 0x01, 'reset': 0x02}
        assert mode in mode_dict.keys()
        self.USB_dev.create_dmd_command('w', True, 0x72, 0x0200, [mode_dict[mode]])
        print('Errors while %s'%mode)
        self.read_error_code(0x72)
        print("DMD  %s" %mode)
        
    
    def dmd_idle_mode(self, mode):
        """
        
        Set the DMD in idle mode. This mode enables a 50/50 duty 
        cycle pattern sequence, where the entire mirror array is continuously
        flipped periodically between the on and off states.

        Parameters
        ----------
        mode : TYPE: Bool
            DESCRIPTION: True if the host wants to enable the idle mode, 
            False otherwise.

        Returns
        -------
        None.

        """
        
        mode_dict = {'start' : 0x01, 'stop' : 0x00}
        assert mode in mode_dict.keys()
        self.USB_dev.create_dmd_command('w', True, 0x42, 0x0201, [mode_dict[mode]])
        print('Errors while turning dmd idle mode  to %s'%mode)
        self.read_error_code(0x42)
        print("DMD idle mode %s" %mode)
        
        if mode=='start' or mode=='stop':
            self.pattern_display_start_stop(mode)




    def internal_test_pattern_select(self,image):
        """
        Select the test pattern displayed on the screen. These 
        test patterns are internally generated.

        Parameters
        ----------
        image : TYPE: string
            DESCRIPTION: Can be 'solid_field', 'horizontal_ramp', 'vertical_ramp', 
            'horizontal_lines', 'diagonal_lines', 'vertical_lines', 'grid', 
            'checkboard', 'RGB_ramp', 'color_bars', 'no_pattern'

        Returns
        -------
        None.


        """
        image_dict={'solid_field':0x00,'horizontal_ramp':0x01,'vertical_ramp':0x02,'horizontal_lines':0x03,'diagonal_lines':0x04,
                    'vertical_lines':0x05,'grid':0x06,'checkboard':0x07,'RGB_ramp':0x08,'color_bars':0x09,'no_pattern':0x0A}
        assert image in image_dict.keys()

        self.USB_dev.create_dmd_command('w',True,0x20,0x1203,data=[image_dict[image]])
        print('Errors while selecting the internal test pattern:')
        self.read_error_code(0x20)
        print("Display test pattern: %s" %image)

    def input_source_configuration(self,mode,bit_depth):
        """
        
        The Input Source Configuration command selects the input source to be
        displayed by the DLPC900: 30-bit parallel port, Internal Test Pattern 
        or flash memory. 

        Parameters
        ----------
        mode : TYPE: string
            DESCRIPTION: Select the input source and interface mode. Can be
            'primary_interface', 'internal_test_pattern', 'flash_image', 
            'solid_curtain'.
                -If 'primary_interface': Primary parallel interface with 16-bit, 
                20-bit, 24-bit, or 30-bit RGB or YUV data formats.
                -If 'internal_test_pattern': Internal test pattern generator.
                -If 'flash_image': Flash. Images are 24-bit single-frame, 
                still images stored in flash that are uploaded on command.
                -If 'solid_curtain': Solid curtain
            
        bit_depth : TYPE: string
            DESCRIPTION: Parallel interface bit depth.
            Can be '30_bits', '24_bits', '20_bits', '16_bits'.

        Returns
        -------
        None.

        """

        data = [0x00]

        mode_dict={'primary_interface':'000','internal_test_pattern':'001','flash_image':'010','solid_curtain':'011'}
        assert mode in mode_dict.keys()
        bit_depth_dict={'30_bits':'00','24_bits':'01','20_bits':'10','16_bits':'11'}
        assert bit_depth in bit_depth_dict.keys()
        self.mode = 'video'

        data_string = '000' + bit_depth_dict[bit_depth] + mode_dict[mode]
        data[0] = int(data_string,2)
        self.USB_dev.create_dmd_command('w',True,0x21,0x1a00,data=data)
        print('Errors while selecting the input source to be displayed:')
        self.read_error_code(0x21)
        print("Input source is now %s" %mode)

    def trigger_in_1(self, trigger_delay, is_trigger_rising_edge = True):
        """

        The Trigger In 1 command sets the rising edge delay of the TRIG_IN1
        signal compared to when the pattern is displayed on the DMD. Before
        executing this command, stop the current pattern sequence.

        Parameters
        ----------
        trigger_delay : TYPE: int
            DESCRIPTION. Delay in microseconds.
            Sets the TRIG_IN_1 delay. Min 105 microseconds
            
        is_trigger_rising_edge : TYPE, optional: Bool
            DESCRIPTION. The default is True. True if one wans the rising edge
            delay, False otherwise.

        Raises
        ------
        Exception
            DESCRIPTION: If trigger_delay < 105 µs, raises error.

        Returns
        -------
        None.

        """

        if trigger_delay < 105:
            raise Exception("Minimum 105 µs trigger_delay")
        else:
            print("configuring trigger")
            trigger_delay_bytes = self.int_to_hex_array(trigger_delay, 2)
            rising_edge_bit = [0x00] if is_trigger_rising_edge else [0x01]
            data = trigger_delay_bytes + rising_edge_bit
            self.USB_dev.create_dmd_command('w', True, 0x43, 0x1a35, data)
            print('Errors while setting the rising edge delay of the TRIG_IN1 signal:')
            self.read_error_code(0x43)
        #assert trigger_delay > 104

    def pattern_display_LUT_definition(self, pattern_index, wait_for_trigger, 
                                       exposure_time = 105, dark_time = 105, 
                                       bit_depth = 1, flicker_active = True):
        """
        The Pattern Display LUT Definition contains the definition of each pattern 
        to be displayed during the pattern sequence. Display Mode must be set
        before sending any pattern LUT definition data. LEDs are always disabled

        Parameters
        ----------
        pattern_index : TYPE: int
            DESCRIPTION: Index of the pattern in the sequence. Must be between
            0 and 255.
            
        wait_for_trigger : TYPE: bool
            DESCRIPTION: True if one wants to wait for trigger before displaying
            the pattern, False otherwise
            
        exposure_time : TYPE: int
            DESCRIPTION: Pattern exposure in microseconds, has to be > 105
            
        dark_time : TYPE: int  
            DESCRIPTION: Dark display time following the exposure (in µs)
            
        bit_depth : TYPE: int
            DESCRIPTION: Select desired bit-depth 
            
        flicker_active : TYPE, optional: bool
            DESCRIPTION. The default is True. True if one wants to activate 
            flickering, False otherwise.

        
        Raises
        ------
        Exception
            DESCRIPTION: Checks if dark_time and exposure_time are > 105, and
            if bit_depth is between 1 and 8.

        Returns
        -------
        None.


        """
        if pattern_index > 256 and pattern_index < 0:
            raise Exception("Wrong pattern_index") 
        # assert pattern_index < 256 and pattern_index >= 0 
        else:
            led_on_off = 0 #0 for off, 1 for on (as int)
            trigger = 1 #0 for off, 1 for on (as string)

            pattern_index_bytes = self.int_to_hex_array(pattern_index, 2)
            exposure_bytes = self.int_to_hex_array(exposure_time, 3)

            #trigger_settings_bytes = [0xf1] if wait_for_trigger else [0x01]
            bit_depth_list = ['000','001','010','011','100','101','110','111']
            led_list = ['000','111']
            trigger_list = ['0','1']
            if not wait_for_trigger:
                trigger = 0
            if not flicker_active:  #switch between flickering(1) and non flickering(0)
                flicker_bit = '0'
            else:
                flicker_bit = '1'
            string_for_trigger = trigger_list[trigger] + led_list[led_on_off] + bit_depth_list[bit_depth-1] + flicker_bit
            print(string_for_trigger)

            trigger_settings_bytes = [0x01]
            trigger_settings_bytes[0] = int(string_for_trigger,2)

            dark_time_bytes = self.int_to_hex_array(dark_time, 3)
            trig2_output_bytes = [0x00]
            
            data = pattern_index_bytes + exposure_bytes + trigger_settings_bytes + \
                dark_time_bytes + trig2_output_bytes + pattern_index_bytes
            self.USB_dev.create_dmd_command('w', True, 0x65, 0x1a34, data)
            print('Errors while creating the LUT:')
            #self.read_error_code(0x65)
            #somehow this command caused problems for shor exposure times. Dont understand why

    def initialize_pattern_BMP_load(self, length, index = 0):
        """
        
        When the Initialize Pattern BMP Load command is issued, the patterns in 
        the flash are not used until the pattern mode is disabled by command. 
        Follow this command by the Pattern BMP Load command to load the images.
        Load the images in the reverse order. Suppose there are 3 images 0,1 
        and 2 then the order for loading the image is 2, 1 and 0.

        Parameters
        ----------
        length : TYPE: int
            DESCRIPTION. Size of compressed image
        index : TYPE, optional: int
            DESCRIPTION. The default is 0. Count images. Image index goes from
            0 to 17, in 24 bit format. 

        Returns
        -------
        None.

        """
        
        data = self.int_to_hex_array(index, n_bytes=2)
        data+= self.int_to_hex_array(length,n_bytes=4)
        self.USB_dev.create_dmd_command('w',True,0x11,0x1a2a, data=data)
        print('Errors while loading BMP pattern:')
        self.read_error_code(0x11)

    def pattern_display_LUT_configuration(self, number_of_patterns, number_of_repeats):
        """
        
        Controls the execution of patterns stored in the lookup table (LUT). 
        Before executing this command, stops the current pattern sequence.

        Parameters
        ----------
        number_of_patterns : TYPE: int
            DESCRIPTION. Number of patterns in the sequence. Should not exceed 
            255.
            
        number_of_repeats : TYPE: int
            DESCRIPTION. Number of type times to repeat the pattern sequence.

        Raises
        ------
        Exception
            DESCRIPTION. Checks if number_of_patterns <= 256

        Returns
        -------
        None.

        """
        
        if number_of_patterns > 255:
            raise Exception("Too many patterns.")
        else:
            print("Configuring LUT with %s images." %number_of_patterns)
            patterns_bytes = self.int_to_hex_array(number_of_patterns, n_bytes=2)
            repeats_bytes = self.int_to_hex_array(number_of_repeats, n_bytes=4)
            data = patterns_bytes + repeats_bytes
            self.USB_dev.create_dmd_command('w', True, 0x0d, 0x1a31, data)
            print('Errors while controling the execution of patterns stored in the lookup table:')
            self.read_error_code(0x0d)

    def send_image(self,image_bits):
        """
        
        Parameters
        ----------
        image_bits : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        max_cmd_payload = 504
        im_size = np.size(image_bits)

        num_full_cmd_groups = im_size/max_cmd_payload
        num_full_cmd_groups = math.ceil(num_full_cmd_groups)
        remainder_group_length = im_size % max_cmd_payload
        print("Full_cmd_groups: " + str(num_full_cmd_groups))

        # Send full command groups
        if num_full_cmd_groups > 1:
            for cmd_group_index in range(num_full_cmd_groups):  
                if cmd_group_index % 50 == 0:
                    print("sending packet group %s" % cmd_group_index)
                self.send_image_command(image_bits[0+cmd_group_index*max_cmd_payload:max_cmd_payload+cmd_group_index*max_cmd_payload],
                                                    cmd_group_index)
        # Send remainder
        self.send_image_command(image_bits[num_full_cmd_groups*max_cmd_payload:num_full_cmd_groups*max_cmd_payload+remainder_group_length],
                                            0xab)

    def send_image_command(self,image_bits,sequence_byte):
        """
        :param image_bits is a numpy uint array of the current payload
        :param sequence_byte is there for bookkeeping, gets placed as sequence byte of first command
        """
        payload_length = np.size(image_bits) 
        assert payload_length <= 504

        command  = [0x00]*8
        command[1] = np.uint8(sequence_byte % 256)
        data_length_with_data_header = self.int_to_hex_array(2+2+payload_length)
        # 2 for the command bytes, 2 for the length bytes in the payload, then payload
        data_length = self.int_to_hex_array(np.size(image_bits))
        
        # compute number of slaves
        if payload_length <= 56:
            print("preparing last packet of image")
            n_slaves = 0
            pad_width = 56 - payload_length
            image_bits_padded = np.pad(image_bits, (0, pad_width), 'constant', constant_values=(0,0))

        else:
            n_slaves = (payload_length - 56) / 64
            if (payload_length - 56) % 64 != 0:
                n_slaves += 1
            pad_width = (64 - (payload_length - 56) % 64)% 64
            image_bits_padded = np.pad(image_bits, (0, pad_width), 'constant', constant_values=(0,0))

        for i in range(2):
            command[2+i] = data_length_with_data_header[i]
        command[4] = 0x2B
        command[5] = 0x1A
        for j in range(2):
            command[6+j] = data_length[j]
        
        if n_slaves == 0:
            command += image_bits_padded.tolist()
            self.USB_dev.raw_command(command)
        else:
            command += image_bits_padded[0:56].tolist()
            self.USB_dev.raw_command(command)
            
            slave_bits = image_bits_padded[56:]
            n_slaves = int(n_slaves)
            for k in range(n_slaves):
                #if OS_TYPE == 'windows':
                #    print("slave rng %s, %s"%(64*k, 64*(k+1)))
                #    print("length %s"%len(slave_bits[64*k:64*k+64].tolist()))
                self.USB_dev.raw_command(slave_bits[64*k:64*k+64].tolist())


    """BASIC COMMANDS"""

    def read_error_code(self,sequence_byte, return_data = False):
        """
        
        Check if there is any error when executing a command.

        Parameters
        ----------
        sequence_byte : TYPE: hex int
            DESCRIPTION: Identity of a command, to check if there are any errors
        return_data : TYPE, optional
            DESCRIPTION. The default is False. True if one wants to return data.

        Raises
        ------
        DmdError
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.
        data : TYPE
            DESCRIPTION.

        """
        
        #print('Checking errors')
        timeout = 0
        error_bit = 0
        while True:
            if self.USB_dev.answer[2] == sequence_byte: #check sequencebyte to identify correct answer
                flagstring = format(self.USB_dev.answer[1], '08b') #converts the second byte into an 8 character string, third is the error bit
                if self.USB_dev.answer[1] > 255:
                    print("Answer by device can not be interpreted!")
                    break
                else:
                    error_bit = int(flagstring[2])
                    data = self.USB_dev.answer
                    break
            else:
                sleep(0.01)
                if timeout >= 100:
                    print("Timeout: Could not finde right device answer!")
                    break
                else:
                    timeout +=1 

        if error_bit == 1:
            self.USB_dev.create_dmd_command('r',True,0xAB,0x0100)
            timeout_error = 0
            error_code = 0
            while True:
                if timeout_error >= 100:
                    print('Timeout: Could not reveive eroor code!')
                    break
                else:
                    if self.USB_dev.answer[2] == 171: #check sequencebyte to identify correct answer
                        error_code = self.USB_dev.answer[5] #sixth byte transports error code
                    else:
                        sleep(0.01)
                        timeout_error += 1
    
            if error_code != 0:
                raise DmdError(error_code)
            return error_code, data
        else:
            print("No errors")
            return 0, data

    def int_to_hex_array(self, number, n_bytes = 2):
        """
        :param positive integer
        :return the integer, as a n_bytes long array of uint8's, starting from lsb
        """
        hex_array = []
        for n in range(n_bytes):
            hex_array.append((number >> n*8) & 0xff)
        return hex_array

    def raw_write_command(self,usb_index,data=[],sequence_byte=0x01):
        self.USB_dev.create_dmd_command('w',True,sequence_byte,usb_code=usb_index,data=data)
        print("Error raw write command:")
        self.read_error_code(sequence_byte)

    def raw_read_command(self,usb_code,data=[],sequence_byte=0x02):
        self.USB_dev.create_dmd_command('r',True,sequence_byte,usb_code=usb_code,data=data)
        print("Error raw read command:")
        self.read_error_code(sequence_byte)
        

    def releaseUSB(self):
        self.USB_dev.releaseUSB()

    def dec_to_bin(self, number):
        return (bin(number)[2:])
    


class DmdError(Exception):
    def __init__(self, value):
        self.error_code_dict = {0:"no error",
                           1:"batch file checksum error",
                           2:"device failure",
                           3:"invalid command number",
                           4:"incompatible controller/dmd",
                           5:"command not allowed in current mode",
                           6:"invalid command parameter",
                           7:"item referred by the parameter is not present",
                           8:"out of resource/RAM",
                           9:"invalid bmp compression type",
                           10:"pattern bit number out of range",
                           11:"pattern bmp not present in flash",
                           12:"pattern dark time out of range",
                           13:"signal delay parameter out of range",
                           14:"pattern exposure time is out of range",
                           15:"pattern number is out of range",
                           16:"invalid pattern definition",
                           17:"pattern image memory address is out of range",
                           255:"Internal error"}
        for i in range(18,255):
            self.error_code_dict[i] = "undefined error"

        self.value = value
    def __str__(self):
        return repr("%s: %s"%(self.value, self.error_code_dict[self.value]))





if __name__ == '__main__':
    test = LightCrafter6500()
    test.input_source_configuration('internal_test_pattern','24_bits')
    test.internal_test_pattern_select('checkboard')
    sleep(1)
    test.set_pattern_on_the_fly_mode()
    test.power_mode('reset')