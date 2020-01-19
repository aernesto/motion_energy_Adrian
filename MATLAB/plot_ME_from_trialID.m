function plot_ME_from_trialID(trialID, me_tab, fira_tab)
% Doesn't transform motion energy whatsoever
figure()
% extract vector of time points for motion energy
times = me_tab{1,2:end};
me_dims = size(me_tab);
for row=2:me_dims(1)
    if strcmp(me_tab.Var1{row}, trialID)
        break
    end
end

plot(times, me_tab{row,2:end})

trial_index = get_trialIndex_from_trialID(trialID);
title(build_description(fira_tab, trial_index))
ylabel('ME')
xlabel('time (s)')
xlim([0,.65])
hold on
cptime = fira_tab(fira_tab.trialIndex == trial_index,:).finalCPTime;
if not(isnan(cptime))
    plot([cptime, cptime], [-50,50], 'r')
end
hold off
end