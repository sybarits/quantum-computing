from dimod.generators import and_gate
from dwave.system import LeapHybridSampler

bqm = and_gate('x1', 'x2', 'y1')
sampler = LeapHybridSampler()    
answer = sampler.sample(bqm)   
print(answer)    
