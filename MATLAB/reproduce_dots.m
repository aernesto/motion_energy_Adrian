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
DOTS = [DATA_FOLDER, session_timestamp, '_dotsPositions.csv'];
disp(DOTS)

trial_data = readtable(FIRA);

num_trials = size(trial_data); 
num_trials = num_trials(2);

if debug_flag
    num_trials = 2;
end

%trial_data(1:5,:)
frames = cell(1, num_trials);
dotsColNames = {...
    'xpos', ...
    'ypos', ...
    'isActive', ...
    'isCoherent', ...
    'frameIdx', ...
    'taskID'};

fullMatrix = zeros(0,length(dotsColNames));
end_block = 0;

for trial_number = 1:num_trials
    row = trial_data(trial_number, :);
    [dots_params, max_time] = extract_dots_params(row);
    
    % loop over frames
    dotsPositions = generate_frames(dots_params, max_time);
    frames{trial_number} = dotsPositions;
    
    % recycle old function that translates frames into a table --> .csv
    numDotsFrames = size(dotsPositions,3);
    
    for frame = 1:numDotsFrames
        numDots = size(dotsPositions,2);
        
        start_block = end_block + 1;
        end_block = start_block + numDots - 1;
        
        fullMatrix(start_block:end_block,:) = [...
            squeeze(dotsPositions(:, :, frame)'),...
            repmat([frame, 100], numDots, 1)];
    end
end

U=array2table(fullMatrix, 'VariableNames', dotsColNames);
writetable(U, DOTS, 'WriteRowNames',true)
disp('dots written')
end

function [params, real_dur] = extract_dots_params(one_row)
% get dots stimulus parameter from table's single row
    params = table2struct(one_row);
    real_dur = params.dotsOff - params.dotsOn;
    params = rmfield(params, { ...
        'taskID', ...
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

function frame_3d_matrix = generate_frames(params_struct, ...
    time_max)
% get dotsPositions 3D matrix from dotsDrawableDotKinetogramDebug's trial
    reversal_time = params_struct.finalCPTime;
    if isnan(reversal_time) || (reversal_time == 0)
        reversal_time = inf;
    end
    
    dots = dotsDrawableDotKinetogramDebug(params_struct);

    function dd = flip_direction(d)
        if d == 180
            dd = 0;
        else
            dd = 180;
        end
    end

    % loop through time/frame
    i = 0;
    curr_time = 0;  % stimulus onset  
    dots.prepare_to_virtually_draw(60);
    has_switched = false;
    while curr_time < time_max
        i = i + 1;
        % use curr_time to check for CP!
        if (curr_time > reversal_time) && ~has_switched
            dots.direction = flip_direction(dots.direction);
            has_switched = true;
        end
        dots.computeNextFrame();
        
        curr_time = curr_time + 1 / 60;
    end
    frame_3d_matrix = dots.dotsPositions;
end