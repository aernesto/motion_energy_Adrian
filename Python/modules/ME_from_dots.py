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

    # """
    # Note the precaution I take below to ensure labeled dots file doesn't exist.
    # """
    # labeled_dots_filename = DOTS_LABELED_FOLDER + 'dots_labeled_' + timestamp + '.csv'
    # if os.path.exists(labeled_dots_filename):
    #     raise ValueError('Labeled dots file already exists')

    # first arg needs to be an iterable
    dots = basic_func.label_dots((timestamp,), DOTS_POSITIONS_FOLDER, return_df=True)

    gb = dots.groupby('trialEnd')

    # todo: any chance I can short-circuit the HDF5 storage step?
    # write dots to HDF5 file
    h5_filename = DOTS_LABELED_FOLDER + timestamp + '.h5'

    # Recall func is called twice the first time!
    _ = gb.apply(basic_func.write_dots_to_file, h5_filename)

    # need to go in manually and delete the first entry in the dataset corresponding to
    # the first group element gb.groups.keys()[0]
    single_row = dots[dots['trialEnd'] == list(gb.groups.keys())[0]]
    pb_dset_name, vals = basic_func.get_group_name(single_row)
    pb_dset_name += '/px'
    f = h5py.File(h5_filename, 'r+')  # read/write
    d = f[pb_dset_name]
    d = d[1:]  # override first trial
    f.__delitem__(pb_dset_name)
    f[pb_dset_name] = d
    f.close()

    # todo: get the rest of the script right
    # Now, we need to compute motion energy
    left_aligned, right_aligned = my_me.extract_me_full_database(h5_filename)

    # and write it to file
    left_aligned.to_csv(
        DOTS_LABELED_FOLDER + timestamp + '_left_aligned_motion_energy.csv',
        index=False
    )
    right_aligned.to_csv(
        DOTS_LABELED_FOLDER + timestamp + '_right_aligned_motion_energy.csv',
        index=False
    )
