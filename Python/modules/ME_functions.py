# import numpy as np
# import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd
import motionenergy as kiani_me
import sys
# sys.path.insert(0, 'dots_db/dotsDB/')
import dots_db.dotsDB.dotsDB as dDB


def get_object_names_in_db(file_path):
    database_info = dDB.inspect_db(file_path)
    object_names = []  # list of object names in database
    idx = 0
    for l1 in database_info.keys():
        curr_d = database_info[l1]
        if (curr_d['attrs'] and curr_d['type'] == 'group') or (curr_d['type'] == 'dataset' and curr_d['shape'][0] > 0):
            object_names.append(l1)
            idx += 1
    return object_names, database_info


def get_names(restr_vals, name_list):
    """
    This function returns a tuple of lists of names.
    First list is for groups, second list is for datasets.
    The purpose is to filter only the names corresponding to the restricted values in restr_vals.
    Values in the dict restr_vals should be iterables (e.g. lists). Keys in restr_vals should be in maps.keys()
    """
    my_round = (lambda x: str(round(float(x), 1)))
    maps = {
        'subject': {i: 'subjS' + str(i) for i in [1, 2, 3, 4, 5]},
        'pcp': {k: 'probCP' + my_round(k) for k in [0, 0.2, 0.5, 0.8]},
        'coh': {0: 'coh0.0', 100: 'coh100.0', 'fcn': my_round},
        'ans': {'l': 'ansleft', 'r': 'ansright'},
        'cp': {True: 'CPyes', False: 'CPno'},
        'vd': {k: 'VD' + str(k) for k in [100, 200, 300, 400]},
        'dir': {k: '/' + k for k in ['left', 'right']}
    }

    dsets = []
    groups = []
    for name in name_list:
        keep = True
        for k, v in restr_vals.items():
            if all([maps[k][val] not in name for val in v]):
                keep = False
                break
        if keep:
            if name[-3:] == '/px':
                dsets.append(name)
            else:
                groups.append(name)
    return groups, dsets


def build_dset_def_str(ddef_dict):
    """Turns a dict defining a dataset into a string"""
    ddef = ''
    for k, v in ddef_dict.items():
        ddef += k
        for vv in v:
            ddef += str(vv)
    return ddef


def extract_list_arrays(group_names, dset_names, uniform_shape, file_path):
    """
    For given lists of groups and datasets in a dotsDB HDF5 DB, extract all the trials as numpy arrays into single list.
    :param group_names: list of groups
    :param dset_names: list of datasets
    :param uniform_shape: shape of all datasets in DB
    :return:
    """
    dots = []
    for (gs, ds) in zip(group_names, dset_names):
        try:
            arrays = [dDB.extract_trial_as_3d_array(file_path, ds, gs, rr+1) for rr in range(uniform_shape)]
            arrays = [a for a in arrays if np.size(a) > 0]  # the if condition removes the empty datasets
        except AssertionError:
            print(f'failure for dataset {ds} and group {gs}')
        else:
            dots += arrays
    return dots


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
        'moments': None,  # irrelevant for now
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


def build_me_df(database_info, group_names, dots, dset_def):
    """
    computes motion energy on a bank of trials and return results as pandas.DataFrame
    :param database_info: dict returned by dotsDB.inspect_database()
    :param group_names: list of group names
    :param dots: list of numpy arrays as returned by extract_list_arrays()
    :return: pandas.DataFrame in long format with main columns 'ME' and 'time'
    """
    # it is convenient to put the attributes in a dict format
    attrs_dicts = [dict(database_info[gname]['attrs']) for gname in group_names]
    # pprint.pprint(attrs_dicts)
    attrs_dict = attrs_dicts[0]  # pick any dict

    # filter parameters (there are more, with default values)
    ppd, framerate = attrs_dict['pixels_per_degree'], attrs_dict['frame_rate']
    filter_shape = 32, 32, 6                 # size parameter of motion_filters()
    filter_res = 1 / ppd, 1 / ppd, 1 / framerate

    # construct filters
    filters = kiani_me.motion_filters(filter_shape, filter_res)

    dots_energy = [kiani_me.apply_motion_energy_filters(x, filters) for x in dots]

    # list of dict that will become a data frame
    rows = []

    filters_id = create_filters_id(filters)

    for trial in range(len(dots_energy)):
        motion_energy = dots_energy[trial].sum(axis=(0, 1))

        time_points = kiani_me.filter_grid(dots[trial].shape[2], 1 / attrs_dict['frame_rate'])
        assert len(time_points) > 0

        for time_point in range(len(time_points)):
            row_as_dict = {
                'dsetID': build_dset_def_str(dset_def),
                'filtersID': filters_id,
                'trial': trial + 1,
                'time': time_points[time_point],
                'ME': motion_energy[time_point],
                'direction': attrs_dict['direction'],
                'coherence': attrs_dict['coh_mean'],
                'density': attrs_dict['density']
            }
            rows.append(row_as_dict)

    return pd.DataFrame(rows)
