function reproduce_dots(session_timestamp)
% ARGS:
%    session_timestamp    string like '2019_11_22_13_59'
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
%     b) get all the paramters that specify the dotsDrawableDotKinetogram
%     c) generate the frames (and save them) WITHOUT drawing anything
%
% 3/ produce final dotsPositions.csv file
end