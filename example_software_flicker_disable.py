#! /usr/bin/env python
#test script where the DMD flickering is suppressed
 
import pyDMD.DMDPattern as dp
import pyDMD.Pattern_on_the_fly as pfly

settings = {'compression':'rle', 'bit_depth': 1}
settings1 = {'compression':'rle'}
pattern = dp.DMDPattern(**settings)
pattern1 = dp.DMDPattern(**settings)
pattern2 = dp.DMDPattern(**settings1)
pattern.load_png('test_patterns/full_white.bmp')
pattern1.load_png('test_patterns/full_black.bmp')
pattern2.load_png('test_patterns/full_white.bmp')

pattern.exposure_time, pattern.dark_time = 105, 0
pattern.flicker_active = False
pattern1.exposure_time, pattern1.dark_time = 105, 0
pattern1.flicker_active = False
pattern2.exposure_time, pattern2.dark_time = 1000000, 0

#Pattern_sequence = {'patterns': [pattern, pattern1, pattern2], 'number_of_repeats': 3}
#Pattern_sequence = {'patterns': [pattern, pattern1, pattern2]}#, 'number_of_repeats': 1}
Pattern_sequence = {'patterns': [pattern, pattern1]}#, 'number_of_repeats': 1}
test = pfly.Pattern_on_the_fly()
test.upload_image_sequence(Pattern_sequence, wait_for_trigger=True)
test.stop(time=10)