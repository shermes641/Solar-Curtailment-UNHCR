"""
Overview
    This Python file (energy_calculation.py) defines a class EnergyCalculation that provides methods 
    for calculating and analyzing energy generation from solar power systems. 
    It focuses on determining the actual energy generated, estimating the expected generation 
    without curtailment (reduction in output), and identifying the estimation method used. 
    The file also includes several imported libraries for data analysis, visualization, 
    and time zone handling.

Key Components
EnergyCalculation Class: 
    This class encapsulates the core functionality of the file. It contains two main methods:

check_energy_generated(data_site, date, is_clear_sky_day, tripping_curt_energy): 
    This method calculates the total energy generated on a specific date for a given site. 
    It takes the time-series data, date, clear sky status, and energy loss due to tripping as input. 
    It returns the total energy generated and potentially updates the input data with expected power values.
check_energy_expected(energy_generated, tripping_curt_energy, vvar_curt_energy, vwatt_curt_energy, is_clear_sky_day): 
    This method estimates the expected energy generation without curtailment based on the actual generation 
    and various curtailment factors (tripping, VVAr, VWatt). 
    It also determines the estimation method used ("Polyfit" for clear sky days, "Linear" 
    for non-clear sky days with tripping, or "n/a" otherwise).
Global Parameters: 
    The file sets global parameters for font sizes and styling used in plots, 
    although plotting itself is not implemented within this file. 
    This suggests that these settings are used by other parts of the project that utilize the 
    calculated energy values.

External Libraries: 
    The file imports several external libraries, including matplotlib, numpy, datetime, pytz, math, seaborn, and others. 
    These libraries are used for data manipulation, visualization, time zone handling, and mathematical calculations.
"""

#IMPORT PACKAGES
import matplotlib.pyplot as plt
import datetime as dt
import math
import seaborn as sns; sns.set_theme()
#import datetime

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

#ENERGY GENERATED CALCULATION
class EnergyCalculation():
    """
    A class consists of methods related to energy calculation

    Methods
        check_energy_generated : Get the amount of energy generated in a certain site in a certain day, unit kWh.
        check_energy_expected : Calculate the expected energy generation without curtailment and the estimation method
    """
    
    def check_energy_generated(self, data_site, date, is_clear_sky_day, tripping_curt_energy):
        """Get the amount of energy generated in a certain site in a certain day, unit kWh.

        Args:
            data_site (df): Cleaned D-PV time-series data, output of site_orgaize function
            date (str): date in focus
            is_clear_sky_day (bool): whether the date is a clear sky day or not
            tripping_curt_energy (float): the amount of energy curtailed due to tripping response

        Returns:
            energy_generated (float): Single value of the total energy generated in that day
            data_site (df): D-PV time series data with updated 'power_expected' column if the there is tripping in a non clear sky day.
        """

        date_dt = dt.datetime.strptime(date, '%Y-%m-%d').date()
        date_idx = data_site.index.date == date_dt
        energy_generated = data_site.loc[date_idx, 'power'].resample('h').mean().sum()/1000

        if not is_clear_sky_day and tripping_curt_energy > 0:
            data_site['power_expected'] = data_site['power_expected_linear']

        return energy_generated, data_site


    def check_energy_expected(self, energy_generated, tripping_curt_energy, vvar_curt_energy, vwatt_curt_energy, is_clear_sky_day):
        ''' Calculate the expected energy generation without curtailment and the estimation method

        Args:
            energy_generated (float): the actual energy generated with curtailment
            tripping_curt_energy (float) : energy curtailed due to tripping. Can't be n/a
            vvar_curt_energy (float) :energy curtailed due to VVAr. Can be n/a in a non clear sky day
            vwatt_curt_energy (float) : energy curtailed due to VWatt. Can be n/a in a non clear sky day
            is_clear_sky_day (bool) : yes if the day is a clear sky day

        Returns:
            energy_generated_expected (float) : the estimated energy generated without curtailment
            estimation_method (str) : the method of estimating the previous value
        '''

        if is_clear_sky_day:
            estimation_method = 'Polyfit'
            energy_generated_expected = energy_generated + tripping_curt_energy + vvar_curt_energy + vwatt_curt_energy
        elif tripping_curt_energy > 0:
            estimation_method = 'Linear'
            if math.isnan(vvar_curt_energy):
                vvar_curt_energy = 0
            if math.isnan(vwatt_curt_energy):
                vwatt_curt_energy = 0
            energy_generated_expected = energy_generated + tripping_curt_energy + vvar_curt_energy + vwatt_curt_energy
        else:
            estimation_method = 'n/a'
            energy_generated_expected = 'n/a'

        return energy_generated_expected, estimation_method

### SUGGESTIONS SOURCERY
# Hey there - I've reviewed your changes and they look great!

# Here's what I looked at during the review
# 🟡 General issues: 1 issue found
# 🟢 Security: all looks good
# 🟢 Testing: all looks good
# 🟢 Complexity: all looks good
# 🟢 Documentation: all looks good
# e:/_UNHCR/CODE/solar_unhcr/src/energy_calculation.py:101

# issue(bug_risk): Mixing string and float return types can cause type inconsistency
#             estimation_method = 'n/a'
#             energy_generated_expected = 'n/a'

#         return energy_generated_expected, estimation_method
# Returning 'n/a' as a string alongside float values breaks type consistency and could cause runtime errors in downstream processing.
