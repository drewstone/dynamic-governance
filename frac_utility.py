# This script analyzes the effect of fractional utilities and
# mechanisms for selecting a capacity that maximizes a non
# welfare metric. Since as we will show below, the social
# welfare maximizing metric is sub-optimal for decentralization

# Consider agents who each have a capacity. For each agent
# with capacity at least as large as the system capacity, this
# agent derives $capacity * fraction_of_hashpower$ utility
# and zero otherwise. Since the sum of fractions of hashpower
# is 1, the social welfare maximizing capacity is to just select
# the largest possible capacity for a the given set of agents.
# Thus, the system tolerates high throughput, but the lowest
# decentralization.

import numpy as np
import agent
import constants
import copy

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


def random_node_capacities(n, low, high):
    return list(
        map(
            lambda capacity: agent.Agent(behavior_type,
                                         capacity,
                                         constants.DIRECT_CAPACITY_REPORT),
            np.random.randint(low, high + 1, n)
        )
    )


def maximize_obj(reports):
    max_cap = 0
    max_obj = 0
    for r in reports:
        (capacity, _) = r

        summed_hashpower = 0
        for rr in reports:
            (c, h) = r

            if c >= capacity:
                summed_hashpower += h * capacity

        if summed_hashpower > max_obj:
            max_cap = capacity
            max_obj = summed_hashpower

    return (max_cap, max_obj)


def get_agent_reports(agents):
    return list(map(lambda a: (a.capacity, a.hash_power), agents))


for t in range(100):
    agents = random_node_capacities(10, 10, 100)
    reports = get_agent_reports(agents)
    (max_cap, value) = maximize_obj(reports)

    print("Run {}".format(t))
    print("Max cap {}, value {}".format(max_cap, value))

    # test misreporting below for all agents below
    for inx, a in enumerate(agents):
        # agents whose capacity is above or below may be
        # able to affect outcome by misreporting below
        if a.capacity < max_cap or a.capacity > max_cap:
            agents_copy = copy.deepcopy(agents)
            ctr = 1
            while a.capacity - ctr > 0:
                ctr += 1
                new_capacity = a.capacity - ctr
                agents_copy[inx].capacity = new_capacity
                new_reports = get_agent_reports(agents_copy)
                (new_max_cap, new_values) = maximize_obj(new_reports)

                if new_max_cap != max_cap:
                    print("New max cap: {} with {} deviating with capacity {}".format(
                        new_max_cap, a.capacity, new_capacity))

            ctr = 1
            while a.capacity + ctr < a.capacity + 20:
                ctr += 1
                new_capacity = a.capacity + ctr
                agents_copy[inx].capacity = new_capacity
                new_reports = get_agent_reports(agents_copy)
                (new_max_cap, new_values) = maximize_obj(new_reports)

                if new_max_cap != max_cap:
                    print("New max cap: {} with {} deviating with capacity {}".format(
                        new_max_cap, a.capacity, new_capacity))
    print("")
