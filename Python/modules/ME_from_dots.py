"""
This module is designed to take as input a '_dotsPositions.csv' file (itself found
from a timestamp argument) and output two '*_ME_df.csv' files, where * is either
'left_aligned' or 'right_aligned'.
"""

import sys
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import pprint
# import seaborn as sns
import h5py
import os.path

# add location of custom modules to path
# sys.path.insert(0, '../modules/')
# sys.path.insert(0, '../modules/dots_db/dotsDB/')

# custom modules
# import dotsDB as ddb
# import motionenergy as kiani_me
# import stimulus as stim
import ME_functions as my_me
import basic_functions as basic_func

FILTER_SHAPE = (32, 32, 6)
# shape of the filters used to compute motion energy in my_me.create_filters()

# full local path to folder where labeled_dots*.csv and *ME_df.csv files will be written
DOTS_LABELED_FOLDER = '/home/adrian/SingleCP_DotsReversal/Fall2019/processed/'

# full local path to folder where FIRA and dotsPositions.csv files reside
DOTS_POSITIONS_FOLDER = '/home/adrian/SingleCP_DotsReversal/Fall2019/raw/'

if __name__ == '__main__':
    """
    When called from the command line, the unique compulsory argument is the timestamp 
    of an existing session for which the '_dotsPositions.csv' file exists. 
    """
    if len(sys.argv) != 2:
        raise ValueError('Unique argument allowed: timestamp "YYYY_MM_DD_HH_mm" of an' +
                         'existing session for which the dotsPositions.csv file exists')
    timestamp = sys.argv[1]

    h5_filename = DOTS_LABELED_FOLDER + 'dotsDB_' + timestamp + '.h5'

    # only process the dotsPositions file if the corresponding HDF5 doesn't exist
    if not os.path.exists(h5_filename):
        try:
            # display some info for user
            print()
            print(f'Starting the processing of *dotsPositions.csv file with timestamp {timestamp}')

            # first arg needs to be an iterable
            dots = basic_func.label_dots((timestamp,), DOTS_POSITIONS_FOLDER, return_df=True)

            gb = dots.groupby('trialEnd')
            # write dots to HDF5 file
            print(f'About to create file {h5_filename}')
            _ = gb.apply(basic_func.write_dots_to_file, h5_filename)
        except AssertionError:
            os.remove(h5_filename)
            raise

        # Recall func is called twice the first time!
        # need to go in manually and delete the first entry in the dataset corresponding to
        # the first group element gb.groups.keys()[0]
        single_row = dots[dots['trialEnd'] == list(gb.groups.keys())[0]]
        gname, vals = basic_func.get_group_name(single_row)
        pb_dset_name = gname + '/px'
        pb_pdset_name = gname + '/paramdset'

        f = h5py.File(h5_filename, 'r+')  # read/write
        d = f[pb_dset_name]
        pdset = f[pb_pdset_name]
        d = d[1:]  # override first trial
        pdset = pdset[1:]
        f.__delitem__(pb_dset_name)
        f.__delitem__(pb_pdset_name)
        f[pb_dset_name] = d
        f[pb_pdset_name] = pdset
        f.close()

    # Now, we need to compute motion energy
    motion_energy = my_me.extract_me_full_database(h5_filename, shape_of_filters=FILTER_SHAPE)

    # and write it to file
    motion_energy.to_csv(
        DOTS_LABELED_FOLDER + timestamp + '_motion_energy.csv',
        index=False
    )
