function trialIx=get_trialIndex_from_trialID(trialID)
  trialIx = str2num(trialID(end-4:end));
end