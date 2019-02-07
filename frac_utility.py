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

import math
import numpy as np
import pprint
import agent
import constants
import copy

num_agents = 10
initial_capacity = 0
behavior_type = constants.HONEST_AGENT
report_type = constants.DIRECT_CAPACITY_REPORT


def increasing_node_capacities(n, start):
    agents = []
    caps = np.arange(start, start + n)

    for i in range(n):
        agents.append(agent.Agent(behavior_type,
                                  caps[i],
                                  math.pow(caps[i], 2),
                                  constants.DIRECT_CAPACITY_REPORT))
    return agents


def random_node_capacities(n, low, high):
    agents = []
    caps = np.random.randint(low, high + 1, n)
    hashes = np.random.randint(low, (high + 1) * 10, n)

    for i in range(n):
        agents.append(agent.Agent(behavior_type,
                                  caps[i],
                                  hashes[i],
                                  constants.DIRECT_CAPACITY_REPORT))
    return agents


def maximize_obj(reports):
    max_cap = {
        "normal": 0,
        "sqrt_capacity": 0,
        "squared_capacity": 0,
        "cubed_capacity": 0,
        "sqrt_hashpower": 0,
        "squared_hashpower": 0,
        "cubed_hashpower": 0,
        "sqrt_both": 0,
        "squared_hashpower": 0,
        "cubed_hashpower": 0,
    }
    max_obj = {
        "normal": 0,
        "sqrt_capacity": 0,
        "squared_capacity": 0,
        "cubed_capacity": 0,
        "sqrt_hashpower": 0,
        "squared_hashpower": 0,
        "cubed_hashpower": 0,
        "sqrt_both": 0,
        "squared_both": 0,
        "cubed_both": 0,
    }
    hashpower_sum = {
        "normal": 0,
        "sqrt_capacity": 0,
        "squared_capacity": 0,
        "cubed_capacity": 0,
        "sqrt_hashpower": 0,
        "squared_hashpower": 0,
        "cubed_hashpower": 0,
        "sqrt_both": 0,
        "squared_both": 0,
        "cubed_both": 0,
    }

    for r in reports:
        (capacity, _) = r
        summed_hashpower = sum([
            reports[j][1] for j in range(len(reports)) if reports[j][0] >= capacity
        ])

        if summed_hashpower * capacity > max_obj["normal"]:
            max_cap["normal"] = capacity
            max_obj["normal"] = summed_hashpower * capacity
            hashpower_sum["normal"] = summed_hashpower
        if summed_hashpower * math.sqrt(capacity) > max_obj["sqrt_capacity"]:
            max_cap["sqrt_capacity"] = capacity
            max_obj["sqrt_capacity"] = summed_hashpower * math.sqrt(capacity)
            hashpower_sum["sqrt_capacity"] = summed_hashpower
        if summed_hashpower * math.pow(capacity, 2) > max_obj["squared_capacity"]:
            max_cap["squared_capacity"] = capacity
            max_obj["squared_capacity"] = summed_hashpower * math.pow(capacity, 2)
            hashpower_sum["squared_capacity"] = summed_hashpower
        if summed_hashpower * math.pow(capacity, 3) > max_obj["cubed_capacity"]:
            max_cap["cubed_capacity"] = capacity
            max_obj["cubed_capacity"] = summed_hashpower * math.pow(capacity, 3)
            hashpower_sum["cubed_capacity"] = summed_hashpower
        if math.sqrt(summed_hashpower) * capacity > max_obj["sqrt_hashpower"]:
            max_cap["sqrt_hashpower"] = capacity
            max_obj["sqrt_hashpower"] = math.sqrt(summed_hashpower) * capacity
            hashpower_sum["sqrt_hashpower"] = summed_hashpower
        if math.pow(summed_hashpower, 2) * capacity > max_obj["squared_hashpower"]:
            max_cap["squared_hashpower"] = capacity
            max_obj["squared_hashpower"] = math.pow(summed_hashpower, 2) * capacity
            hashpower_sum["squared_hashpower"] = summed_hashpower
        if math.pow(summed_hashpower, 3) * capacity > max_obj["cubed_hashpower"]:
            max_cap["cubed_hashpower"] = capacity
            max_obj["cubed_hashpower"] = math.pow(summed_hashpower, 3) * capacity
            hashpower_sum["cubed_hashpower"] = summed_hashpower
        if math.sqrt(summed_hashpower) * math.sqrt(capacity) > max_obj["sqrt_both"]:
            max_cap["sqrt_both"] = capacity
            max_obj["sqrt_both"] = math.sqrt(summed_hashpower) * math.sqrt(capacity)
            hashpower_sum["sqrt_both"] = summed_hashpower
        if math.pow(summed_hashpower, 2) * math.pow(capacity, 2) > max_obj["squared_both"]:
            max_cap["squared_both"] = capacity
            max_obj["squared_both"] = math.pow(summed_hashpower, 2) * math.pow(capacity, 2)
            hashpower_sum["squared_both"] = summed_hashpower
        if math.pow(summed_hashpower, 3) * math.pow(capacity, 3) > max_obj["cubed_both"]:
            max_cap["cubed_both"] = capacity
            max_obj["cubed_both"] = math.pow(summed_hashpower, 3) * math.pow(capacity, 3)
            hashpower_sum["cubed_both"] = summed_hashpower
    return (max_cap, max_obj, hashpower_sum)


def get_agent_reports(agents):
    return list(map(lambda a: (a.capacity, a.hash_power), agents))


# run simulation a bunch of times
for t in range(100):
    # sample random node capacities
    agents = random_node_capacities(100, 10, 100)
    # agents = increasing_node_capacities(100, 10)
    # get reports from agents
    reports = get_agent_reports(agents)
    # find maximizing capacity
    (max_cap, _, hash_sum) = maximize_obj(reports)
    # logging
    print("Run {}, reports = {}".format(t, reports))
    print("Max cap\n")
    pprint.pprint(max_cap)
    # test misreporting above and below for all agents below
    for inx, a in enumerate(agents):
        # agents whose capacity is above or below may be
        # able to affect outcome by misreporting below
        for key in max_cap:
            if a.capacity < max_cap[key]:
                utility_of_agent = 0
            else:
                utility_of_agent = a.capacity * (a.hash_power * 1.0 / hash_sum[key])

            if a.capacity < max_cap[key] or a.capacity > max_cap[key]:
                agents_copy = copy.deepcopy(agents)
                ctr = 1
                while a.capacity - ctr > 0:
                    new_capacity = a.capacity - ctr
                    agents_copy[inx].capacity = new_capacity
                    new_reports = get_agent_reports(agents_copy)
                    (new_max_cap, new_values, hp_sum) = maximize_obj(new_reports)
                    ctr += 1
                    
                    if a.capacity < new_max_cap[key]:
                        utility_from_deviation = 0
                    else:
                        utility_from_deviation = new_max_cap[key] * (a.hash_power * 1.0 / hp_sum[key])

                    if utility_from_deviation > utility_of_agent:
                        str = "KEY = {}, NEW_MAX_CAP = {}, AGENT = {}, DEVIATION = {}, OLD = {}"
                        print(str.format(
                            key, new_max_cap[key], a.capacity, new_capacity, max_cap[key]))

                ctr = 1
                while a.capacity + ctr < a.capacity + 10:
                    new_capacity = a.capacity + ctr
                    agents_copy[inx].capacity = new_capacity
                    new_reports = get_agent_reports(agents_copy)
                    (new_max_cap, new_values, hp_sum) = maximize_obj(new_reports)
                    ctr += 1

                    if a.capacity < new_max_cap[key]:
                        utility_from_deviation = 0
                    else:
                        utility_from_deviation = new_max_cap[key] * (a.hash_power * 1.0 / hp_sum[key])

                    if utility_from_deviation > utility_of_agent:
                        str = "KEY = {}, NEW_MAX_CAP = {}, AGENT = {}, DEVIATION = {}, OLD = {}"
                        print(str.format(
                            key, new_max_cap[key], a.capacity, new_capacity, max_cap[key]))
    print("")
