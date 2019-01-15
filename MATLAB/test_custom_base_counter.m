slots = {[5,6],...
    [33,37], ...
    [400,4000]};
currNumber = [5,33, 400]
for i = 1:7
    currNumber = custom_base_counter(currNumber, slots)
end
    