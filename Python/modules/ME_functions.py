# import numpy as np
# import matplotlib.pyplot as plt
import re
import pandas as pd
import motionenergy as kiani_me
import sys
# sys.path.insert(0, 'dots_db/dotsDB/')
import dots_db.dotsDB.dotsDB as dDB


def map_snow_dots_params_to_kiani_dots(param_dict):
    new_dict = {
        'radius': param_dict['diameter'] / 2,
        'density': param_dict['density'],
        'size': param_dict['pixelSize'],
        'speed': param_dict['speed'],
        'coherence': param_dict['coherence'] / 100,
        'ppd': param_dict['pixelsPerDegree'],
        'framerate': 1 / param_dict['windowFrameRate'],
        'duration': param_dict['viewingDuration'],
        'moments': None, # irrelevant for now
        'seed': param_dict['randSeedBase'],
                }
    return new_dict


def compute_motion_energy_for_trials_in_db(db_file, dset_name, gp_name, trial_list, filters, append_to=None,
                                           create_dsetid=True):
    """
    Computes the motion energy (ME) for trials of the dots stimulus. An ME value is obtained for each trial and each
    timestep. Results are returned as pandas.DataFrame.

    :param db_file: full path to hdf5 file created with the dotsDB module
    :param dset_name: name of dataset inside hdf5 file (full path)
    :param gp_name: name of group inside hdf5 file (full path)
    :param trial_list: list of positive integers indicating the trials to extract
    :param filters: filters as outputted by motion_filters()
    :param append_to: pandas data frame. If None, a data frame is created, otherwise, rows are appended.
    :param create_dsetid: (bool). if True, create_dset_id() is called to fill the dataframe field.
        Otherwise use dset_name
    :return: a pandas data frame in long format with the following columns
        dsetID; filtersID; trial; time; ME; direction; coherence; density
        If append_to is not None, the inputted data frame is edited in place?
    """
    db_info = dDB.inspect_db(db_file)
    attrs_dict = dict(db_info[gp_name]['attrs'])

    trials = [dDB.extract_trial_as_3d_array(db_file, dset_name, gp_name, trial_number) for trial_number in trial_list]
    dots_energy = [kiani_me.apply_motion_energy_filters(x, filters) for x in trials]

    # list of dict that will become a data frame
    rows = []

    filters_id = create_filters_id(filters)
    if create_dsetid:
        dataset_id = create_dset_id(db_file, dset_name)
    else:
        dataset_id = dset_name

    for trial in range(len(trial_list)):
        motion_energy = dots_energy[trial].sum(axis=(0, 1))

        time_points = kiani_me.filter_grid(trials[trial].shape[2], 1 / attrs_dict['frame_rate'])
        assert len(time_points) > 0

        for time_point in range(len(time_points)):
            row_as_dict = {
                'dsetID': dataset_id,
                'filtersID': filters_id,
                'trial': trial_list[trial],
                'time': time_points[time_point],
                'ME': motion_energy[time_point],
                'direction': attrs_dict['direction'],
                'coherence': attrs_dict['coh_mean'],
                'density': attrs_dict['density']
            }
            rows.append(row_as_dict)

    if append_to is None:
        return pd.DataFrame(rows)


def create_dset_id(db_file, dset_name):
    """
    produce a shorter string from the dataset name in the hdf5 file, with info about file name, coherence and direction
    of stimulus

    :param db_file: (str) full path to hdf5 file
    :param dset_name: (str) dataset name (starting from root in hdf5 file)
    :return (str): short string encoding info about the dataset
    """
    extension_length = 3
    extension = db_file[-extension_length:]
    assert extension == '.h5'
    db_name = db_file[:-extension_length]

    direction = 'left' if 'dleft' in dset_name else 'right'

    coh_pattern = r"_c[0-9]+_"
    coh_match = re.search(coh_pattern, dset_name)
    if coh_match:
        coherence = coh_match.group(0)[2:][:-1]  # this trims the first 2 chars '_c' and the last one '_'
    else:
        raise ValueError('no coherence was found in dset_name')

    return db_name + direction + coherence


def create_filters_id(filters):
    """create string to encode filters characteristics. This uses the named tuple structure kiani_me.FilterSet"""
    filters_id = ''
    for entry in filters:
        for s in entry.shape:
            filters_id += str(s)
            filters_id += '_'
    filters_id = filters_id[:-1]  # remove last '_'
    return filters_id
