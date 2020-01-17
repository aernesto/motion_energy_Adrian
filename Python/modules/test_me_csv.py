"""
Script to diagnose motion energy csv file produced by ME_from_dots.py

Questions:
1/ What is the list of trial indices?
  a) in FIRA
  b) in ME file

"""

import numpy as np
import pandas as pd

TIMESTAMP = '2020_01_99_14_05' # '2020_01_06_14_05'

PROCESSED_FOLDER = '/home/adrian/SingleCP_DotsReversal/Fall2019/processed/'
ME_CSV_FILENAME = TIMESTAMP + '_motion_energy.csv'
RAW_FOLDER = '/home/adrian/SingleCP_DotsReversal/Fall2019/raw/' + TIMESTAMP + '/'
FIRA_FILENAME = 'completed4AFCtrials_task100_date_' + TIMESTAMP + '.csv'
DOTS_FILENAME = TIMESTAMP + '_dotsPositions.csv'


def is_sequence_int(seq):
    """
    :param seq: ndarray
    :return: True if seq is a sequence of integers with no gaps
    """
    real_seq = np.arange(seq.min(), seq.max() + 1)
    if seq.shape != real_seq.shape:
        return False
    return all(real_seq == seq)


def diagnose_int_sequence(seq, title=None):
    if title:
        print(title)
    print(f"min = {seq.min()}, max= {seq.max()}, len= {len(seq)}")
    if not is_sequence_int(seq):
        indices = np.arange(1, len(seq))
        differences = np.diff(seq)
        aberrant = indices[differences != 1]
        print(f"aberrant rows in ordered sequence = {aberrant}")
        for i in aberrant:
            _ = [print(f"row {ii}, trial index {seq[ii]}") for ii in range(i-1, i+1)]
            print()
    else:
        print("sequence has no aberrations")
        print()

# FIRA

fira_data = pd.read_csv(RAW_FOLDER + FIRA_FILENAME)
fira_trial_index = fira_data['trialIndex'].to_numpy(dtype=int)

diagnose_int_sequence(fira_trial_index, title='diagnose FIRA trial index')

# Motion Energy CSV
trial_indices = []
with open(PROCESSED_FOLDER + ME_CSV_FILENAME) as f:
    for row_ix, line in enumerate(f):
        if row_ix:  # skip first row
            str_timestamp = line[:22]
            trial_indices.append(int(str_timestamp[-5:]))

trial_indices = np.array(trial_indices)
trial_indices.sort()
diagnose_int_sequence(trial_indices, title='diagnostic on ME trial indices')

# dotsPositions
dots_data = pd.read_csv(RAW_FOLDER + DOTS_FILENAME)
dots_trial_index = np.unique(dots_data['trialIx'].to_numpy(dtype=int))
dots_trial_index.sort()
diagnose_int_sequence(dots_trial_index, title='diagnostic on dotsPositions trial indices')
