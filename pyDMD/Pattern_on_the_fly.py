#!/usr/bin/env python


import pyDMD.LightCrafter6500 as lc
import pyDMD.DMDPattern as dp
import numpy as np 
from time import sleep 
import glob
import cv2

class Pattern_on_the_fly():
    def __init__(self):
        self.lc_dmd = lc.LightCrafter6500()
    
    def upload_image_sequence(self, dmd_pattern_sequence, wait_for_trigger=False):
        """
        
        Send an image or a sequence of image to the device.

        Parameters
        ----------
        dmd_pattern_sequence : TYPE: dictionnary
            DESCRIPTION: dic with the following structure:
            {'patterns': [dmd_pattern], 'number_of_repeats': number_of_repeats}
                
        wait_for_trigger : TYPE, optional: Bool
            DESCRIPTION. The default is False. True if want to wait for trigger.

        Returns
        -------
        None.

        """
        
        self.lc_dmd.pattern_display_start_stop('stop')
        self.lc_dmd.set_pattern_on_the_fly_mode()

        for indx, dmd_pattern in enumerate(dmd_pattern_sequence['patterns']):
            self.lc_dmd.pattern_display_LUT_definition(indx, wait_for_trigger, dmd_pattern.exposure_time, dmd_pattern.dark_time, dmd_pattern.bit_depth, dmd_pattern.flicker_active)
        
        sequence_length = len(dmd_pattern_sequence['patterns'])
        number_of_repeats = dmd_pattern_sequence.pop('number_of_repeats', 0)
        for indx, dmd_pattern in reversed(list(enumerate(dmd_pattern_sequence['patterns']))): #load last image first
            image_bits = dmd_pattern.compress_pattern()
            self.lc_dmd.initialize_pattern_BMP_load(np.size(image_bits),index=indx)
            self.lc_dmd.send_image(image_bits)
            print('Sent pattern %s' %indx)
            self.lc_dmd.pattern_display_LUT_configuration(sequence_length, number_of_repeats)
            
        self.lc_dmd.trigger_in_1(105)
        self.lc_dmd.pattern_display_start_stop('start')
        print('All images uploaded!')

    def upload_one_image(self,  dmd_pattern_file, exposure_time, 
                         dark_time, number_of_repeats, short_axis_flip=False, 
                         long_axis_flip=False, bit_depth=1, wait_for_trigger=False):
        
        """
       
        Upload one image on the DMD during a given time. 

        Parameters
        ----------
        dmd_pattern_file : TYPE: string
            DESCRIPTION: Path of the pattern you want to upload
            
        number_of_repeats : TYPE: int
            DESCRIPTION: Number of times the image is projected
            
        exposure_time : TYPE: int
            DESCRIPTION: Exposure time of the pattern, time in microseconds > 104
            
        dark_time : TYPE: int
            DESCRIPTION: Dark time of the pattern, time in microseconds > 104
            
        bit_depth : TYPE: int
            DESCRIPTION: Bit depth of the pattern, 1 if black and white. 
            Max bit_depth = 8. Default : bit_depth=1
        
        short_axis_flip : TYPE: Bool
            DESCRIPTION: True if short axis flip, False otherwise. Default : False
            
        long_axis_flip : TYPE: Bool
            DESCRIPTION: True if long axis flip, False otherwise. Default: False
            
        wait_for_trigger : TYPE: Bool
            DESCRIPTION. The default is False. True if one wants to wait for a 
            trigger. Default: False
            
            
        Raises
        ------
        Exception
            DESCRIPTION.

        Returns
        -------
        None.

        """

        self.lc_dmd.set_pattern_on_the_fly_mode()       #POF mode
        self.lc_dmd.long_axis_image_flip(long_axis_flip)
        self.lc_dmd.short_axis_image_flip(short_axis_flip)    #Flip or not
        
        if type(dmd_pattern_file) is not str:
            raise Exception("dmd_pattern_file has to be a str")
        settings = {'compression':'rle', 'bit_depth': bit_depth}
        #dmd_pattern = dp.DMDPattern(**settings)
        dmd_pattern = dp.DMDPattern(**settings)
        dmd_pattern.load_png(dmd_pattern_file)
        dmd_pattern.exposure_time, dmd_pattern.dark_time = exposure_time, dark_time
        one_pattern = {'patterns': [dmd_pattern], 'number_of_repeats': number_of_repeats}
        self.upload_image_sequence(one_pattern)


    def play_pattern_sequence(self,dmd_pattern_file,exposure_time,dark_time, 
                              nb_repeat_sequence, bit_depth=1, compression_type='rle'):
        
        """
        
        Display a sequence of patterns on the DMD

        Parameters
        ----------
        dmd_pattern_file : TYPE: String
            DESCRIPTION: Path of the folder in which the sequence pattern is.
            Every image in the folder has to have the name 'sequence_number', 
            number going from 0 to number of sequences.
            
        exposure_time : TYPE: Int
            DESCRIPTION: exposure time (in microseconds) of every image of the
            sequence. Has to be >105
            
        dark_time : TYPE: Int
            DESCRIPTION: Dark time (in microseconds) of every image of the 
            sequence. Has to be >105
            
        nb_repeat_sequence : TYPE: Int
            DESCRIPTION: The number of time you want the sequence to be 
                        displayed
        
        bit_depth : TYPE: Int
            DESCRIPTION: Bit depth, 1 if in black and white. Must be between
            1 and 8. Default: bit_depth=1
        
        compression_type : String
            DESCRIPTION: Compression type, 'rle' for ex. 
            Default: compression_type='rle'

        Returns
        -------
        None.

        """
    
        images = [cv2.imread(file) for file in glob.glob("{}/*.png".format(dmd_pattern_file))]
        nb_patterns=len(images)
        number_of_repeats=nb_patterns*nb_repeat_sequence
        settings = {'compression': compression_type, 'bit_depth': bit_depth}
        
        
        #Opening the patterns:
        dict_patterns={}
        
        for i in range(nb_patterns):
            dict_patterns["pattern{}".format(i)] = dp.DMDPattern(**settings)
        list_pattern=[]
        for i in range(nb_patterns):
            dict_patterns["pattern{}".format(i)].load_png("{}/sequence_{}.png".format(dmd_pattern_file,i))
            
            dict_patterns["pattern{}".format(i)].exposure_time=exposure_time
            dict_patterns["pattern{}".format(i)].dark_time=dark_time
            
            list_pattern.append(dict_patterns["pattern{}".format(i)])
        
        Pattern_sequence={'patterns': list_pattern, 'number_of_repeats': number_of_repeats}
        self.upload_image_sequence(Pattern_sequence)

    
    def display_on_dmd(self, image_or_sequence, dmd_pattern_file, 
                       exposure_time, dark_time, number_of_repeats):
        """
        Display either an image or a sequence.

        Parameters
        ----------
        image_or_sequence : TYPE: string
            DESCRIPTION: 'image' if display one image, 'sequence' if display
            a sequence
            
        Other variables are the same as before.

        Raises
        ------
        Exception
            DESCRIPTION: if image_or_sequence is not 'image' or 'sequence',
            raise an error.

        Returns
        -------
        None.

        """
        
        
        if image_or_sequence=='image':
            self.upload_one_image(dmd_pattern_file, exposure_time, dark_time, number_of_repeats)
            
        elif image_or_sequence=='sequence':
            self.play_pattern_sequence(dmd_pattern_file, exposure_time, dark_time, number_of_repeats)
            
        else:
            raise Exception("image_or_sequence has to be 'image' or 'sequence'.")


    def stop(self, time=10):
        sleep(time)
        self.lc_dmd.pattern_display_start_stop('stop')


if __name__ == '__main__':
    test = Pattern_on_the_fly()
    test.upload_one_image('C:/Users/loicm/Desktop/Cours ENS/M1/Stage/created_patterns/image/stick_bin.jpg', 2*10**6, 1*10**6, 3)
    #test.play_pattern_sequence("C:/Users/loicm/Desktop/Cours ENS/M1/Stage/created_patterns/sequence",1*10**6,105,3)
    #test.stop(10)

