#! /usr/bin/env python
#test script where the DMD flickering is suppressed
 
import pyDMD.DMDPattern as dp
import pyDMD.Pattern_on_the_fly as pfly

settings = {'compression':'rle', 'bit_depth': 1}
settings1 = {'compression':'rle'}
patternDir = "Y:\Archiv\2D\Experiment\DMD Patterns\DMD 2"
pattern = dp.DMDPattern(**settings)
pattern1 = dp.DMDPattern(**settings)
pattern2 = dp.DMDPattern(**settings1)
pattern.load_png('test_patterns/full_white.bmp')
pattern1.load_png('test_patterns/grayscale.png')

# This pattern is shown until the next pattern is triggered because t=105micros
# and flicker_active=False
pattern.exposure_time, pattern.dark_time = 105, 0
pattern.flicker_active = False
pattern.wait_for_trigger = True

# This pattern is shown until the next pattern is triggered because t=105micros
# and flicker_active=False
pattern1.exposure_time, pattern1.dark_time = 105, 0
pattern1.flicker_active = False
pattern1.wait_for_trigger = True

Pattern_sequence = {'patterns': [pattern, pattern1], 'number_of_repeats': 0}
test = pfly.Pattern_on_the_fly()
test.upload_image_sequence(Pattern_sequence)

#test.stop(time=10)