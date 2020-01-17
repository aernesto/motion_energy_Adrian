function trialID=get_trialID_from_trialIndex(trialIx, behavr_table)
  ts = num2str(behavr_table(behavr_table.trialIndex == trialIx,:).date);
  ts = [ts(1:4),'_',ts(5:6),'_',ts(7:8),'_',ts(9:10),'_',ts(11:12)];
  ixs = num2str(trialIx);
  padding = 5 - length(ixs);
  trialID = [ts, '_', repmat('0',1, padding), ixs];
end