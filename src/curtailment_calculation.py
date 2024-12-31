"""
Overview
This Python script curtailment_calculation.py calculates and analyzes solar power curtailment for a given site and date. 
It uses time-series data from a D-PV system and GHI (Global Horizontal Irradiance) data to determine the amount of energy lost due to various curtailment mechanisms. 
The script identifies curtailment due to tripping events, voltage-VAR control (VVar), and voltage-watt control (VWatt). 
It then summarizes the findings and generates visualizations of GHI, power output, and voltage-power relationships.

Key Components
compute(file_path, data_file, ghi_file): 
    This is the main function that drives the curtailment analysis. 
    It takes the directory path, D-PV data filename, and GHI data filename as input. 
    It orchestrates the entire process from data loading and preprocessing to curtailment calculation and visualization.

Data Loading and Preprocessing: 
    The script uses the pandas library to load and manipulate data. 
    It performs checks on data size and resamples the data to a consistent time interval (minutes). 
    The FileProcessing class handles file input and general data processing tasks.

Curtailment Calculation: 
    Several classes and functions are responsible for calculating different types of curtailment:
TrippingCurt:       Detects and quantifies energy loss due to tripping events.
VVarCurt:           Calculates curtailment due to voltage-VAR control.
VWattCurt:          Calculates curtailment due to voltage-watt control.
Polyfit:            Performs polynomial fitting to estimate expected power generation in the absence of curtailment. This is used as a baseline for comparison.
ClearSkyDay:        Determines if the given day is a clear sky day, which influences the curtailment analysis.
EnergyCalculation:  Calculates the actual and expected energy generated.
Visualization:      The DataVisualization class handles the generation of plots:
    GHI plot over time.
    Scatter plot of power output.
    Line plot of power and voltage, highlighting curtailment periods.
Output: 
    The script displays a summary of the curtailment analysis in a tabular format, including the amount of energy curtailed due to each mechanism. 
    It also generates the visualizations mentioned above.

External Dependencies: 
    The script relies on several external libraries, including pandas, matplotlib, numpy, datetime, pytz, 
    seaborn, and custom modules like energy_calculation, clear_sky_day, tripping_curt, vvar_curt, vwatt_curt, polyfit, file_processing, 
    and data_visualization. These modules likely contain the detailed implementations of the curtailment algorithms and data processing functions.
"""

#IMPORT PACKAGES
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme()
from IPython.display import display

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

#IMPORT FUNCTIONS 
# for package implementatoin
from energy_calculation import *
from clear_sky_day import *
from tripping_curt import *
from vvar_curt import *
from vwatt_curt import *
from polyfit import *
from file_processing import *
from data_visualization import *

#class instantiation
file_processing = FileProcessing()
clear_sky_day = ClearSkyDay()
data_visualization = DataVisualization()
energy_calculation = EnergyCalculation()
tripping_curt = TrippingCurt()
polyfit_f = Polyfit()
vvar_curt = VVarCurt()
vwatt_curt = VWattCurt()


def compute(file_path, data_file, ghi_file):
    ''' Compute solar curtailment from D-PV time series data of a certain site in a certain date & ghi data.
    
    Args:
        file_path (str) : directory path
        data_file (str) : D-PV time series data of a certain site in a certain date file name
        ghi_file (str) : ghi file name

    Returns:
        None, but displaying summary of curtailment analysis, ghi plot, power scatter plot, and power lineplot.
        
    Functions needed:
        - input_general_files
        - check_data_size
        - site_organize
        - resample_in_minute
        - check_polyfit
        - check_clear_sky_day
        - check_tripping_curtailment
        - check_energy_generated
        - check_vvar_curtailment
        - check_vwatt_curtailment
        - check_energy_expected
        - summarize_result_into_dataframe
        - display_ghi
        - display_power_scatter
        - display_power_voltage
    '''

    site_details, unique_cids= file_processing.input_general_files(file_path)
    summary_all_samples = pd.DataFrame()

    data = pd.read_csv(file_path + data_file)
    pd.to_datetime(data['Timestamp'].str.slice(0, 19, 1))
    data['Timestamp'] = pd.to_datetime(data['Timestamp'].str.slice(0, 19, 1))
    data.set_index('Timestamp', inplace=True)

    if size_is_ok := file_processing.check_data_size(data):
        ghi = pd.read_csv(file_path + ghi_file, index_col = 0)
        ghi.index = pd.to_datetime(ghi.index)

        c_id = data['c_id'].iloc[0]
        date = str(data.index[0])[:10]

        data_site, ac_cap, dc_cap, EFF_SYSTEM, inverter = vvar_curt.site_organize(c_id, site_details, data, unique_cids)
        data_site = file_processing.resample_in_minute(data_site)

        #check the expected power using polyfit
        data_site, polyfit, is_good_polyfit_quality = polyfit_f.check_polyfit(data_site, ac_cap)

        is_clear_sky_day = clear_sky_day.check_clear_sky_day(date, file_path)
        tripping_response, tripping_curt_energy, estimation_method, data_site = tripping_curt.check_tripping_curtailment(is_clear_sky_day, c_id, data_site, unique_cids, ac_cap, site_details, date)
        energy_generated, data_site = energy_calculation.check_energy_generated(data_site, date, is_clear_sky_day, tripping_curt_energy)
        vvar_response, vvar_curt_energy, data_site = vvar_curt.check_vvar_curtailment(c_id, date, data_site, ghi, ac_cap, dc_cap, EFF_SYSTEM, is_clear_sky_day)
        data_site, vwatt_response, vwatt_curt_energy = vwatt_curt.check_vwatt_curtailment(data_site, date, is_good_polyfit_quality, file_path, ac_cap, is_clear_sky_day)

        energy_generated_expected, estimation_method = energy_calculation.check_energy_expected(energy_generated, tripping_curt_energy, vvar_curt_energy, vwatt_curt_energy, is_clear_sky_day)

        summary = file_processing.summarize_result_into_dataframe(c_id, date, is_clear_sky_day, energy_generated, energy_generated_expected, estimation_method, tripping_response, tripping_curt_energy, vvar_response, vvar_curt_energy, vwatt_response, vwatt_curt_energy)

        display(summary)
        data_visualization.display_ghi(ghi, date)
        data_visualization.display_power_scatter(data_site, ac_cap)
        plt = data_visualization.display_power_voltage(data_site, date, vwatt_response, vvar_response)
        plt.show()
    else:
        print('Cannot analyze this sample due to incomplete data.')

### SUGGESTIONS SOURCERY
# Hey there - I've reviewed your changes - here's some feedback:

# Overall Comments:

# Consider breaking down the compute() function into smaller, more focused functions for better maintainability and testing. Currently it handles too many responsibilities (data loading, processing, curtailment calculations, and visualization).
# Move the matplotlib visualization parameters from global scope into the DataVisualization class to prevent potential side effects on other parts of the application.
# Here's what I looked at during the review
# 🟢 General issues: all looks good
# 🟢 Security: all looks good
# 🟢 Testing: all looks good
# 🟢 Complexity: all looks good
# 🟢 Documentation: all looks good
