# import numpy as np
import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd
import motionenergy as kiani_me
import sys
# sys.path.insert(0, 'dots_db/dotsDB/')
import dots_db.dotsDB.dotsDB as dDB


def plot_cyl(db_info, fixed_length, cylinders, object_names, path_to_file, cyl_number,
             plot=True, return_series=False, w=16, h=5, real=True):
    tuple_cyl, replot = cylinders[cyl_number]
    cyl = build_cyl(tuple_cyl)
    if plot and replot:
        plt.rcParams["figure.figsize"] = (w, h)  # (w, h) # figure size
        if real:
            d = compute_me_diff(cyl, object_names, fixed_length, db_info, path_to_file)
        else:
            d = compute_artificial_dm_kernels(cyl, object_names, fixed_length, db_info, path_to_file)
        plt.plot(d)
        plt.ylabel('Delta ME (R-L)')
        plt.xlabel('time (s)')
        plt.title('cyl' + str(cyl_number) + print_cyl(cyl))
        plt.show()
        if return_series:
            return d
    else:
        if return_series:
            if real:
                return compute_me_diff(cyl, object_names, fixed_length, db_info)
            else:
                return compute_artificial_dm_kernels(cyl, object_names, fixed_length, db_info, path_to_file)
        else:
            print(f'nothing was done as plot={plot} and return_series={return_series}')


def print_cyl(cyl):
    base = ''
    for k, v in cyl.items():
        base += k + ':'
        for vv in v:
            base += str(vv) + '-'
        base = base[:-1]  # delete trailing -
        base += ' '
    return base


def build_cyl(cyl_tuple):
    n = len(cyl_tuple)
    keys = [cyl_tuple[i] for i in range(n) if not i % 2]  # even-index entries
    values = [cyl_tuple[i] for i in range(n) if i % 2]  # odd-index entries
    return dict([(keys[i], values[i]) for i in range(n // 2)])


def get_dots_from_cylinder(cylinder, object_names, uniform_shape, file_path, side):
    curr_cylinder = cylinder.copy()
    curr_cylinder['ans'] = side[0]

    group_names, dset_names = get_names(curr_cylinder, object_names)

    return extract_list_arrays(group_names, dset_names, uniform_shape, file_path), group_names, curr_cylinder


def compute_me_diff(cylinder, object_names, uniform_shape, database_info, file_path):
    """
    A cylinder looks like this:
    cylinder = {'coh': [0], 'vd': [400], 'cp': [False]}
    """
    r_dots, r_group_names, r_cylinder = get_dots_from_cylinder(cylinder, object_names, uniform_shape, file_path,
                                                               'right')
    l_dots, l_group_names, l_cylinder = get_dots_from_cylinder(cylinder, object_names, uniform_shape, file_path, 'left')

    # truncate to minimum number of frames (left time-alignment)
    min_num_frames = min(min(r_k.shape[2], l_k.shape[2]) for r_k, l_k in zip(r_dots, l_dots))

    r_dots = [d[:, :, :min_num_frames] for d in r_dots]
    l_dots = [d[:, :, :min_num_frames] for d in l_dots]

    r_agg_df = build_me_df(database_info, r_group_names, r_dots, r_cylinder)
    l_agg_df = build_me_df(database_info, l_group_names, l_dots, l_cylinder)

    righties = r_agg_df.groupby('time').mean()
    lefties = l_agg_df.groupby('time').mean()

    final = righties['ME'] - lefties['ME']
    return final


def artificial_decide(df, cp_time):
    """
    this function is meant to be used within a pandas.core.GroupBy.apply() call
    :param df: a pandas.DataFrame with two columns named 'ME' and 'time'. Time is in seconds. Should only contain data
        about a single trial
    :param cp_time: theoretical time of a potential CP in seconds.
    :return: a tuple of strings representing the decisions about direction of motion in the last
        epoch ('left' vs 'right') and presence or absence of a CP ('CP' vs 'noCP').
    """
    first_epoch_df = df[df['time'] <= cp_time]
    first_epoch_me = first_epoch_df['ME'].mean()

    if df['time'].max() > cp_time:
        second_epoch_df = df[df['time'] > cp_time]
        second_epoch_me = second_epoch_df['ME'].mean()
        # Add two choice columns
        df['cp_choice'] = 'CP' if first_epoch_me * second_epoch_me < 0 else 'noCP'
        df['dir_choice'] = 'right' if second_epoch_me > 0 else 'left'
    else:
        df['cp_choice'] = 'noCP'  # perfect knowledge of time assumed
        df['dir_choice'] = 'right' if first_epoch_me > 0 else 'left'

    return df


def compute_artificial_dm_kernels(cylinder, object_names, uniform_shape, database_info, file_path):
    """
    A cylinder looks like this:
    cylinder = {'coh': [0], 'vd': [400], 'cp': [False]}
    """
    r_dots, r_group_names, r_cylinder = get_dots_from_cylinder(cylinder, object_names, uniform_shape, file_path,
                                                               'right')
    l_dots, l_group_names, l_cylinder = get_dots_from_cylinder(cylinder, object_names, uniform_shape, file_path, 'left')

    # truncate to minimum number of frames (left time-alignment)
    min_num_frames = min(min(r_k.shape[2], l_k.shape[2]) for r_k, l_k in zip(r_dots, l_dots))

    r_dots = [d[:, :, :min_num_frames] for d in r_dots]
    l_dots = [d[:, :, :min_num_frames] for d in l_dots]

    all_dots = r_dots + l_dots

    agg_df = build_me_df(database_info, r_group_names, all_dots, cylinder)  # group names passed do not matter

    # compute artificial decision
    agg_df = agg_df.groupby('trial').apply(artificial_decide, 0.2)

    righties = agg_df[agg_df['dir_choice'] == 'right'].groupby('time').mean()
    lefties = agg_df[agg_df['dir_choice'] == 'left'].groupby('time').mean()

    # final might well contain only NaN values, if 0 trials with a particular choice appear
    final = righties['ME'] - lefties['ME']
    return final


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
        'subject': {i: 'subj' + str(i) for i in range(10, 10+50)},
        'pcp': {k: 'probCP' + my_round(k) for k in [0.3, 0.7]},
        'coh': {0: 'coh0', 100: 'coh100', 'fcn': my_round},
        'ans': {'l': 'ansleft', 'r': 'ansright'},
        'cp': {True: 'CPyes', False: 'CPno'},
        'vd': {k: 'VD' + str(k) for k in [100, 200, 250, 300, 400, 600]},
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
    :param file_path: full local path to .h5 file
    :return: list of numpy arrays
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
        If append_to is not None, data is appended to the append_to data frame (returns a copy)
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
    else:
        return pd.concat([append_to, pd.DataFrame(rows)], ignore_index=True)


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
