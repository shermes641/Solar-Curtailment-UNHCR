"""
Overview
    This Python file (data_visualization.py) provides a class DataVisualization for creating visualizations of solar power data. 
    It uses the matplotlib and seaborn libraries to generate plots related to Global Horizontal Irradiance (GHI), 
    power generation, voltage, and other related metrics. 
    The class is designed to help analyze and understand the performance of solar power systems.

Key Components
    DataVisualization Class: 
        This class encapsulates the visualization logic. 
        It offers several methods for generating different types of plots.

    display_ghi(ghi, date): 
        This method displays the GHI profile for a given day. 
        It takes a Pandas DataFrame (ghi) containing GHI data and a date string (date) as input. 
        The plot shows the variation of GHI throughout the day, focusing on daylight hours (5:00 to 18:00).

    display_power_scatter(data_site, ac_cap): 
        This method creates a scatter plot showing the relationship between voltage and normalized power, 
        reactive power, and power factor. It takes a Pandas DataFrame (data_site) containing power data 
        and the AC capacity (ac_cap) of the inverter as input. 
        The plot helps visualize how these parameters vary with voltage.

    display_power_voltage(data_site, date, vwatt_response, vvar_response): 
        This method generates a plot showing the time series of actual power, expected power, 
        reactive power, power limits (if applicable), and voltage. 
        It takes a Pandas DataFrame (data_site), a date string (date), and boolean flags 
        (vwatt_response, vvar_response) indicating the presence of V-Watt and V-VAr responses as input. 
        This plot provides a comprehensive view of the power and voltage dynamics over time.

Global Parameters: 
    The file sets global parameters for font sizes and styling using matplotlib.rcParams. 
    This ensures consistent formatting across all generated plots. 
    A show boolean variable controls whether plots are displayed interactively. 
    It's currently set to False, suggesting the plots are likely saved rather than displayed directly.
"""

#IMPORT PACKAGES
import matplotlib.pyplot as plt
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

show = False

#DATA VISUALIZATION
class DataVisualization():
    """
    A class consists of methods related to data visualization

    Methods
        display_ghi : Display GHI plot of the day
        display_power_scatter : Display P/VA rated, Q/VA rated, and PF (P/VA) as a scatter plot
        display_power_voltage : Display power, reactive power, expected power, power limit due to vwatt/vvar, and voltage
        
    """
    
    def display_ghi(self, ghi, date):
        ''' Display GHI plot of the day

        Args:
            ghi(df) : ghi data of the day
            date (str): the date of the analysis

        Returns:
            None, but displaying GHI plot
        '''

        year = int(date[:4])
        month = int(date[5:7])
        day = int(date[8:10])

        ghi_plot = ghi[(ghi['HH24'] >= 5) & (ghi['HH24'] <= 18)]

        fig, ax = plt.subplots()
        fig.set_size_inches(9, 5)

        ax.plot(ghi_plot['Mean global irradiance (over 1 minute) in W/sq m'], color = 'C1', markersize = 8)
        ax.set_ylabel('GHI in W/sq m', **fontdict)
        ax.set_xlabel('Time in Day', **fontdict)

        self._extracted_from_display_power_voltage_25(year, month, day, ax)

        if show:
            plt.show()
        return plt

    def display_power_scatter(self, data_site, ac_cap):
        ''' Display P/VA rated, Q/VA rated, and PF (P/VA) as a scatter plot

        Args:
            date_site(df) : time series D-PV data
            ac_cap (int) : ac capacity of the inverter

        Returns:
            None, but displaying plot
        '''

        data_site['power_normalized'] = data_site['power'] / ac_cap
        data_site['var_normalized'] = data_site['reactive_power'] / ac_cap

        fig, ax = plt.subplots()
        fig.set_size_inches(9, 5)

        ax.scatter(data_site['voltage'], data_site['power_normalized'], color = 'r', marker = 'o', linewidths = 0.1, alpha = 1, label = 'P/VA-rated')
        ax.scatter(data_site['voltage'], data_site['var_normalized'], color = 'b', marker = 'o', linewidths = 0.1, alpha = 1, label = 'Q/VA-rated')
        ax.scatter(data_site['voltage'], data_site['pf'], color = 'g', marker = 'o', linewidths = 0.1, alpha = 1, label = 'PF')

        ax.set_xlabel('Voltage (Volt)', **fontdict)
        ax.set_ylabel('Real Power, Reactive Power, PF', **fontdict)
        ax.legend(prop={'size': 15})

        return self._extracted_from_display_power_voltage_27(ax)

    def display_power_voltage(self, data_site, date, vwatt_response, vvar_response):
        ''' Display power, reactive power, expected power, power limit due to vwatt/vvar, and voltage

        Args:
            date_site(df) : time series D-PV data
            date (str): date of analysis
            vwatt_response (str): whether there is vwatt repsonse or not
            vvar_response (str): whether there is vvar response or not

        Returns:
            None, but displaying plot
        '''

        year = int(date[:4])
        month = int(date[5:7])
        day = int(date[8:10])

        fig, ax = plt.subplots()
        fig.set_size_inches(18.5, 10.5)

        line1 = ax.plot(data_site['power'], color = 'b', label = 'Actual Power', lw = 3)
        line2 = ax.plot(data_site['power_expected'], color = 'y', label = 'Expected Power')
        line3 = ax.plot(data_site['reactive_power'], color = 'g', label = 'Reactive Power')
        ax.set_ylim([-100, 6000])

        if vwatt_response == 'Yes':
            line4 = ax.plot(data_site['power_limit_vw'], color = 'm', label = 'Power Limit V-Watt')
            #show power limit here
        elif vvar_response == 'Yes':
            line4 = ax.plot(data_site['power_limit_vv'], color = 'm', label = 'Power Limit V-VAr')

        ax.set_ylabel('Power (watt or VAr)', **fontdict)
        ax.set_xlabel('Time in Day', **fontdict)
        ax.legend(loc = 2, prop={'size': 15})

        ax2 = ax.twinx()
        line4 = ax2.plot(data_site['voltage'], color = 'r', label = 'Voltage')
        ax2.set_ylim([199, 260])
        ax2.set_ylabel('Voltage (volt)', **fontdict)
        ax2.legend(loc = 1, prop={'size': 15})

        self._extracted_from_display_power_voltage_25(year, month, day, ax)
        return self._extracted_from_display_power_voltage_27(ax2)

    # TODO Rename this here and in `display_power_scatter` and `display_power_voltage`
    def _extracted_from_display_power_voltage_27(self, arg0):
        arg0.tick_params(axis='both', which='major', labelsize=20)
        arg0.tick_params(axis='both', which='minor', labelsize=20)
        if show:
            plt.show()
        return plt

    # TODO Rename this here and in `display_ghi` and `display_power_voltage`
    def _extracted_from_display_power_voltage_25(self, year, month, day, ax):
        time_range = range(3, 10)
        labels = [f'{str(2 * i)}:00' for i in time_range]
        values = [datetime(year, month, day, 2 * i, 0) for i in time_range]
        plt.xticks(values, labels)
        ax.tick_params(axis='both', which='major', labelsize=20)
        ax.tick_params(axis='both', which='minor', labelsize=20)

### SUGGESTIONS SOURCERY
# Hey there - I've reviewed your changes - here's some feedback:

# Overall Comments:

# Consider moving global plotting parameters into the DataVisualization class to avoid potential conflicts when using the module in larger applications
# Clean up commented out code and unused imports at the top of the file
# Here's what I looked at during the review
# e:/_UNHCR/CODE/solar_unhcr/src/data_visualization.py:21

# suggestion(code_refinement): Consider making plot style configurable
# fontdict={'fontsize': FONT_SIZE, 'fontweight' : 'bold'}
# # can add in above dictionary: 'verticalalignment': 'baseline' 

# style = 'ggplot' # choose a style from the above options
# plt.style.use(style)

# Instead of hardcoding 'ggplot', consider allowing the style to be passed as a parameter or configured externally for more flexibility.

# Suggested implementation:

# style = kwargs.get('plot_style', 'ggplot')  # Allow configurable plot style with 'ggplot' as default
# plt.style.use(style)

# This change assumes the surrounding function uses **kwargs to allow flexible parameter passing
# If the function doesn't currently use **kwargs, you'll need to modify the function signature to include it
# Users can now optionally specify a different plot style when calling the function, e.g., plot_function(plot_style='seaborn')
# If no style is specified, it will default to 'ggplot' as before
# Resolve
# e:/_UNHCR/CODE/solar_unhcr/src/data_visualization.py:38

# suggestion(code_refinement): Potential time filtering could be more robust
        
#     """
    
#     def display_ghi(self, ghi, date):
#         ''' Display GHI plot of the day

# The time filtering from 5 to 18 hours seems hardcoded. Consider making the time range a configurable parameter to handle different solar tracking scenarios.

# Resolve
# e:/_UNHCR/CODE/solar_unhcr/src/data_visualization.py:94

# suggestion(code_refinement): Scatter plot could benefit from more configurable visualization
#         fig, ax = plt.subplots()
#         fig.set_size_inches(9, 5)

#         ax.scatter(data_site['voltage'], data_site['power_normalized'], color = 'r', marker = 'o', linewidths = 0.1, alpha = 1, label = 'P/VA-rated')
#         ax.scatter(data_site['voltage'], data_site['var_normalized'], color = 'b', marker = 'o', linewidths = 0.1, alpha = 1, label = 'Q/VA-rated')
#         ax.scatter(data_site['voltage'], data_site['pf'], color = 'g', marker = 'o', linewidths = 0.1, alpha = 1, label = 'PF')
# Consider adding parameters to customize scatter plot aesthetics like marker size, transparency, and color for more flexible visualization.

# Suggested implementation:

#         ax.scatter(data_site['voltage'], data_site['power_normalized'], 
#                    color='r', marker='o', 
#                    s=30,  # marker size
#                    linewidths=0.1, 
#                    alpha=1, 
#                    label='P/VA-rated', 
#                    edgecolors='black')  # optional edge color
#         ax.scatter(data_site['voltage'], data_site['var_normalized'], 
#                    color='b', marker='o', 
#                    s=30,  # marker size
#                    linewidths=0.1, 
#                    alpha=1, 
#                    label='Q/VA-rated', 
#                    edgecolors='black')  # optional edge color
#         ax.scatter(data_site['voltage'], data_site['pf'], 
#                    color='g', marker='o', 
#                    s=30,  # marker size
#                    linewidths=0.1, 
#                    alpha=1, 
#                    label='PF', 
#                    edgecolors='black')  # optional edge color

# To make this even more flexible, you could consider:

# Creating a method that allows passing custom scatter plot parameters
# Adding a configuration dictionary for plot aesthetics
# Implementing default values that can be easily overridden
# Potential future improvement would be to create a method like:

# def plot_scatter_with_options(ax, x_data, y_data, label, 
#                                color='r', 
#                                marker='o', 
#                                marker_size=30, 
#                                alpha=1, 
#                                edge_color='black'):
#     ax.scatter(x_data, y_data, 
#                color=color, 
#                marker=marker, 
#                s=marker_size, 
#                alpha=alpha, 
#                label=label, 
#                edgecolors=edge_color)
# Resolve
# e:/_UNHCR/CODE/solar_unhcr/src/data_visualization.py:137

# suggestion(bug_risk): String comparison for boolean flags is error-prone
#         line3 = ax.plot(data_site['reactive_power'], color = 'g', label = 'Reactive Power')
#         ax.set_ylim([-100, 6000])

#         if vwatt_response == 'Yes':
#             line4 = ax.plot(data_site['power_limit_vw'], color = 'm', label = 'Power Limit V-Watt')
#             #show power limit here
# Use boolean values instead of string comparisons. This makes the code more type-safe and reduces potential string-related errors.

# Resolve
# e:/_UNHCR/CODE/solar_unhcr/src/data_visualization.py:135

# suggestion(code_refinement): Hard-coded plot limits might not suit all datasets
#         line1 = ax.plot(data_site['power'], color = 'b', label = 'Actual Power', lw = 3) 
#         line2 = ax.plot(data_site['power_expected'], color = 'y', label = 'Expected Power')
#         line3 = ax.plot(data_site['reactive_power'], color = 'g', label = 'Reactive Power')
#         ax.set_ylim([-100, 6000])

#         if vwatt_response == 'Yes':
# Consider dynamically calculating y-axis limits based on the actual data range to make the visualization more adaptive.
