# This script analyzes the effect of fractional utilities and
# mechanisms for selecting a capacity that maximizes a non
# welfare metric. Since as we will show below, the social
# welfare maximizing metric is sub-optimal for decentralization

# Consider agents who each have a capacity. For each agent
# with capacity at least as large as the system capcity, this
# agent derives $capacity * fraction_of_hashpower$ utility
# and zero otherwise. Since the sum of fractions of hashpower
# is 1, the social welfare maximizing capacity is to just select
# the largest possible capacity for a the given set of agents.
# Thus, the system tolerates high throughput, but the lowest
# decentralization.

import numpy as np
import agent
import constants

num_agents = 10
initial_capacity = 0
behavior_type = constants.HONEST_AGENT
report_type = constants.DIRECT_CAPACITY_REPORT


def increasing_node_capacities(n, start):
    return list(
        map(
            lambda capacity: agent.Agent(behavior_type,
                                         capacity,
                                         constants.DIRECT_CAPACITY_REPORT),
            np.arange(start, start + n)
        )
    )


print(increasing_node_capacities(num_agents, 10))

def obj(reports):
    obj_arr = []
    max_obj = 0
    for r in reports:
        (capacity, _) = r

        summed_hashpower = 0
        for rr in reports:
            (c, h) = r

            if c >= capacity:
                summed_hashpower += h * capacity

        if summed_hashpower == max_obj:
            obj_arr.append(capacity)

        if summed_hashpower > max_obj:
            obj_arr = [capacity]
            max_obj = summed_hashpower

def reports(agents):
    return list(map(lambda a: a.capacity, self.active_agents))
