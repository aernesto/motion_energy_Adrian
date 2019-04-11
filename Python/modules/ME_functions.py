# import numpy as np
# import matplotlib.pyplot as plt
import pandas as pd
import motionenergy as kiani_me
import sys
sys.path.insert(0, 'dots_db/dotsDB/')
import dotsDB as ddb


def map_snow_dots_params_to_kiani_dots(param_dict):
    new_dict = {}
    new_dict['radius'] = param_dict['diameter'] / 2
    new_dict['density'] = param_dict['density']
    new_dict['size'] = param_dict['pixelSize']
    new_dict['speed'] = param_dict['speed']
    new_dict['coherence'] = param_dict['coherence'] / 100
    new_dict['ppd'] = param_dict['pixelsPerDegree']
    new_dict['framerate'] = 1 / param_dict['windowFrameRate']
    new_dict['duration'] = param_dict['viewingDuration']
    new_dict['moments'] = None # irrelevant for now
    new_dict['seed'] = param_dict['randSeedBase']
    return new_dict


def compute_motion_energy_for_trials_in_db(db_file, dset_name, gp_name, trial_list, filters, append_to=None):
    """

    :param db_file: full path to hdf5 file created with the dotsDB module
    :param dset_name: name of dataset inside hdf5 file (full path)
    :param gp_name: name of group inside hdf5 file (full path)
    :param trial_list: list of positive integers indicating the trials to extract
    :param filters: filters as outputted by motion_filters()
    :param append_to: pandas data frame. If None, a data frame is created, otherwise, rows are appended.
    :return: a pandas data frame in long format with the following columns
        dsetID; filtersID; trial; time; ME; direction; coherence; density
        If append_to is not None, the inputted data frame is edited in place?
    """
    db_info = ddb.inspect_db(db_file)
    attrs_dict = dict(db_info[gp_name]['attrs'])

    trials = [ddb.extract_trial_as_3d_array(db_file, dset_name, gp_name, trial_number) for trial_number in trial_list]
    dots_energy = [kiani_me.apply_motion_energy_filters(x, filters) for x in trials]

    time_points = kiani_me.filter_grid(attrs_dict['num_frames'], 1 / attrs_dict['frame_rate'])
    assert len(time_points) > 0
    # the data frame to return has num_trials x num_time_points rows

    # list of dict that will become a data frame
    rows = []

    dataset_id = create_dset_id(db_file, dset_name)
    filters_id = create_filters_id(filters)

    for trial in range(len(trial_list)):
        motion_energy = dots_energy[trial].sum(axis=(0, 1))
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
    """todo: to write"""
    return ''


def create_filters_id(filters):
    """todo: to write"""
    return ''
