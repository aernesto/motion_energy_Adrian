function desc = build_description(behavior_table, trialIndex)
  single_row = behavior_table(behavior_table.trialIndex == trialIndex, :);
  coh = ['coh=',num2str(single_row.coherence(1))];
  dir = single_row.direction(1);
  if dir == 180
      dir = 'left';
  else
      dir = 'right';
  end
  rev = single_row.reversal(1);
  if rev < 0.001
      rev = 'NO';
  else
      rev = 'YES';
  end
  desc = [coh, '; startDir=', dir, '; hasCP=', rev];
end