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
