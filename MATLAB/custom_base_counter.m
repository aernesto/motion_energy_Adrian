function nextNumber = custom_base_counter(currNumber, slots)
% counts in a custom basis. For instance, if a can take on the values 5 and
% 6, and b can take on the values 33, 37 and 59, then counting in this
% basis looks like the following
% 33 5
% 33 6
% 37 5
% 37 6
% 59 5
% 59 6
% this function is useful to loop through all combinations of vectors that
% don't have same size.
% ARGS:
%   currNumber  - current number, provided in the custom basis
%   slots       - allowed values for each entry in the basis. Should be a
%                 cell of vectors, and no vector has duplicate values
% RETURNS:
%   nextNumber  - next number, incrementing by 1 in the custom basis

nextNumber = currNumber;
numEntries = length(currNumber);


for entry_idx = 1:numEntries
    entry = currNumber(entry_idx);
    currSlot = slots{entry_idx};
    dummySeq = 1:length(currSlot);
    idx_in_slot = dummySeq(ismember(currSlot, entry));
    new_entry = get_next_entry(currSlot, idx_in_slot);
    if isnan(new_entry)
        nextNumber(entry_idx) = currSlot(1);
        continue  % to update next digit
    else
        nextNumber(entry_idx) = new_entry;
        break
    end        
end   

if entry_idx == numEntries && isnan(new_entry)
    disp('max number reached in custom basis')
    nextNumber = currNumber;
end

end