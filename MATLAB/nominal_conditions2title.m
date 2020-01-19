function desc = nominal_conditions2title(cond_struct)
  coh = ['coh=',num2str(cond_struct.coherence)];
  desc = [coh, '; endDir=', cond_struct.endDir, '; hasCP=', ...
      cond_struct.CP, '; choice=', cond_struct.dirChoice];
end