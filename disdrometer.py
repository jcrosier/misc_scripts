import numpy as np
import os


# create global array with D bins
# create global array with V bins
# create globals specifying cols for PSD data
# create globals specifying cols for HK data
# create globals specifying cols for timestamp data

# create function to create netcdf file
# create function to create netcdf datasets

def load_thies(fname):
    with open(fname, 'r') as file:
        for idx, line in enumerate(file):

            # first line is a header, it is not data
            if idx == 0:
                continue

            # matches telegram#4/5 packet WITH PSDs
            if len(line) == 2230:
                print('PSD', idx, len(line))

            # matches telegram#4/5 packet WITHOUT PSDs
            elif len(line) == 201:
                print('No PSD', idx, len(line))

            # unrecognised data length
            else:
                print(f'Unrecognised length for line#{idx} in {os.path.basename(fname)}')

load_thies('C:/Users/jonny/OneDrive - The University of Manchester/Research/Projects/NCAS/Disdrometers/202404220000_distrometer_1min.txt')
