import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np;
import agent
import constants

def get_random_agent_distribution(num_agents):
	agents = agent.setup_agents({
		"capacities": [],
		"agent_mode": constants.HONEST_RANDOM_AGENTS,
		"num_agents": num_agents,
		"low_capacity": 1,
		"high_capacity": 1000,
		"report_type": constants.DIRECT_CAPACITY_REPORT,
	})
	
	total_hash = sum(list(map(lambda a: a.hash_power, agents)))
	distribution = list(map(lambda a: a.hash_power * 1.0 / total_hash, agents))
	return distribution


num_agents = 10
delta = 1*10**(-num_agents)

lengths = []
for i in range(1000):
	ctr = 1
	distribution = get_random_agent_distribution(num_agents)
	while True:
		summation = sum(list(map(lambda p: (1-p)**ctr, distribution)))
		if summation < delta:
			lengths.append(ctr)
			break
		else:
			ctr += 1

lengths = np.array(lengths)
mean = np.mean(lengths)
print(mean, lengths)