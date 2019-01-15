%% DESCRIPTION
% Aim of this script is to launch a series of trials and to record the dots
% stimulus info from each one of them, on a frame-by-frame basis
% 
% All the resulting data gets dumped into a single .csv file

clear
tic
%% PARAMETER SETTINGS

oFileName = 'ME_DB_1'; % shouldn't include the extension, nor the path
% this is the absolute path to the output file
oFilePath = '~/DATA/MATLAB/dots_frame_by_frame/'; 

% spans of parameters to sweep through
cohSpan     = [0,20];%0:20:100; % coherence
dirSpan     = [0,1];%[0,1];    % direction
speedSpan   = 2:3;%2:5;    % speed
durSpan     = .2;%[.2,.4];  % duration in sec
cpSpan      = 0;%[0];    % change point presence
seedSpan    = 1:2;%1:5;      % random seed

iterPerCond = 2;        % number of iteration per condition

numComb = length(cohSpan) * ... % number of combinations
    length(dirSpan)       * ...
    length(speedSpan)     * ...
    length(durSpan)       * ...
    length(cpSpan)        * ...
    length(seedSpan)      ;

% generate all possible combinations
combinations = cell(1,numComb);

% actual values at initialization
comb = [...
    cohSpan(1),...
    dirSpan(1),...
    speedSpan(1),...
    durSpan(1),...
    cpSpan(1),...
    seedSpan(1)];

% allowed values for each parameter
slots = {...
    cohSpan,...
    dirSpan,...
    speedSpan,...
    durSpan,...
    cpSpan,...
    seedSpan}; 

% initialize outside of for loop
combinations{1} = comb;

% fill in the rest with a for loop
for cc = 2:numComb
    comb = custom_base_counter(comb, slots);
    combinations{cc} = comb;
end

% static parameters that don't change across trials
dotsParams.stencilNumber = 1;
dotsParams.pixelSize     = 5;
dotsParams.diameter      = 10;
dotsParams.yCenter       = 0;
dotsParams.xCenter       = 0;
dotsParams.density       = 80;
dotsParams.coherenceSTD  = 0; % I don't know what that is

displayIndex = 1;

% column names in final csv file
colNames={...
    'stencilNumber', ...
    'pixelSize', ...
    'diameter', ...
    'speed', ...
    'yCenter', ...
    'xCenter', ...
    'density', ...
    'direction', ...
    'coherence', ...
    'dotsDuration', ...
    'randSeedBase', ...
    'coherenceSTD', ...
    'frameIdx', ...
    'onsetTime', ...
    'onsetFrame', ...
    'swapTime', ...
    'isTight', ...
    'iter', ...
    'dotIdx', ...
    'xpos', ...
    'ypos', ...
    'isCoherent'};


%% RUN TRIALS

% cell that will store the data of each iteration as a table
data_as_cell = cell(iterPerCond, numComb);

for comb_idx = 1:numComb
    % set parameters for this combination
    comb = combinations{comb_idx};
    
    dotsParams.coherence    = comb(1);
    dotsParams.direction    = comb(2);
    dotsParams.speed        = comb(3);
    dotsParams.dotsDuration = comb(4); % in sec
    dotsParams.cp           = comb(5);
    dotsParams.randSeedBase = comb(6);
    
    for iter = 1:iterPerCond
        data_as_cell{iter, comb_idx} = produce_dots(displayIndex,...
            colNames, dotsParams, iter);
    end
end

%% SAVE / WRITE TO FILE
% convert all the data into a single table
accumulationTable = [data_as_cell{1,1};data_as_cell{2,1}];
for ccc = 2:numComb
    for iii = 1:iterPerCond
        accumulationTable = [accumulationTable; data_as_cell{iii,ccc}];
    end
end

save([oFilePath, oFileName,'.mat']) % to save workspace
fileToWrite = [oFilePath, oFileName, '.csv'];
writetable(accumulationTable,fileToWrite,'WriteRowNames',true)
toc