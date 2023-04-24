#! /usr/bin/env python
#test script where the DMD flickering is suppressed
 
import pyDMD.DMDPattern as dp
import pyDMD.Pattern_on_the_fly as pfly

settings = {'compression':'rle', 'bit_depth': 1}
pattern = dp.DMDPattern(**settings)
pattern.load_png('test_patterns/BoxDMD2_500px.png')

pattern.exposure_time, pattern.dark_time = 105, 0

# Show pattern forever -> number_of_repeats = 0
Pattern_sequence = {'patterns': [pattern], 'number_of_repeats': 0}
test = pfly.Pattern_on_the_fly()
test.upload_image_sequence(Pattern_sequence)
