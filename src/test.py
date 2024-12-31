"""
Overview
This Python script (test.py) is designed to test the curtailment_calculation module by running it against a set of sample data files. 
It iterates through a specified list of sample numbers, constructs file paths for data and GHI 
(Global Horizontal Irradiance) files corresponding to each sample, and then calls the compute function 
from the curtailment_calculation module to perform analysis on each sample.

Key Components
curtailment_calculation module: This module contains the core logic for performing curtailment analysis. 
The script imports and utilizes its compute function.
file_path variable: 
    This variable stores the base directory path where the data files are located. 
    It's crucial to configure this path correctly for the script to function as intended. 
    The current path suggests a Windows environment.
Loop and sample numbers: 
    The for loop iterates through a list of sample numbers 
    ([1, 11] in this case). The script is designed to test different scenarios, 
    likely representing various curtailment events and data conditions as described in the comments.
File path construction: 
    Inside the loop, the script dynamically constructs the file paths for the data and GHI files 
    using string formatting. This allows for easy processing of multiple sample files.
compute function call: 
    The core functionality lies in calling curtailment_calculation.compute() with the constructed file paths. 
    This function likely performs the actual curtailment analysis based on the provided data and GHI.
"""

import curtailment_calculation

# MODIFY THE FILE_PATH ACCORDING TO YOUR DIRECTORY FOR SAVING THE DATA FILES.
file_path = r"E:\_UNHCR\CODE\solar_unhcr\data" #for running on smh laptop

#These samples represent (consecutively) tripping curtailment in a non clear sky day, tripping curtailment in a clear sky
#day, vvar curtailment, vwatt curtailment, incomplete datasample, and sample without curtailment.
for i in [1, 11]: #, [1,11,14, 4, 5, 9]:
    sample_number = i
    print('Analyzing sample number {}'.format(i))
    data_file = '/data_sample_{}.csv'.format(sample_number)
    ghi_file = '/ghi_sample_{}.csv'.format(sample_number)

    curtailment_calculation.compute(file_path, data_file, ghi_file)

### SUGGESTIONS SOURCERY
# Hey there - I've reviewed your changes - here's some feedback:

# Overall Comments:

# Use relative paths and path manipulation libraries (like pathlib) instead of hardcoded absolute paths to make tests portable across different environments
# Either uncomment and run all test cases or remove the documentation for unused test cases to avoid confusion. Currently only running 2 out of 6 described test scenarios.
# Here's what I looked at during the review
# e:/_UNHCR/CODE/solar_unhcr/src/test.py:1

# issue(testing): This file seems to contain example usages, not actual tests.
# import curtailment_calculation

# # MODIFY THE FILE_PATH ACCORDING TO YOUR DIRECTORY FOR SAVING THE DATA FILES.
# It's important to have proper unit tests to ensure the curtailment_calculation.compute function works correctly. Consider using a testing framework like pytest and writing assertions to validate the outputs of the function given specific inputs.

# Resolve
# e:/_UNHCR/CODE/solar_unhcr/src/test.py:6

# issue(testing): Missing tests for described edge cases.
# # MODIFY THE FILE_PATH ACCORDING TO YOUR DIRECTORY FOR SAVING THE DATA FILES.
# file_path = r"E:\_UNHCR\CODE\solar_unhcr\data" #for running on smh laptop

# #These samples represent (consecutively) tripping curtailment in a non clear sky day, tripping curtailment in a clear sky
# #day, vvar curtailment, vwatt curtailment, incomplete datasample, and sample without curtailment.
# for i in [1, 11]: #, [1,11,14, 4, 5, 9]:
#     sample_number = i
# You've described several important edge cases (vvar curtailment, vwatt curtailment, incomplete data, no curtailment). Each of these should have its own dedicated test case with clear assertions to ensure the function handles them correctly.

# Resolve
# e:/_UNHCR/CODE/solar_unhcr/src/test.py:8

# question(testing): Unclear why some sample numbers are commented out.

# #These samples represent (consecutively) tripping curtailment in a non clear sky day, tripping curtailment in a clear sky
# #day, vvar curtailment, vwatt curtailment, incomplete datasample, and sample without curtailment.
# for i in [1, 11]: #, [1,11,14, 4, 5, 9]:
#     sample_number = i
#     print('Analyzing sample number {}'.format(i))
# The commented-out sample numbers suggest potentially incomplete testing. Either include them in the test suite or remove them entirely. If they represent known broken cases, create separate tests to track those failures.

# Resolve
# e:/_UNHCR/CODE/solar_unhcr/src/test.py:14

# issue(testing): Missing assertions.
#     data_file = '/data_sample_{}.csv'.format(sample_number)
#     ghi_file = '/ghi_sample_{}.csv'.format(sample_number)

#     curtailment_calculation.compute(file_path, data_file, ghi_file)
# Calling the function without assertions doesn't constitute a proper test. Add assertions to validate the output of compute against expected values for each sample. For example, check the returned curtailment values, any status flags, or other relevant outputs.
