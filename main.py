import time
import numpy as np
from errors import value_error
import constants
from sim import Simulator


if __name__ == "__main__":
    agent_options = {
        "num_agents": 30,
        "low_capacity": 5,
        "high_capacity": 100,
        "agent_mode": constants.HONEST_RANDOM_AGENTS,
        "capacities": [],
        "report_type": constants.DIRECT_CAPACITY_REPORT,
    }

    initial_param = 1
    num_rounds = 5 * (int(np.ceil(np.log(30))) + 1)
    num_times = 100
    bounded_perc = 0.25
    suppress_perc = 0.33

    decision_types = [
        # constants.SOCIAL_WELFARE_MAXIMIZING,
        # constants.MEDIAN_REPORT,
        # constants.LOWER_MEDIAN_REPORT,
        # constants.UPPER_MEDIAN_REPORT,
        # constants.WEIGHTED_MEDIAN_REPORT,
        constants.SUPPRESSED_MEDIAN_REPORT,
        constants.SUPPRESSED_WEIGHTED_MEDIAN_REPORT
        # constants.HASHPOWER_CAPACITY_MAXIMIZING,
        # constants.HASHPOWER_CAPSQUARED_MAXIMIZING,
        # constants.HASHPOWER_CAPSQRT_MAXIMIZING,
        # constants.LEADER_REPORT,
        # constants.BOUNDED_LEADER_REPORT,
    ]
    utility_types = [
        constants.LINEAR_UTILITY,
    ]

    mutation_rule = constants.CYCLE_ONE_AGENT

    # logging_mode = constants.DEBUG_LOGGING
    logging_mode = None
    # logging_mode = constants.LOG_DROPOUT

    sim = Simulator({
        "agent_options": agent_options,
        "num_rounds": num_rounds,
        "num_times": num_times,
        "initial_param": initial_param,
        "decision_types": decision_types,
        "utility_types": utility_types,
        "logging_mode": logging_mode,
        "bounded_percent": bounded_perc,
        "suppress_percent": suppress_perc,
        "mutation_rule": mutation_rule,
    })


    start_time = time.time()
    sim.start()
    print("--- %s seconds ---" % (time.time() - start_time))
