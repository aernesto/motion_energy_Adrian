function [dots_params, frames] = reproduce_dots(session_timestamp, debug_flag)
% ARGS:
%    session_timestamp    string like '2019_11_22_13_59'
%    debug                if true, function runs very differently
% RETURNS:
%    nothing but writes a file [session_timestamp, '_dotsPositions.csv']
% DESCRIPTION:
% The goal of this script is to reproduce the dots shown to a subject in a 
% session.
% A session is uniquely identified by a timestamp of the form
% YYYY_MM_DD_HH_mm
% The dots are dumped into a csv file <timestamp>_dotsPositions.csv
%
% Algorithm:
%
% 1/ fetch FIRA .csv file corresponding to the session
%
% 2/ loop through trials:
%     a) get the seed
%     b) get all the parameters that specify the dotsDrawableDotKinetogram
% ------- up to here ok --------
%
%     c) generate the frames (and save them) WITHOUT drawing anything
%
% 3/ produce final dotsPositions.csv file

DATA_FOLDER = ['/Users/adrian/oneCP/Fall_2019/raw/', ...
    session_timestamp, '/'];
FILE_NAME = ['completed4AFCtrials_task100_date_', ...
    session_timestamp, '.csv'];
FIRA = [DATA_FOLDER, FILE_NAME];

trial_data = readtable(FIRA);

num_trials = size(trial_data); 
num_trials = num_trials(2);

if debug_flag
    num_trials = 2;
end

%trial_data(1:5,:)
frames = cell(1, num_trials);

for trial_number = 1:num_trials
    row = trial_data(trial_number, :);
    [dots_params, max_time] = extract_dots_params(row);
    
    % loop over frames
    frames{trial_number} = generate_frames(dots_params, ...
        debug_flag, max_time);
   
    % recycle old function that translates frames into a table --> .csv
end
end

function [params, real_dur] = extract_dots_params(one_row)
    params = table2struct(one_row);
    real_dur = params.dotsOff - params.dotsOn;
    params = rmfield(params, {'taskID', ...
        'trialIndex', ...
        'trialStart', ...
        'trialEnd', ...
        'RT', ...
        'cpRT', ...
        'dirChoice', ...
        'cpChoice', ...
        'dirCorrect', ...
        'cpCorrect', ...
        'fixationOn', ...
        'fixationStart', ...
        'targetOn', ...
        'dotsOn', ...
        'finalCPTime', ...
        'dotsOff', ...
        'choiceTime', ...
        'cpChoiceTime', ...
        'blankScreen', ...
        'feedbackOn', ...
        'subject', ...
        'date', ...
        'probCP', ...
        'cpScreenOn', ...
        'dummyBlank'});
    
    params.density = 150;
    params.speed = 5;
    params.pixelSize = 6;
    params.diameter = 8;
    params.coherenceSTD = 10;
    params.stencilNumber = 1;
    params.recordDotsPositions = true;
    params.isVisible = 0;
end

function frame_3d_matrix = generate_frames(params_struct, debug_flag, time_max)
    if debug_flag
        dots = dotsDrawableDotKinetogramDebug(params_struct);
    else
        dots = dotsDrawableDotKinetogramDebug(params_struct);
    end

    % loop through time/frame
    i = 0;
    curr_time = 0;  % stimulus onset  
    dots.prepare_to_virtually_draw(60);
    while curr_time < time_max
        i = i + 1;
        
        % use curr_time to check for CP!
        dots.computeNextFrame();
        
        curr_time = curr_time + 1 / 60;
    end
    frame_3d_matrix = dots.dotsPositions;
end