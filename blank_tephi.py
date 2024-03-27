import matplotlib.pyplot as plt
import tephi
from datetime import datetime
from siphon.simplewebservice.wyoming import WyomingUpperAir


CONST_G = 9.81
CONST_R = 287
CONST_K = 273.15


class Dataset:
    def __init__(self, p_data, t_data, color, label, group):
        self.data = zip(p_data, t_data)
        self.color = color
        self.label = label
        self.group = group


def calc_standard_temp(p):
    if p > 226:
        t0 = 288
        p0 = 1000
        DALR= 0.0065
        altitude = (t0/DALR)*(1-((p/p0)**(CONST_R*DALR/CONST_G)))
        return (t0-CONST_K) - (altitude*DALR)
    else:
        return -56.5


def plot_tephi(data_list, title, group_list):
    #tephi.MIXING_RATIO_LINE.update({'color': 'purple', 'linewidth': 0, 'linestyle': None})
    #tephi.MIXING_RATIO_TEXT.update({"size": 0})
    #tephi.WET_ADIABAT_LINE.update({'color': 'purple', 'linewidth': 0, 'linestyle': None})
    #tephi.WET_ADIABAT_TEXT.update({"size": 0})
    tephi.ISOBAR_LINE.update({'color': 'gray'})
    tephi.ISOBAR_TEXT.update({'color': 'gray', 'size': 12})
    tpg = tephi.Tephigram(isotherm_locator=tephi.Locator(20), dry_adiabat_locator=tephi.Locator(20))
    for idx, data in enumerate(data_list):
        if data.group in group_list:
            tpg.plot(data.data, label=data.label, linewidth=3, color=data.color, linestyle=None, marker=None)
        else:
            tpg.plot(data.data, linewidth=0, color='white', linestyle=None, marker=None)
    plt.title(title, fontsize=24)
    plt.yticks(fontsize=35)
    plt.savefig(title+".jpg", dpi=150)
    plt.close('all')

####################################################
# Create a datetime object for the sounding and string of the station identifier.
date = datetime(2024, 3, 27, 12)
station = '03808'

df = WyomingUpperAir.request_data(date, station)

sonde_pressure = [p for p in df['pressure'].tolist() if p > 100]
sonde_temperature = df['temperature'].tolist()
sonde_td = df['dewpoint'].tolist()



std_pressures = [*range(1000, 50, -50)]
std_temperatures = [calc_standard_temp(pressure) for pressure in std_pressures]

pressures = [1000, 500]
span_profile = Dataset([1000., 100], [-20., -50.], '', '', 0)
standard_profile = Dataset(std_pressures, std_temperatures, 'red', '1976 Standard Atmosphere', 1)
sonde_profile = Dataset(sonde_pressure, sonde_temperature, 'red', 'TEMPERATURE', 5)
sonde_profile_td = Dataset(sonde_pressure, sonde_td, 'blue', 'DEWPOINT', 5)
isobar_1000 = Dataset([pressures[0]]*6, [*range(-20, 50, 10)], 'red', '1000 mb', 2)
isobar_500 = Dataset([pressures[1]]*6, [*range(-40, 30, 10)], 'blue', '500 mb', 2)
isotherm_15 = Dataset(pressures, [15]*2, 'red', '15 degC', 3)
isotherm_n20 = Dataset(pressures, [-20]*2, 'blue', '-20 degC', 3)
entropy_15 = Dataset(pressures, [tephi.transforms.convert_pt2pT(press, 15)[1] for press in pressures], 'red', '15 degC', 4)
entropy_40 = Dataset(pressures, [tephi.transforms.convert_pt2pT(press, 40)[1] for press in pressures], 'blue', '40 degC', 4)

plot_list = [span_profile, standard_profile, isobar_1000, isobar_500, isotherm_15, isotherm_n20, entropy_15, entropy_40, sonde_profile, sonde_profile_td]
#plot_tephi(plot_list, 'BLANK', [])
#plot_tephi(plot_list, 'STANDARD ATMOSPHERE', [1])
#plot_tephi(plot_list, 'ISOBARS', [2])
#plot_tephi(plot_list, 'ISOTHERMS', [3])
#plot_tephi(plot_list, 'ISENTROPES', [4])
plot_tephi(plot_list, 'CAMBORNE_20240327_12Z_2', [5])
