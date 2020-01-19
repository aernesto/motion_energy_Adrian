function [kernel, tot_trials, trialID] = compute_kernel(nom_cond, fira, me)
% computes left-aligned average motion energy across group of trials
% satisfying the given nominal stimulus conditions and subject's direction
% choice.
% ARGS:
% nom_cond:  a struct fixing stimulus nominal conditions and subject's
% direction choice
% fira:   a table with FIRA behavioral data
% me:   motion energy table 
% NOTE: No transformation is applied to ME values (sign is NOT flipped)

% step 0 = convert human-readable stimulus conditions to appropriate values
    function new_struct = convert_conditions(cond)
        % assumes cond is a struct of stimulus nominal conditions and
        % subject's direction choice in 'human-readable' format. Returns a
        % struct with the format appropriate for indexing in the behavioral
        % table. 
        % NOTE: coherence and duration fields are left untouched
        if strcmp(cond.dirChoice, 'right')
            new_struct.dirChoice = 1;
        elseif strcmp(cond.dirChoice, 'left')
            new_struct.dirChoice = 0;
        else
            new_struct.dirChoice = 'any';
        end
        new_struct.coherence = cond.coherence;
        new_struct.duration = cond.duration;
        if strcmp(cond.endDir, 'right')
            new_struct.endDir = 0;
        elseif strcmp(cond.endDir, 'left')
            new_struct.endDir = 180;
        else 
            new_struct.endDir = 'any';
        end
        if strcmp(cond.CP, 'NO')
            new_struct.CP = 0;
        elseif strcmp(cond.CP, 'YES')
            new_struct.CP = 0.2;
        else
            new_struct.CP = 'any';
        end
    end

nom_cond = convert_conditions(nom_cond);

% step 1 = filter trials in behavioral table

logical_ix = fira.coherence == nom_cond.coherence;
logical_ix = logical_ix & (fira.duration == nom_cond.duration);

if not(ischar(nom_cond.dirChoice))  % only filter on dirChoice if not 'any'
    logical_ix = logical_ix & (fira.dirChoice == nom_cond.dirChoice);
end
if not(ischar(nom_cond.endDir))  % only filter on endDir if not 'any'
    logical_ix = logical_ix & (fira.direction == nom_cond.endDir);
end
if not(ischar(nom_cond.CP))
    logical_ix = logical_ix & (fira.reversal == nom_cond.CP);
end
useful_trials = fira(logical_ix, :);

% step 2 = convert trialIndex to trialID
trialID = cell(size(useful_trials.trialIndex));
for i = 1:length(trialID)
    tix = useful_trials.trialIndex(i);
    trialID{i} = get_trialID_from_trialIndex(tix, useful_trials);
end

% step 3 = extract relevant motion energy
me_dims = size(me);
logical_ix_me = false(me_dims);

% loop through rows of motion energy table and flag them as true if the
% trialID is one of the 'useful' ones
for r=1:me_dims(1)
    logical_ix_me(r) = ismember(me.Var1{r}, trialID);
end

relevant_me = me(logical_ix_me, 2:end);
tot_trials = size(relevant_me, 1);
% step 4 = average
kernel = mean(relevant_me{:, :}, 1);

end