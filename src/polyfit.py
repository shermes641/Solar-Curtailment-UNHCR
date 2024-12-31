"""
Overview
This Python file (polyfit.py) provides a Polyfit class for estimating the expected energy generation of a 
solar PV system without curtailment. It uses polynomial fitting to model the power generation curve 
throughout the day, filtering the input data to remove noise and the effects of curtailment. 
The core functionality revolves around fitting a quadratic polynomial to the power generation data and 
then using this polynomial to estimate the expected power at any given time.

Key Components
Polyfit Class: 
    This class encapsulates all the methods related to polynomial fitting and power generation estimation.
    check_polyfit Method: 
        This is the main method of the class. It orchestrates the entire process of data filtering, 
        polynomial fitting, quality checking, and energy generation calculation. 
        It takes the time series data and AC capacity as input and returns the fitted polynomial, 
        a quality flag, and the calculated and expected energy generation.
Filtering Methods: 
    Several methods are dedicated to filtering the input data:
    filter_sunrise_sunset: 
        Filters data outside of sunrise and sunset times based on a power threshold.
    filter_data_limited_gradients: 
        Filters data points based on the gradient of the power curve to ensure a generally parabolic shape, characteristic of solar power generation.
    filter_power_data_index: 
        Filters out data points that indicate curtailment (sudden drops in power output).
    get_datetime_list Method: 
        Converts a list of string timestamps to numerical datetime objects suitable for polynomial fitting.
    get_polyfit Method: 
        Performs the polynomial fitting using NumPy's polyfit function. It takes the time and power data, and the degree of the polynomial (typically 2 for a quadratic fit) as input and returns the fitted polynomial.
    get_single_date_time Method: 
        Converts a single string timestamp to a numerical datetime object.
Global Parameters: 
    The file sets global parameters for font sizes and styling used in plotting 
    (although plotting is commented out in the current code). These parameters enhance the visualization 
    of the results if plotting is enabled.
"""

#IMPORT PACKAGES
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.dates as md
from datetime import datetime
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

class Polyfit():
    """
    A class consists of methods related to polyfit estimate for expected energy generation without curtailment. 

    Methods
        check_polyfit : Filter the power data, do polyfit estimate, check its quality, and calculate expected energy generated.
        filter_sunrise_sunset : Filter a D-PV Time series data based on its estimated sunrise and sunset time.
        filter_data_limited_gradients : Filter the power_array data so it includes only decreasing gradient (so the shape is parabolic)
        filter_power_data_index : Take the time and power data from D-PV time-series data & filter out curtailment. Will be used for polyfit regression.
        get_datetime_list : CONVERT A LIST STRING TIMESTAMP TO DATETIME OBJECTS, THEN CONVERT IT TO FLOAT OF UNIX TIMESTAMPS.
        get_polyfit : GET POLYFIT OF DESIRED DEGREE, NEED x_array as float, not dt object
        get_single_date_time : CONVERT A SINGLE STRING TIMESTAMP TO DATETIME OBJECTS
    """
    
    def check_polyfit(self, data_site, ac_cap):
        """Filter the power data, do polyfit estimate, check its quality, and calculate expected energy generated.

        Args:
            data_site (df): Cleaned D-PV time-series data
            ac_cap (int): The maximum real power generated by the pv system due to inverter limitation

        Returns:
            polyfit (polyfit) : function to transform map timestamp into expected power without curtailment
            is_good_polyfit_quality (bool) : True only if more than 50 actual points are near to polyfit result
            energy_generated (float) : calculated energy generated
            energy_generated_expected (float): calculated expected generated energy from the polyfit 
            data_site (df): data_site with expected power column

        Functions needed:
        - filter_sunrise_sunset
        - filter_power_data_index
        - filter_data_limited_gradients
        - get_datetime_list
        - get_polyfit
        """
        data_site.index.rename('ts', inplace = True)

        sunrise, sunset, data_site = self.filter_sunrise_sunset(data_site)
        data_site['power_relative'] = data_site['power'] / ac_cap
        timestamp_complete = data_site.index
        data_site_more_300 = data_site.loc[data_site['power'] > 300]

        power_array, time_array = self.filter_power_data_index(data_site_more_300)
        time_array = time_array.strftime('%Y-%m-%d %H:%M:%S')
        time_array = time_array.to_series(index=None, name='None')
        power_array, time_array = self.filter_data_limited_gradients(power_array, time_array)

        time_array_float = self.get_datetime_list(time_array)

        polyfit = self.get_polyfit(time_array_float, power_array, 2)

        polyfit_power_array = polyfit(time_array_float)

        timestamp = timestamp_complete
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        timestamp = self.get_datetime_list(timestamp)
        data_site['power_expected'] = polyfit(timestamp)
        data_site.loc[data_site['power_expected'] < 0, 'power_expected'] = 0

        #correct the power expected when it is below the actual power
        #data_site.loc[data_site['power_expected'] < data_site['power'], 'power_expected'] = data_site['power']

        #limit the maximum power expected to be the same with ac capacity of the inverter
        data_site.loc[data_site['power_expected'] > ac_cap, 'power_expected'] = ac_cap

        #plt.plot(data_site.index, data_site['power'])
        #plt.plot(data_site.index, data_site['power_expected'])
        #plt.show()

        error = abs(data_site['power_expected'] - data_site['power'])
        points_near_polyfit_count = error[error<50].count()

        if points_near_polyfit_count > 50: #the initial value is 50
            is_good_polyfit_quality = True
        else:
            is_good_polyfit_quality = False

        return data_site, polyfit, is_good_polyfit_quality

    def filter_sunrise_sunset(self, df):
        """Filter a D-PV Time series data based on its estimated sunrise and sunset time.

        Args:
        df (df): D-PV Time series data with 'power' column

        Returns:
        sunrise (timestamp): estimated sunrise time (when power is >10 W for the first time in a day)
        sunset (timestamp): the opened ghi data (when power is >10 W for the last time in a day)
        df (df): filtered D-PV Time series data

        The sunrise and sunset time may be inaccurate in a cloudy morning or evening. However, it should not
        affect the result because we only care about the power produced by the PV system. 
        """

        LIMIT_DAY_POWER = 10
        if df is None or len(df.index) == 0:
            return None, None, None

        tmp_df = df.loc[df['power'] > LIMIT_DAY_POWER]
        if len(tmp_df.index) == 0:
            return None, None, None

        sunrise = tmp_df.index[0]
        sunset = tmp_df.index[-1]

        df = df.loc[df.index > sunrise]
        df = df.loc[df.index < sunset]

        return sunrise, sunset, df

    def filter_data_limited_gradients(self, power_array, time_array):
        """Filter the power_array data so it includes only decreasing gradient (so the shape is parabolic)

        Args:
        power_array (pd series): non curtailment filtered power data
        time_array (pd datetime): non curtailment filtered timestamp data

        Returns:
        power_array (pd series): gradient filtered power data
        time_array (pd datetime): gradient filtered timestamp data

        Funcitons needed:
        - get_single_date_time
        """

        if power_array is None:
            return None, None

        # IN GENERAL ANLGE MUST BE BETWEEN THESE VALUES
        ANGLE_LOWER_LIMIT = 80
        ANGLE_UPPER_LIMIT = 90

        # BUT AFTER 'CONTINUANCE_LIMIT' CONTINUOUS VALUES HAVE BEEN ACCEPTED, THE LOWER ANGLE LIMIT IS RELAXED TO THIS VALUE BELOW
        WIDER_ANGLE_LOWER_LIMIT = 70
        CONTINUANCE_LIMIT = 2

        gradients = []
        timeGradients = []
        power_array = power_array.tolist()
        time_array = time_array.tolist()
        filter_array = []

        n = len(power_array)
        gradientsCompliance = [0] * n

        runningCount = 0

        for i in range(1, n):
            g = abs(math.degrees(math.atan((power_array[i] - power_array[i - 1]) / (
                        self.get_single_date_time(time_array[i]) - self.get_single_date_time(time_array[i - 1])))))

            addFlag = False

            if g > ANGLE_LOWER_LIMIT and g < ANGLE_UPPER_LIMIT:
                addFlag = True
                runningCount += 1

            elif runningCount > CONTINUANCE_LIMIT and g > WIDER_ANGLE_LOWER_LIMIT:
                addFlag = True

            else:
                runningCount = 0

            if addFlag:
                gradientsCompliance[i - 1] += 1
                gradientsCompliance[i] += 1

            if g > 85:
                gradients.append(g)
                timeGradients.append(time_array[i])

        if gradientsCompliance[0] == 1 and gradientsCompliance[1] == 2:
            filter_array.append(True)
        else:
            filter_array.append(False)

        for i in range(1, n - 1):
            if gradientsCompliance[i] == 2:
                filter_array.append(True)
            elif gradientsCompliance[i] == 1 and (gradientsCompliance[i - 1] == 2 or gradientsCompliance[i + 1] == 2):
                filter_array.append(True)
            else:
                filter_array.append(False)

        if gradientsCompliance[n - 1] == 1 and gradientsCompliance[n - 2] == 2:
            filter_array.append(True)
        else:
            filter_array.append(False)


        power_array = pd.Series(power_array)
        time_array = pd.Series(time_array)

        power_array = power_array[filter_array]
        time_array = time_array[filter_array]

        return power_array, time_array



    def filter_power_data_index(self, df):
        """Take the time and power data from D-PV time-series data & filter out curtailment. Will be used for polyfit regression.

        Args:
        df (df): Time-series D-PV data with power column and timestamp as an index

        Returns:
        power_array (pd series): filtered power data
        time_array (pd datetime): filtered timestamp data

        This function filter outs data point that is decreasing in the first half, and filters out data point that
        is incerasing in the second half. That happens only if there is curtailment. 
        """

        max_daily_power = max(df.power)
        if len(df.loc[df['power'] == max_daily_power].index) > 1:
            first_time_highest = str(df.loc[df['power'] == max_daily_power].index[0])
            df.loc[first_time_highest, 'power'] += 1
            max_daily_power = max(df.power)

        filter_first_half = []
        filter_second_half = []
        power_array = df.power
        time_array = df.index

        halfFlag = True  # True is first half, False is second half
        last_highest_power = 0

        for power in power_array:

            # IF power IS GREATER THAN last_highest_power THEN INCLUDE power AND INCREASE last_highest_power
            if power > last_highest_power:
                last_highest_power = power
                filter_first_half.append(True)
            else:
                filter_first_half.append(False)

            if power == max_daily_power:
                break

        last_highest_power = 0

        # PERFORM SAME FILTER ON SECOND SIDE OF POWER ARRAY
        for power in power_array.iloc[::-1]:

            if power == max_daily_power:
                break

            if power > last_highest_power:
                last_highest_power = power
                filter_second_half.append(True)
            else:
                filter_second_half.append(False)

        # COMBINE TO FILTERED SIDES
        filter_second_half.reverse()
        filter_array = filter_first_half + filter_second_half
        return power_array[filter_array], time_array[filter_array]

    def get_datetime_list(self, list_to_convert):
        """CONVERT A LIST STRING TIMESTAMP TO DATETIME OBJECTS, THEN CONVERT IT TO FLOAT OF UNIX TIMESTAMPS.

        Args:
        list_to_convert (pd Series) : List of time in str. Example can be time_array

        Returns:
        datenums (ndarray) : List of float unix timestamp

        This is used for polyfit preparation.
        """
        # 
        dates = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in list_to_convert]
        datenums = md.date2num(dates)
        return datenums

    def get_polyfit(self, x_array, y_array, functionDegree):
        """GET POLYFIT OF DESIRED DEGREE, NEED x_array as float, not dt object

        Args:
        x_array (ndarray) : List of float unix timestamp
        y_array (pd Series): List of power value corresponding to x_array time
        functionDegree (int): Degree of polynomial. Quadratic functions means functionDegree = 2

        Returns:
        polyfit (np poly1d): polyfit model result, containing list of the coefficients and the constant.
                            The first, second, and third values are coef of x^2, x, and the constant.
        """


        timestamps = x_array
        xp = np.linspace(timestamps[0], timestamps[len(timestamps) - 1], 1000) #IDK what is this for. Seems redudant.
        z = np.polyfit(timestamps, y_array, functionDegree)
        polyfit = np.poly1d(z)

        return polyfit


    def get_single_date_time(self, d):
        """CONVERT A SINGLE STRING TIMESTAMP TO DATETIME OBJECTS

        Args:
        d (str): string timestamp

        Returns:
        daetimeobject
        """
        return md.date2num(datetime.strptime(d, '%Y-%m-%d %H:%M:%S'))
    
### SUGGESTIONS SOURCERY
# Hey there - I've reviewed your changes - here's some feedback:

# Overall Comments:

# Consider breaking down the Polyfit class into smaller, more focused classes (e.g., DataFilter, DateTimeConverter, PolynomialFitter) to improve maintainability and follow Single Responsibility Principle.
# Document the significance and derivation of magic numbers (e.g., ANGLE_LOWER_LIMIT = 80, CONTINUANCE_LIMIT = 2) to help maintainers understand their purpose.
# Add input validation and error handling to handle malformed data gracefully, particularly in methods like filter_power_data_index and check_polyfit.
# Here's what I looked at during the review
# 🟡 General issues: 2 issues found
# 🟢 Security: all looks good
# 🟢 Testing: all looks good
# 🟢 Complexity: all looks good
# 🟢 Documentation: all looks good
# e:/_UNHCR/CODE/solar_unhcr/src/polyfit.py:136

# suggestion(code_refinement): Overly complex gradient filtering method with multiple nested conditions

#         return sunrise, sunset, df

#     def filter_data_limited_gradients(self, power_array, time_array):
#         """Filter the power_array data so it includes only decreasing gradient (so the shape is parabolic)

# Consider refactoring the method to use more vectorized NumPy operations and simplify the logic. The current implementation creates multiple intermediate arrays and uses complex nested conditions that make the code hard to understand and maintain.

# Resolve
# e:/_UNHCR/CODE/solar_unhcr/src/polyfit.py:155

# suggestion(code_refinement): Magic numbers used without clear documentation or configuration
#             return None, None

#         # IN GENERAL ANLGE MUST BE BETWEEN THESE VALUES
#         ANGLE_LOWER_LIMIT = 80
#         ANGLE_UPPER_LIMIT = 90

# Consider making these threshold values configurable parameters or adding clear documentation explaining their significance in the gradient filtering process.

# Suggested implementation:

#             return None, None

#         # Configurable angle thresholds for gradient filtering
#         # These values represent the acceptable range of angles for valid gradient selection
#         # Default values are set to filter out very flat or near-vertical gradients
#         angle_lower_limit = kwargs.get('angle_lower_limit', 80)
#         angle_upper_limit = kwargs.get('angle_upper_limit', 90)

# Update the subsequent code to use angle_lower_limit and angle_upper_limit instead of the hardcoded constants
# Add a docstring or comment explaining the purpose of these angle thresholds in the method
# Consider adding type hints and validation for the input parameters
# Example of further improvement in the method:

# def some_method(self, *args, **kwargs):
#     """
#     Filter gradients based on their angle.

#     Args:
#         angle_lower_limit (float, optional): Minimum acceptable angle for gradient. Defaults to 80.
#         angle_upper_limit (float, optional): Maximum acceptable angle for gradient. Defaults to 90.

#     Returns:
#         Filtered gradient data
#     """
#     angle_lower_limit = kwargs.get('angle_lower_limit', 80)
#     angle_upper_limit = kwargs.get('angle_upper_limit', 90)

#     # Validate input thresholds
#     if not (0 <= angle_lower_limit < angle_upper_limit <= 180):
#         raise ValueError("Invalid angle thresholds")
