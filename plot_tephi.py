import os.path
import matplotlib.pyplot as plt
import tephi
import requests
import pandas
from datetime import datetime, timedelta
from siphon.simplewebservice.wyoming import WyomingUpperAir

# Number of attempts to download a file from the server
NUMBER_TRIES = 20

# Physical constants
CONST_G = 9.81
CONST_R = 287
CONST_K = 273.15

# Graphing options
P_DATA_THRESHOLD = 100
ISOBAR_INTERVAL = 100
T_INCREMENT = 20
ANCHOR = [(1000, -40), (50, -80)]   # [(P_bottom, T_bottom),(P_top, T_top)]
SIMPLE_PLOT = True


class Profile:
    def __init__(self, dataframe):
        self.T = TempDataframe(dataframe)
        self.Td = DewDataframe(dataframe)


class TimeInterval:
    def __init__(self, start, end, delta):
        self.start = start
        self.end = end
        self.delta = delta


class TempDataframe:
    def __init__(self, dataframe):
        p_data = [p for p in dataframe['pressure'].tolist() if p > P_DATA_THRESHOLD]
        self.data = zip(p_data, dataframe['temperature'].tolist())
        self.color = 'red'
        self.name = "TEMPERATURE"


class DewDataframe:
    def __init__(self, dataframe):
        p_data = [p for p in dataframe['pressure'].tolist() if p > P_DATA_THRESHOLD]
        self.data = zip(p_data, dataframe['dewpoint'].tolist())
        self.color = 'blue'
        self.name = "DEWPOINT"


class Empty:
    def __init__(self):
        self.data = zip([850], [0])
        self.color = 'white'
        self.name = ""


class Isobar:
    def __init__(self, pressure, t_start, t_end, t_delta):
        num_values = 1 + int((t_end - t_start) / t_delta)
        self.data = zip([pressure]*num_values, [*range(t_start, t_end, t_delta)])
        self.color = 'green'
        self.name = "ISOBAR " + str(pressure) + " mb"


class Isotherm:
    def __init__(self, temperature, p_start, p_end):
        self.data = zip([p_start, p_end], [temperature]*2)
        self.color = 'purple'
        self.name = "ISOTHERM " + str(temperature) + " degC"


class IsoEntropy:
    def __init__(self, theta, p_start, p_end):
        self.data = zip([p_start, p_end],
                        [tephi.transforms.convert_pt2pT(press, theta)[1] for press in [p_start, p_end]])
        self.color = 'orange'
        self.name = "ISENTROPE (constant THETA) " + str(theta) + " degC"


class StandardAtmosphere:
    def __init__(self, pressure_data):
        self.data = zip(pressure_data, [self.calc_standard_temp(pressure) for pressure in pressure_data])
        self.color = 'pink'
        self.name = "1976 STANDARD ATMOSPHERE"

    @staticmethod
    def calc_standard_temp(pressure):
        if pressure > 226:
            t0 = 288
            p0 = 1000
            lapse_rate = 0.0065
            altitude = (t0/lapse_rate)*(1-((pressure/p0)**(CONST_R*lapse_rate/CONST_G)))
            return (t0-CONST_K) - (altitude*lapse_rate)
        else:
            return -56.5


def process_batch(site_dict, dates, data_path, plot_path, save_csv=True, save_plot=True, use_local=True):

    for site_name in site_dict.keys():

        current_date = dates.start
        attempt = 0

        while True:
            profile_name = site_name + '_' + current_date.strftime('%Y%m%d_%H')

            # Check if the file already exists. If it does, skip the download process for this time interval
            if os.path.exists(data_path + profile_name + '.csv') is True and use_local:
                if save_plot:
                    df = pandas.read_csv(data_path + profile_name + '.csv')
                    data = Profile(df)
                    plot_tephi([data.T, data.Td], profile_name, plot_path)
                current_date += dates.delta
                continue

            # Try to download data from the Wyoming archive
            try:
                attempt += 1
                df = WyomingUpperAir.request_data(current_date, site_dict[site_name])
                data = Profile(df)

            # No data found for this site+time combination
            except ValueError:
                print(f'No data found for {profile_name}')
                attempt = 0
                current_date += dates.delta

            # Server is busy
            except requests.HTTPError:
                if attempt > NUMBER_TRIES:
                    print(f'Failed to download {profile_name}')
                    attempt = 0
                    current_date += dates.delta

            # Download was successful -> save the dataframe to a csv
            else:
                if save_csv:
                    df.to_csv(data_path + profile_name + '.csv')
                if save_plot:
                    plot_tephi([data.T, data.Td], profile_name, plot_path)
                current_date += dates.delta
                attempt = 0

            # Check if there are any times left to download
            finally:
                if current_date > dates.end:
                    break


def plot_tephi(data_list, name, path):

    if SIMPLE_PLOT:
        tephi.MIXING_RATIO_LINE.update({'color': 'purple', 'linewidth': 0, 'linestyle': None})
        tephi.MIXING_RATIO_TEXT.update({"size": 0})
        tephi.WET_ADIABAT_LINE.update({'color': 'purple', 'linewidth': 0, 'linestyle': None})
        tephi.WET_ADIABAT_TEXT.update({"size": 0})
    tephi.ISOBAR_LINE.update({'color': 'gray'})
    tephi.ISOBAR_TEXT.update({'color': 'gray', 'size': 12})
    tephi.ISOBAR_SPEC = [(ISOBAR_INTERVAL, None)]

    tpg = tephi.Tephigram(isotherm_locator=tephi.Locator(T_INCREMENT), dry_adiabat_locator=tephi.Locator(T_INCREMENT),
                          anchor=ANCHOR)
    for data in data_list:
        tpg.plot(data.data, label=data.name, linewidth=3, color=data.color, linestyle=None, marker=None)
    plt.title(name, fontsize=24)
    plt.yticks(fontsize=35)
    plt.savefig(path + name + ".jpg", dpi=150)
    plt.close('all')


# Example of batch downloading (Wyoming database) and plotting
# -------------------------------------------------------------
sites = {
    'BARROW': '70026',
    'MIAMI': '72202'
}
time_interval = TimeInterval(datetime(2024, 3, 20, 00), datetime(2024, 3, 21, 00), timedelta(hours=12))
process_batch(sites, time_interval, './data/', './plots/', save_csv=True, save_plot=True, use_local=True)


# Example plots for Isolines and Standard Atmosphere Model
# -------------------------------------------------------------
SAM = StandardAtmosphere([*range(1000, 50, -10)])
isobar_850 = Isobar(850, -40, 30, 10)
isotherm_m20 = Isotherm(-20, 1000, 300)
entropy_20 = IsoEntropy(20, 1000, 250)
plot_tephi([SAM, isobar_850, isotherm_m20, entropy_20], 'ISOLINES', './plots/')

# Example Blank Tephigram
# -------------------------------------------------------------
empty = Empty()
plot_tephi([empty], 'EMPTY', './plots/')
