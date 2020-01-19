% Example script to compute very simple reverse kernels
%%
clear
TIMESTAMP = '2020_01_07_14_09';

% where the motion_energy.csv file lies
PROCESSED_FOLDER = '/home/adrian/SingleCP_DotsReversal/Fall2019/processed/';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     IMPORTANT NOTE! 
%
% motion energy values have the wrong sign in the .csv file
% always flip the sign before processing
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ME_CSV_FILENAME = [TIMESTAMP , '_motion_energy.csv'];
path_to_me = [PROCESSED_FOLDER, ME_CSV_FILENAME];

% where the behavior .csv file lies
RAW_FOLDER = ['/home/adrian/SingleCP_DotsReversal/Fall2019/raw/' , TIMESTAMP , '/'];
FIRA_FILENAME = ['completed4AFCtrials_task100_date_' , TIMESTAMP , '.csv'];
path_to_fira = [RAW_FOLDER, FIRA_FILENAME];

% load data
fira_table = readtable(path_to_fira);
me_table = readtable(path_to_me);
% extract vector of time points for motion energy
times = me_table{1,2:end};

% produce a few plots of motion energy on single trials, just by reading
% off arbitrary rows of the motion energy table
for me_row=692:697
    figure(me_row)
    plot(times, me_table{me_row,2:end})
    trialID = me_table{me_row,1}{1};
    trial_index = get_trialIndex_from_trialID(trialID);
    title(build_description(fira_table, trial_index))
    ylabel('ME')
    xlabel('time (s)')
    xlim([0,.65])
    hold on
    cptime = fira_table(fira_table.trialIndex == trial_index,:).finalCPTime;
    if not(isnan(cptime))
        plot([cptime, cptime], [-50,50], 'r')
    end
    hold off
end

%%
% Compute a kernel by 
% 1/ fixing nominal stimulus conditions
% 2/ averaging ME across trials with the same nominal conditions
nominal_conditions.dirChoice = 'left';  % options = 'right', 'left', 'any'
nominal_conditions.coherence = 0;
nominal_conditions.endDir = 'any'; % options = 'right', 'left', 'any'
nominal_conditions.duration = 0.4;
nominal_conditions.CP = 'any';
[kk, num_trials, trialIDs] = compute_kernel(nominal_conditions, fira_table, me_table);
disp('trial IDs used in kernel')
trialIDs
%figure()
plot(times, kk)
text(.5,.1,[num2str(num_trials), ' trials'], 'Units', 'normalized');
title(nominal_conditions2title(nominal_conditions));
xlabel('time (s)')
ylabel('AVG ME')
