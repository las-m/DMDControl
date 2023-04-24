#!/usr/bin/env python

import numpy as np 
import matplotlib.pyplot as plt
from PIL import Image

class DMDPattern():
    def __init__(self, **kwargs):
        """
        If key is in the dictionary, remove it and return its value, else return default. 
        If default is not given and key is not in the dictionary, a KeyError is raised.  
        """
        self.resolution = kwargs.pop('resolution', (1920, 1080))
        self.zero_point = kwargs.pop('zero_pixel', (960, 540))
        self.compression = kwargs.pop('compression', 'none')
        self.exposure_time = kwargs.pop('exposure_time', 105)
        self.dark_time = kwargs.pop('dark_time', 0)
        self.bit_depth = kwargs.pop('bit_depth', 1)
        self.flicker_active = kwargs.pop('flicker_acitve', True)
        self.wait_for_trigger = kwargs.pop('wait_for_trigger', False)
        
        self.pattern = np.zeros(self.resolution)
        self.compressed_pattern = None
        self.compressed_pattern_length = None

    def compress_pattern(self):
        """
        :return the pattern as a 1d array of uint8's, including the appropriate image header
        """
        #make 1d, apply compression
        compression_function_dict = {'none': self.non_compressed_image, 'rle': self.rle_compressed_image}
        if len(self.pattern.shape) == 2:
            self.pattern_3d = 0xff*np.dstack((self.pattern,self.pattern,self.pattern))
        else:
            self.pattern_3d = self.pattern
        compressed_pattern, pattern_length = compression_function_dict[self.compression](self.pattern_3d)

        #get the header
        header = self.make_header(pattern_length, self.compression)
        command_sequence = [*header,*compressed_pattern]
        
        print ("Compressed to %s bytes" %len(command_sequence))
        cs_uint = np.array(command_sequence,dtype=np.uint8)
        return cs_uint

    def load_png(self,file):
        im_frame = Image.open(file)#.convert('LA')
        self.pattern = np.array(im_frame) 
        width, height = im_frame.size
        self.resolution = (width, height)
        if self.resolution != (1920,1080):
            im = Image.new("RGB", (1920,1080) , color=(0,0,0)) #create black backgorund and add image to get right resolution
            im.paste(im_frame)
            self.pattern = np.array(im)            
        
        if len(self.pattern.shape) == 3 and self.pattern.shape[2] == 4: #if color code includes transparency-byte, ignore it
                self.pattern = np.delete(self.pattern,3,2)

    def show_pattern(self):
        plt.gray()
        plt.imshow(self.pattern,interpolation='none')
        plt.show()

    def non_compressed_image(self,pattern):
        """
        :param (M, N) matrix of uint8 that represents a pattern
        :return 1D 24bit compressed bitmap
        """
        compressed_pattern = np.packbits(np.ravel(pattern))
        
        return compressed_pattern, np.size(compressed_pattern)

    def rle_compressed_image(self, pattern):
        """
        :param (M, N) matrix of uint8 that represents a pattern
        :return 1D 24bit compressed bitmap
        """
        command_sequence = []
        for row_idx in np.arange(np.shape(pattern)[0]):
            command_sequence+=self.rle_row_comp(pattern[row_idx,:])
        command_sequence+=[0x00, 0x01]

        #print np.where(command_sequence == 0x01)
        return command_sequence, len(command_sequence)

    def rle_row_comp(self,row):
        run_idxs, run_lengths, vals = self.standard_rle_compression(row, 0)
        
        command_sequence = []
        for idx, run_idx in np.ndenumerate(run_idxs):
            command_sequence+=self.parse_run(run_lengths[idx], vals[:,idx])
        return command_sequence

    def standard_rle_compression(self, x, zero_index = 0):
        """
        :param (N,3) array that corresponds to part or all of one row of an image.
        :param zero index is an offset of the indexes.
        :returns first indexes of runs, lengths of runs, vals of runs. 
        """
        assert np.shape(x)[1] == 3
        x = np.transpose(x)
        #diffs = np.where(np.sum(np.abs(np.diff(x)),axis=1)!=0)
        diff_idx = np.hstack((np.zeros(1,dtype=np.int64),np.where(np.sum(np.abs(np.diff(x)),axis=0)!=0)[0]+1)) + zero_index   # returns list of indexes of new runs
        diff_idx_hi = np.roll(diff_idx,-1)
        diff_idx_hi[-1] = np.shape(x)[1]
        run_lengths = diff_idx_hi - diff_idx   # compute run lengths
        vals = x[:,diff_idx]  # compute values

        return diff_idx, run_lengths, vals

    def parse_run(self, run_length, run_val):
        run_val = np.ravel(run_val)
        if run_length == 0:
            raise Exception()
        if run_length<256:
            if run_length == 1:
                #return [0x00, 0x01, run_val[0],run_val[1],run_val[2]]
                return [0x01, run_val[0],run_val[1],run_val[2]]
            else:
                return [np.uint8(run_length),run_val[0],run_val[1],run_val[2]]
        else:
            commands = []
            while run_length > 255:
                commands+=self.parse_run(0xff, run_val)
                run_length-=255
            commands+=self.parse_run(run_length, run_val)
            return commands

    def make_header(self,compressed_pattern_length,compression_type):
        """
        :return header for image sequence
        """
        #Note: taken directly from sniffer of the TI GUI
        header = [0x53, 0x70, 0x6C, 0x64, #Signature
                0x80, 0x07, 0x38, 0x04, #Width and height: 1920, 1080
                0x60, 0x11, 0x00, 0x00, #Number of bytes in encoded image_data
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, #reserved
                0x00, 0x00, 0x00, 0x00, # BG color BB, GG, RR, 00
                0x01, #0x01 reserved - manual says 0, sniffer says 1 
                0x00, #encoding 0 none, 1 rle, 2 erle
                0x01, #reserved 
                0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00] #reserved
            
        encoded_length_bytes_header = self.int_to_hex_array(compressed_pattern_length, 4)
        compression_dictionary = {'none': 0, 'rle': 1, 'erle': 2}

        for i in range(4):
            header[8 + i] = encoded_length_bytes_header[i]
        header[25] = compression_dictionary[compression_type]

        return np.array(header, dtype=np.uint8).tolist()

    def int_to_hex_array(self, number, n_bytes = 2):
        """
        :param positive integer
        :return the integer, as a n_bytes long array of uint8's, starting from lsb
        """
        hex_array = []
        for n in range(n_bytes):
            hex_array.append((number >> n*8) & 0xff)
        return hex_array

if __name__ == '__main__':
    pattern = DMDPattern()
    pattern.load_png('../DMD_Test/grayscale.png')
    pattern.show_pattern()