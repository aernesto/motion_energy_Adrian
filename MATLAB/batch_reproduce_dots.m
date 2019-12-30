% reproduce and save dots for a list of sessions
% on the path should be:
% Lab_Matlab_Control_Adrian_Fork
% Analysis_SingleCP_DotsReversal
% Lab_Matlab_Utilities
% mgl
% mQUESTPlus
% 
%
% REPRODUCED WITH OLD WAY
% that is the way that did not save the number of frames by epoch
%     '2019_11_20_15_34', ... done
%     '2019_11_19_13_15', ... done 
%     '2019_11_06_15_02', ... faulty dataset
%     '2019_11_06_12_43', ... done
%     '2019_11_05_16_19', ... done
%     '2019_11_05_13_18', ... done
%     '2019_11_05_10_27', ... done
%     '2019_11_25_16_12', ... done
%     '2019_11_26_13_11', ... done
%     '2019_12_11_12_21', ... done
%     '2019_12_12_14_06', ... done
%
%     '2019_12_13_13_37', ... test dataset
%
% REPRODUCED WITH THE NEW WAY that stores number of frames per epoch
%
%
%
%
%
%
%
list_of_sessions = { ...
    '2019_12_18_14_00', ...
    '2019_12_19_09_57', ...
    '2019_12_18_17_06', ...
    '2019_12_30_13_47', ...
    };

for s = 1:length(list_of_sessions)
    timestamp = list_of_sessions{s};
    reproduce_dots(timestamp, false);
end