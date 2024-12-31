"""
Overview
    This Python file (file_processing.py) provides a class FileProcessing designed to handle and process 
    data related to solar power generation. 
    It includes functionalities for inputting data from various sources 
    (circuit details, site details, GHI data), summarizing results into a convenient dataframe, 
    and performing checks and preprocessing steps on the data, 
    such as resampling and data size validation. 
    The file also sets global parameters for plot styling.

Key Components
FileProcessing Class: 
    This class encapsulates the core file processing logic.
input_general_files(self, file_path): 
    Reads circuit details, site details, and unique circuit IDs from CSV files located in the specified 
    file_path. Returns the merged site and circuit details as a dataframe and unique circuit IDs.
summarize_result_into_dataframe(...): 
    Takes various parameters related to energy generation (actual, expected, curtailment, etc.) 
    and organizes them into a summary dataframe. 
    This function is crucial for reporting and analysis.
check_data_size(self, data): 
    Performs a basic sanity check on the input D-PV time series data to ensure it contains a 
    reasonable number of data points and covers the expected daytime hours.
resample_in_minute(self, data): 
Resamples the input D-PV time series data to a minute-level resolution if the original data has a 
higher resolution (more than 2000 data points). This function helps standardize the data frequency.
read_ghi(self, file_path, ghi_filename): 
    Reads Global Horizontal Irradiance (GHI) data from a CSV file, adds a timestamp column, 
    and converts the GHI values to numeric format. It returns both the modified and original GHI dataframes.
Global Parameters: 
    The file sets global parameters for font sizes and plot styling using matplotlib.pyplot. 
    This ensures consistent visualization across the project.
"""

#IMPORT PACKAGES
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns; sns.set_theme()

#SET GLOBAL PARAMETERS
# ================== Global parameters for fonts & sizes =================
FONT_SIZE = 20
rc={'font.size': FONT_SIZE, 'axes.labelsize': FONT_SIZE, 'legend.fontsize': FONT_SIZE, 
    'axes.titlesize': FONT_SIZE, 'xtick.labelsize': FONT_SIZE, 'ytick.labelsize': FONT_SIZE}
plt.rcParams.update(**rc)
plt.rc('font', weight='bold')
 
# For label titles
fontdict={'fontsize': FONT_SIZE, 'fontweight' : 'bold'}
# can add in above dictionary: 'verticalalignment': 'baseline' 

style = 'ggplot' # choose a style from the above options
plt.style.use(style)

class FileProcessing():
    """
    A class consists of methods related to file processing

    Methods
        input_general_files: Input circuit data, site data, and unique cids data. 
        summarize_result_into_dataframe: Collect results into a dataframe to be shown as summary.
        check_data_size: Check whether the D-PV time series data has normal size
        resample_in_minute: Check whether the length of the data is in 5 s (more than 10k rows), then resample it into per minute.
        read_ghi: Input the ghi data and adding a timestamp column, while keeping the original ghi data.
        
    """
    
    def input_general_files(self, file_path):
        """Input circuit data, site data, and unique cids data. 

        Args:
            file_path (str): Local directory where the datafiles are stored. 

        Returns:
            site_details (df): merged site_details and circuit_details file
            unique_cids (df): array of c_id and site_id values. 
        """

        circuit_details = pd.read_csv(file_path + r"/details_c_id.csv")
        site_details = pd.read_csv (file_path + r"/details_site_id.csv")
        site_details = site_details.merge(circuit_details, left_on = 'site_id', right_on = 'site_id')
        unique_cids = pd.read_csv(file_path + r"/UniqueCids500.csv", index_col = 0)
        return site_details, unique_cids

    def summarize_result_into_dataframe(self, c_id, date, is_clear_sky_day, energy_generated, energy_generated_expected, estimation_method, tripping_response, tripping_curt_energy, vvar_response, vvar_curt_energy, vwatt_response, vwatt_curt_energy):
        """Collect results into a dataframe to be shown as summary.

        Args:
            c_id (int): circuit id
            date (str): date
            is_clear_sky_day (bool): whether the certain date is a clear sky day or not based on the ghi data
            energy_generated (float): the amount of actual energy generated based on the power time series data
            energy_generated_expected (float): the amount of expected energy generated based on either linear or polyfit estimate
            estimation_method (str): linear or polyfit
            tripping_response (str): whether there is a detected tripping response or not, meaning zero power in the day
            tripping_curt_energy (float): the amount of energy curtailed due to tripping response
            vvar_response (str): whether there is a detected V-VAr respones or not, meaning VAr absorbtion or injection in the day
            vvar_curt_energy (float): the amount of energy curtailed due to VVAr response limiting the maximum allowed real power
            vwatt_response (str): whether there is detected V-Watt response or not, can also be inconclusive for some cases.
            vwatt_curt_energy (float): the amount of eneryg curtailed due to VWatt response limiting the maximum allowed real power.

        Returns:
            summary (df): summarized results.
        """

        summary = pd.DataFrame({
            'c_id' : [c_id],
            'date' : [date],
            'clear sky day': [is_clear_sky_day],
            'energy generated (kWh)' : [energy_generated],
            'expected energy generated (kWh)' : [energy_generated_expected],
            'estimation method' : [estimation_method],
            'tripping response' : [tripping_response],
            'tripping curtailment (kWh)' : [tripping_curt_energy],
            'V-VAr response' : [vvar_response],
            'V-VAr curtailment (kWh)' : [vvar_curt_energy],
            'V-Watt response' : [vwatt_response],
            'V-Watt curtailment (kWh)' : [vwatt_curt_energy]
        })
        return summary

    def check_data_size(self, data):
        """Check whether the D-PV time series data has normal size, where we assume the resolution of the timestamp is 60 s or smaller. 
        Args:
            data (df): D-PV time series data

        Returns:
            size_is_ok (bool): True if more the data makes sense
        """
        
        VERY_LOW_OUTPUT_AVE_PERCENTAGE_CAPACITY = 0.05
        MIN_LEN = 2 #before is 10
        
        if len(data) > MIN_LEN:
            if ((data.index.hour >= 7) & (data.index.hour <= 17)).sum() > 0: #there must be datapoint between 7 and 17
                size_is_ok = True
            else:
                size_is_ok = False
        else:
            size_is_ok = False
            
        return size_is_ok

    def resample_in_minute(self, data):
        ''' Check whether the length of the data is in 5 s (more than 10k rows), then resample it into per minute.

        Args:
            data(df) : D-PV time series data

        Returns:
            data(df) : D-PV time series data in min  
        '''

        if len(data) > 2000:
            data = data.resample('min').agg({
                'c_id' : np.mean,
                'energy' : np.sum,
                'power' : np.mean,
                'reactive_power' : np.mean,
                'voltage' : np.mean,
                'duration' : np.sum,
                'va' : np.mean,
                'pf' : np.mean
            })
        return data

    # Load GHI data
    def read_ghi(self, file_path, ghi_filename):
        ''' Input the ghi data and adding a timestamp column, while keeping the original ghi data.

        Args:
            file_path (str): local directory path
            ghi_filename (str) : ghi file name with / in the beginning.

        Returns:
            ghi (df): ghi data with added timestamp column as an index
            ghi_ori(df): unmodified ghi data
        '''

        ghi_path = file_path + ghi_filename
        ghi = pd.read_csv (ghi_path) 
        ghi_ori = ghi.copy()

        ghi['timestamp'] = pd.to_datetime(pd.DataFrame ({'year' : ghi['Year Month Day Hours Minutes in YYYY'].values, 
                                                        'month' : ghi['MM'], 
                                                        'day' : ghi['DD'], 
                                                       'hour' : ghi['HH24'], 
                                                       'minute' : ghi['MI format in Local standard time']}))
        ghi.set_index('timestamp', inplace = True)
        # Deal with the space characters (ghi is in object/string form at the moment)
        ghi['Mean global irradiance (over 1 minute) in W/sq m'] = [float(ghi_t) if ghi_t.count(' ')<= 3 else np.nan for ghi_t in ghi['Mean global irradiance (over 1 minute) in W/sq m']]
        return ghi, ghi_ori

### SUGGESTIONS SOURCERY
# Hey there - I've reviewed your changes - here's some feedback:

# Overall Comments:

# Consider adding error handling for file operations - the current implementation assumes all file operations will succeed which could lead to runtime errors if files are missing or permissions are incorrect.
# Replace magic numbers (e.g., 2000 in resample_in_minute, 0.05 and 2 in check_data_size) with named constants and add documentation explaining their significance.
# Here's what I looked at during the review
# 🟡 General issues: 1 issue found
# 🟢 Security: all looks good
# 🟢 Testing: all looks good
# 🟢 Complexity: all looks good
# 🟢 Documentation: all looks good
# e:_UNHCR\CODE\solar_unhcr\src\file_processing.py:52

# suggestion(code_refinement): Method has many parameters, consider using a dataclass or dictionary
#         unique_cids = pd.read_csv(file_path + r"/UniqueCids500.csv", index_col = 0)
#         return site_details, unique_cids

#     def summarize_result_into_dataframe(self, c_id, date, is_clear_sky_day, energy_generated, energy_generated_expected, estimation_method, tripping_response, tripping_curt_energy, vvar_response, vvar_curt_energy, vwatt_response, vwatt_curt_energy):
#         """Collect results into a dataframe to be shown as summary.

# With 12 parameters, this method signature is quite complex. A dataclass or dictionary could make the method more maintainable.

# Suggested implementation:

# import pandas as pd
# import matplotlib.pyplot as plt
# from dataclasses import dataclass

# The method signature has been changed to use the new ResultSummary dataclass.
# A new to_dataframe() method has been added to the dataclass to convert the summary to a DataFrame.
# Developers will now create a ResultSummary instance and call to_dataframe() instead of the previous method.
# Example usage would look like:

# summary = ResultSummary(
#     c_id='some_id', 
#     date='2023-01-01', 
#     is_clear_sky_day=True, 
#     # ... other parameters ...
# )
# result_df = summary.to_dataframe()
# This approach provides several benefits:

# Type hints for all parameters
# Easier to read and understand the data structure
# Immutable by default
# Can be easily extended or modified
