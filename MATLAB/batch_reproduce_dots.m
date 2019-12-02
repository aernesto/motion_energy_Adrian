% reproduce and save dots for a list of sessions
% on the path should be:
% Lab_Matlab_Control_Adrian_Fork
% Analysis_SingleCP_DotsReversal
% Lab_Matlab_Utilities
% mgl
% mQUESTPlus

list_of_sessions = { ...
    '2019_11_20_15_34', ...  %done
    '2019_11_19_13_15', ...  %done %  '2019_11_06_15_02', ...   problematic -- WHY?
    '2019_11_06_12_43', ... % done
    '2019_11_05_16_19', ... % done
    '2019_11_05_13_18', ... % done
    '2019_11_05_10_27', ... % done
    '2019_11_25_16_12', ... % done
    '2019_11_26_13_11', ... % done
    };

for s = 1:length(list_of_sessions)
    timestamp = list_of_sessions{s};
    reproduce_dots(timestamp, false);
end