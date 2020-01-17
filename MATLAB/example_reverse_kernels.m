% Example script to compute very simple reverse kernels
clear
TIMESTAMP = '2020_01_07_14_09';

PROCESSED_FOLDER = '/home/adrian/SingleCP_DotsReversal/Fall2019/processed/';
ME_CSV_FILENAME = [TIMESTAMP , '_motion_energy.csv'];
RAW_FOLDER = ['/home/adrian/SingleCP_DotsReversal/Fall2019/raw/' , TIMESTAMP , '/'];
FIRA_FILENAME = ['completed4AFCtrials_task100_date_' , TIMESTAMP , '.csv'];
DOTS_FILENAME = [TIMESTAMP , '_dotsPositions.csv'];
ME_ROW = 499;  % random row from ME CSV file to plot (should be > 1)

path_to_fira = [RAW_FOLDER, FIRA_FILENAME];
path_to_me = [PROCESSED_FOLDER, ME_CSV_FILENAME];

fira_table = readtable(path_to_fira);
me_table = readtable(path_to_me);
times = me_table{1,2:end};

%figure()
plot(times, me_table{ME_ROW,2:end})
trialID = me_table{ME_ROW,1}{1};
trial_index = get_trialIndex_from_trialID(trialID);
title(build_description(fira_table, trial_index))
xlabel('time (s)')
xlim([0,.65])
hold on
cptime = fira_table(fira_table.trialIndex == trial_index,:).finalCPTime;
if not(isnan(cptime))
    plot([cptime, cptime], [-50,50], 'r')
end
hold off