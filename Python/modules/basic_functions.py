import h5py
import pandas as pd
import numpy as np
import os
import dots_db.dotsDB.dotsDB as ddb


def label_dots(timestamps, data_folder, return_df=False, global_labeled_dots_filename=None):
    """
    fetches dots data outputted by MATLAB (the _dotsPositions.csv files) for specified session timestamps, adds
    relevant fira data (join operation) and appends resulting 'labeled_dots' dataframe to the 
    global_labeled_dots_filename.
    :param timestamps: list or tuple of strings of the form '2019_11_05_16_19'
    :param data_folder: string with path to folder '.../raw/' where fira and dotsPositions .csv data reside.
    :param return_df: (bool) If True, a pandas.DataFrame is returned
    :param global_labeled_dots_filename: string with full path and filename for global .csv file to write to.
                                         If None, no file is written.
    :return: Either a pandas.DataFrame or None. Might also write to file depending on arg.
    """
    list_of_labeled_dots_dataframes = []
    for ts in timestamps:
        folder = data_folder + ts + '/'
        fira = pd.read_csv(folder + 'completed4AFCtrials_task100_date_' + ts + '.csv')
        dots = pd.read_csv(folder + ts + '_dotsPositions.csv')
        dots = dots[dots['isActive'] == 1]
        del dots['isActive'], dots['taskID'], dots['isCoherent']
        try:
            assert fira.index.min() == 0 and fira.index.max() == 819 and len(fira.index) == 820
            assert dots['trialIx'].min() == 0 and dots['trialIx'].max() == 819
        except AssertionError:
            print(f'assert failed with timestamp {ts}')
            continue
        labeled_dots = dots.join(fira, on="trialIx")
        labeled_dots['trueVD'] = labeled_dots['dotsOff'] - labeled_dots['dotsOn']
        labeled_dots['presenceCP'] = labeled_dots['reversal'] > 0
        to_drop = ['trialIndex', 'RT', 'cpRT', 'dirCorrect', 'cpCorrect',
                   'randSeedBase', 'fixationOn', 'fixationStart', 'targetOn',
                   'choiceTime', 'cpChoiceTime', 'blankScreen', 'feedbackOn',
                   'cpScreenOn', 'dummyBlank', 'finalDuration', 'dotsOn', 'dotsOff']
        labeled_dots.drop(columns=to_drop, inplace=True)
        to_rename = {
            'duration': 'viewingDuration',
            'direction': 'initDirection',
        }
        labeled_dots.rename(columns=to_rename, inplace=True)
        labeled_dots.dropna(subset=['dirChoice'], inplace=True)
        list_of_labeled_dots_dataframes.append(labeled_dots)
        
    # only proceed if list of dataframes is not empty
    if list_of_labeled_dots_dataframes:
        full_labeled_dots = pd.concat(list_of_labeled_dots_dataframes)
        if global_labeled_dots_filename:  # kwarg is not None
            if os.path.exists(global_labeled_dots_filename):  # file already exists --> append data
                full_labeled_dots.to_csv(global_labeled_dots_filename, index=False, mode='a+', header=False)
            else:  # file doesn't exist --> create it
                full_labeled_dots.to_csv(global_labeled_dots_filename, index=False, mode='a+', header=True)
        if return_df:  # DataFrame should be returned
            return full_labeled_dots
        else:
            return None


def inspect_csv(df):
    """df is a pandas.DataFrame"""
    print(df.head())
    print(len(df))
    print(np.unique(df['taskID']))
    try:
        print(np.unique(df['pilotID']))
    except KeyError:
        print(np.unique(df['subject']))


def get_trial_params(df):
    """coherence, viewing duration, presenceCP, direction, subject, block, probCP"""
    coh = df['coherence'].values[0]
    vd = df['viewingDuration'].values[0]
    pcp = df['presenceCP'].values[0]
    idir = df['initDirection'].values[0]
    subj = df['subject'].values[0]
    block = df['block'].values[0]
    Pcp = df['probCP'].values[0]
    return coh, vd, pcp, idir, subj, block, Pcp


def get_trial_from_dots_ts(dot_ts, trials_ts, trials_df):
    trial_dump_time = np.min(trials_ts[trials_ts>dot_ts])
    assert trial_dump_time - dot_ts < .5, 'trialEnd occurs more than 0.5 sec after seqDumpTime'
    return trials_df[trials_df['trialEnd'] == trial_dump_time]


def add_trial_params(row, t, trials):
    """
    function that adds appropriate values to trial parameter columns in dots dataframe
    :param row: row from dataframe
    :param t: dataframe with FIRA data
    :param trials: numpy array of trialEnd timestamps (scalars)
    """
    time = row['seqDumpTime']
    try:
        trial = get_trial_from_dots_ts(time, trials, t)
    except AssertionError:
        print(f'0.5 sec margin failed at row {row.name}')
        return row
    c, v, p, i, s, b, P = get_trial_params(trial)
    row['coherence'] = c
    row['viewingDuration'] = v
    row['presenceCP'] = p
    row['initDirection'] = i
    row['subject'] = s
    row['block'] = b
    row['probCP'] = P
    return row


def set_nans(df):
    if 'isActive' in df:
        del df['isActive']
    df['coherence'] = np.nan
    df['viewingDuration'] = np.nan
    df['presenceCP'] = np.nan
    df['initDirection'] = np.nan
    df['subject'] = np.nan
    df['block'] = np.nan
    df['probCP'] = np.nan
    return df


def numeric_switch_direction(init_dir):
    init_dir = int(init_dir)
    authorized = {0, 180}
    assert init_dir in authorized, f'direction argument {init_dir} should lie in {authorized}'
    (other_dir,) = {0, 180} - {init_dir}
    return other_dir


def build_trial_identifier(df):
    """
    Out of a data frame containing info for a single date and trial, builds a 22-char string used as a trial identifier
    :param df: (pandas.DataFrame) must have
            a 'trialIndex' column with a single value in the whole data frame
            a 'date' column with a single value in the whole data frame
    :return: (str) for trialIndex=3 and date=202001061405, returns '2020_01_06_14_05_00003'
    """
    trial_index = df['trialIndex'][0]
    # the following forces the string representing the integer to have at least 5 characters
    # so 3 will yield 00003 and 1000 will yield 01000, but 220001 will yield 220001
    # I need to control for string length to store as fixed-length string in HDF5 format
    index_string = f"{trial_index:05d}"
    assert len(index_string) == 5, f"trial_index {trial_index} has more than 5 digits"
    date_str = str(df['date'][0])
    date_str = '_'.join([date_str[:4], date_str[4:6], date_str[6:8], date_str[8:10], date_str[10:]])
    assert len(date_str) == 16, f"timestamp {date_str} has more than 16 characters"
    # total length of returned string should be 16 + 1 + 5 = 22
    return date_str + '_' + index_string


def get_frames(df):
    """
    get the dots data as a list of numpy arrays, as dotsDB requires them
    also returns a list of dicts, all having the keys: 'timestamp', 'coherence', 'endDirection', 'numberFramesPreCP',
    'numberFramesPostCP'. Length of the two lists are equal.

    :param df: (pandas.DataFrame) data frame containing data about a single trial only
    :return: (2-tuple) list of frames and trial_identifier (see :function:build_trial_identifier())
    """
    trial_identifier = build_trial_identifier(df)

    # (could/should probably be re-written with groupby and apply...)
    num_frames = np.max(df["frameIdx"]).astype(int)
    assert not np.isnan(num_frames), 'NaN num_frames'
    list_of_frames = []

    for fr in range(num_frames):
        frame_data = df[df["frameIdx"] == (fr+1)]
        list_of_frames.append(np.array(frame_data[['ypos', 'xpos']]))  # here I swap xpos with ypos for dotsDB
    return list_of_frames, trial_identifier


def get_group_name(df):
    """
    get the trial's parameters, and therefore the HDF5 group where the data should be appended
    """
    # get HDF5 group name

    def choice(c):
        """
        :param c: (int) either 0 for 'left' or 1 for 'right'
        :return: (str) either '/ansright' or '/ansleft'
        """
        if c == 1:
            return '/ansright'
        elif c == 0:
            return '/ansleft'
        else:
            raise ValueError(f'unexpected choice value {c}')

    def chgepoint(c):
        """
        :param c: (bool) whether the trial contains a CP or not
        :return: (str) either '/CPyes' or '/CPno'
        """
        return '/CPyes' if c else '/CPno'

    def viewdur(v):
        """
        :param v: (float or int) viewing duration in seconds
        :return: (str) e.g. '/VD200'
        """
        return '/VD' + str(int(1000*v))

    def direction(d):
        """
        :param d: (int) either 180 for left or 0 for rightward moving dots (at start of trial)
        :return: (str) either 'left' or 'right'
        """
        return 'left' if d else 'right'

    ss, pp, cc, ch, cp, vd, di, cpt = df[['subject', 'probCP', 'coherence', 'dirChoice', 'presenceCP',
                               'viewingDuration', 'initDirection', 'finalCPTime']].values[0, :]

    ss = str(ss)
    group_name = '/subj' + ss + \
                 '/probCP' + str(pp) + \
                 '/coh' + str(cc) + \
                 choice(ch) + \
                 chgepoint(cp) + \
                 viewdur(vd) + '/' + \
                 direction(di)

    vals = {'coh': cc,
            'subject': ss,  # should ss be int or str here???
            'probCP': pp,
            'dirChoice': ch,
            'presenceCP': cp,
            'viewingDuration': vd,
            'initDirection': direction(di),
            'cpTime': cpt}

    return group_name, vals


def write_dots_to_file(df, hdf5_file):
    """
    write the dots info contained in the pandas.DataFrame df to a dotsDB HDF5 file.

    :param df: (pandas.DataFrame) should only contain data about a single trial.
    :param hdf5_file: (str) full path to HDF5 file
    """
    trial_indices = df['trialIndex'].unique()
    assert len(trial_indices) == 1, f'more than 1 trialIndex: {trial_indices}'
    frames, extra_params = get_frames(df)
    gn, params = get_group_name(df)

    # exit function if number of frames too different from theoretical one
    vd = params['viewingDuration']
    num_frames = len(frames)
    if abs(num_frames-vd*60) > 5:
        tr = df['trialEnd'].values[0]
        print(f'trial with trialEnd {tr} not written; discrepancy num_frames {num_frames} and VD {vd}')
        return None

    cptime = params['cpTime'] if params['presenceCP'] else None
    parameters = dict(speed=5,
                      density=150,
                      coh_mean=params['coh'],
                      coh_stdev=10,
                      direction=params['initDirection'],
                      num_frames=np.max(df["frameIdx"]).astype(int),
                      diameter=8,
                      pixels_per_degree=(55.4612 / 2),
                      dot_size_in_pxs=3,
                      cp_time=cptime)

    stimulus = ddb.DotsStimulus(**parameters)

    try:
        ddb.write_stimulus_to_file(stimulus, 1, hdf5_file, [extra_params],
                                   pre_generated_stimulus=[frames],
                                   group_name=gn, append_to_group=True, initial_shape=50)
    except TypeError:
        print(f'group name {gn}')
        print(f'type(frames) = {type(frames)}, len(frames)= {len(frames)}, frames[0].shape = {frames[0].shape}')
        raise


def count_duplicates(dataset):
    """   
    goes through all elements in dataset and builds two objects:
    :param dataset: an h5py dataset instance. Its shape is assumed to be of the 
        form (N,) and each entry is an ndarray of bools.
    :returns: a dict 'seen' and a list 'dupes'. The dict has as keys 
        the unique elements from the dataset and as values their counts.
        The list has unique duplicated elements
    """
    seen = {}
    dupes = []

    for x in dataset:
        x = tuple(x)
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                dupes.append(x)
            seen[x] += 1
    return seen, dupes


def extract_keys(name):
    """
    example names are:
    subj13/probCP0.7/coh100/ansright/CPno/VD300/right/px
    subj13/probCP0.7/coh53/ansright/CPyes/VD300/right/px
    subj11/probCP0.7/coh100/ansleft/CPyes/VD250/left/px

    recall
        (fira['subject'] == 10) & (fira['probCP'] == 0.7) & (fira['coherence'] == 61) \
    & (fira['dirChoice'] == 0) & (fira['reversal'] == 0.2) & (fira['duration'] == .4) & \
    (fira['direction'] == 0)
    """
    items = name.split('/')
    subject = int(items[0][4:])
    probCP = round(float(items[1][6:]), 1)
    coh = int(items[2][3:])
    dir_choice = 1 if items[3][3:] == 'right' else 0
    cp_time = 0.0 if items[4][2:] == 'no' else 0.2
    vd = round(float(items[5][2:]) / 1000, 2)
    init_dir = 0 if items[6] == 'right' else 180
    return subject, probCP, coh, dir_choice, cp_time, vd, init_dir


def count_h5(item_counts):
    """
    :param item_counts: a dict with keys being very long tuples of boolean entries and values being the number
        of occurrences of such trial in the h5py dataset
    """
    total_count = 0
    for i in item_counts:
        if any(i):
            total_count += item_counts[i]
    return total_count


def count_trials_fira(dset_name, fira_df):
    if dset_name[0] == '/':
        dset_name = dset_name[1:]
    subj, pcp, coh, choice, cptime, dur, direction = extract_keys(dset_name)
    df = fira_df[
        (fira_df['subject'] == subj) &
        (fira_df['probCP'] == pcp) &
        (fira_df['coherence'] == coh) &
        (fira_df['dirChoice'] == choice) &
        (fira_df['reversal'] == cptime) &
        (fira_df['duration'] == dur) &
        (fira_df['direction'] == direction)
    ]
    return len(df)


def count_trials_dots(dset_name, dots_df):
    if dset_name[0] == '/':
        dset_name = dset_name[1:]
    subj, pcp, coh, choice, cptime, dur, direction = extract_keys(dset_name)
    particular_dset = dots_df[
        (dots_df['subject'] == subj) &
        (dots_df['probCP'] == pcp) &
        (dots_df['coherence'] == coh) &
        (dots_df['dirChoice'] == choice) &
        (dots_df['reversal'] == cptime) &
        (dots_df['viewingDuration'] == dur) &
        (dots_df['initDirection'] == direction)
    ]
    return len(particular_dset['trialIx'].unique())



