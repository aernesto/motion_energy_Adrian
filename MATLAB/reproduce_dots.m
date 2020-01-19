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

DATA_FOLDER = ['/home/adrian/SingleCP_DotsReversal/Fall2019/raw/', ...%'/Users/adrian/oneCP/Fall_2019/raw/', ...
    session_timestamp, '/'];
FILE_NAME = ['completed4AFCtrials_task100_date_', ...
    session_timestamp, '.csv'];  
FIRA = [DATA_FOLDER, FILE_NAME];
DOTS = [DATA_FOLDER, session_timestamp, '_dotsPositions.csv'];
disp(DOTS)

trial_data = readtable(FIRA);

num_trials = size(trial_data); 
num_trials = num_trials(1);

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
    'taskID', ...
    'trialIx'};

fullMatrix = zeros(0,length(dotsColNames));
end_block = 0;

for trial_number = 1:num_trials
    row = trial_data(trial_number, :);
    [dots_params, frame_counts] = extract_dots_params(row);
    
    % loop over frames
    dotsPositions = generate_frames(dots_params, frame_counts);
    frames{trial_number} = dotsPositions;
    
    % recycle old function that translates frames into a table --> .csv
    numDotsFrames = size(dotsPositions,3);
    
    for frame = 1:numDotsFrames
        numDots = size(dotsPositions,2);
        
        start_block = end_block + 1;
        end_block = start_block + numDots - 1;
        
        fullMatrix(start_block:end_block,:) = [...
            squeeze(dotsPositions(:, :, frame)'),...
            repmat([frame, 100, trial_number-1], numDots, 1)];
    end
end

U=array2table(fullMatrix, 'VariableNames', dotsColNames);
writetable(U, DOTS, 'WriteRowNames',true)
disp('dots written')
end

function dd = flip_direction(d)
    if d == 180
        dd = 0; 
    else
        dd = 180;
    end
end


function [params, params2] = extract_dots_params(one_row)
% get dots stimulus parameter from table's single row
    params = table2struct(one_row);
    params2.numberDrawPreCP = params.numberDrawPreCP;
    params2.numberDrawPostCP = params.numberDrawPostCP;
    
    if params.reversal > 0  % there is a CP
        % set 'direction' to 'initDir' instead of 'endDir'
        params.direction = flip_direction(params.direction);
    end
    
    % remove unnecessary fields
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
        'dummyBlank', ...
        'cpTimeDotsClock', ...
        'firstDraw', ...
        'lastDraw', ...
        'firstDrawPostCP', ...
        'numberDrawPreCP', ...
        'numberDrawPostCP', ...
        'reversal', ...
        'duration', ...
        'finalDuration'});
    
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
    second_struct)
% get dotsPositions 3D matrix from dotsDrawableDotKinetogramDebug's trial
    reversal_frame = second_struct.numberDrawPreCP + 1;
    tot_num_frames = second_struct.numberDrawPostCP + ...
        second_struct.numberDrawPreCP;

    dots = dotsDrawableDotKinetogramDebug(params_struct);

    % loop through frame
    i = 1;  % frame count
    dots.prepare_to_virtually_draw(60);
    while i <= tot_num_frames
        if i == reversal_frame
            dots.direction = flip_direction(dots.direction);
        end
        dots.computeNextFrame();
        i = i + 1;
    end
    frame_3d_matrix = dots.dotsPositions;
end