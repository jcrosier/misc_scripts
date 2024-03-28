import matplotlib.pyplot as plt
import tephi
import time
import copy
from datetime import datetime
from siphon.simplewebservice.wyoming import WyomingUpperAir


CONST_G = 9.81
CONST_R = 287
CONST_K = 273.15


sites = {'names': ['CAMBORNE', 'BARROW', 'MIAMI', 'BECHAR', 'MCMURDO'],
             'ids': ['03808', '70026', '72202', '60571', '89664']}
date = datetime(2024, 3, 26, 00)


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
    tephi.MIXING_RATIO_LINE.update({'color': 'purple', 'linewidth': 0, 'linestyle': None})
    tephi.MIXING_RATIO_TEXT.update({"size": 0})
    tephi.WET_ADIABAT_LINE.update({'color': 'purple', 'linewidth': 0, 'linestyle': None})
    tephi.WET_ADIABAT_TEXT.update({"size": 0})
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


def plot_it(data_list, sites, num, date):
    df_camborne = data_list[0]
    df_barrow = data_list[1]
    df_miami = data_list[2]
    df_bechar = data_list[3]
    df_mcmurdo = data_list[4]

    camborne_T = Dataset([p for p in df_camborne['pressure'].tolist() if p > 100], df_camborne['temperature'].tolist(), 'red', 'TEMPERATURE', 0)
    camborne_Td = Dataset([p for p in df_camborne['pressure'].tolist() if p > 100], df_camborne['dewpoint'].tolist(), 'blue', 'DEWPOINT', 0)

    barrow_T = Dataset([p for p in df_barrow['pressure'].tolist() if p > 100], df_barrow['temperature'].tolist(), 'red', 'TEMPERATURE', 1)
    barrow_Td = Dataset([p for p in df_barrow['pressure'].tolist() if p > 100], df_barrow['dewpoint'].tolist(), 'blue', 'DEWPOINT', 1)

    miami_T = Dataset([p for p in df_miami['pressure'].tolist() if p > 100], df_miami['temperature'].tolist(), 'red', 'TEMPERATURE', 2)
    miami_Td = Dataset([p for p in df_miami['pressure'].tolist() if p > 100], df_miami['dewpoint'].tolist(), 'blue', 'DEWPOINT', 2)

    bechar_T = Dataset([p for p in df_bechar['pressure'].tolist() if p > 100], df_bechar['temperature'].tolist(), 'red', 'TEMPERATURE', 3)
    bechar_Td = Dataset([p for p in df_bechar['pressure'].tolist() if p > 100], df_bechar['dewpoint'].tolist(), 'blue', 'DEWPOINT', 3)

    mcmurdo_T = Dataset([p for p in df_mcmurdo['pressure'].tolist() if p > 100], df_mcmurdo['temperature'].tolist(), 'red', 'TEMPERATURE', 4)
    mcmurdo_Td = Dataset([p for p in df_mcmurdo['pressure'].tolist() if p > 100], df_mcmurdo['dewpoint'].tolist(), 'blue', 'DEWPOINT', 4)

    plot_list = [camborne_Td, camborne_T, barrow_Td, barrow_T, miami_Td, miami_T, bechar_Td, bechar_T, mcmurdo_Td, mcmurdo_T]
    time_string = date.strftime("%Y%m%d_%H")
    plot_tephi(plot_list, sites['names'][num]+'_'+time_string, [num])

def download_list(sites_dictionary, date):
    data = []
    pos = 0
    num = len(sites_dictionary['ids'])
    print('hello')
    while True:
        site_id = sites_dictionary['ids'][pos]
        try:
            new_list = copy.deepcopy(WyomingUpperAir.request_data(date, site_id))
        except:
            time.sleep(0.1)
        else:
            data.append(new_list)
            pos += 1
        if pos == num:
            break

    return data


def plot_all(datasets, sites, date):
    num = len(datasets)
    for i in range(num):
        plot_it(datasets, sites, i, date)


datasets = download_list(sites, date)
plot_all(datasets, sites, date)