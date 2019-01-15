function entry = get_next_entry(vector, index)
% returns vector(index+1) if exists, NaN otherwise
    if length(vector) > index
        entry = vector(index+1);
    else
        entry = nan;
    end
end