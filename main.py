import time
import numpy as np
from agent import Agent
from errors import value_error
import constants
from sim import Simulator


def increasing_node_capacities(n, start, report_type):
    agents = []
    caps = sorted(np.arange(start, start + n))
    hashes = np.arange(start, start + n)

    for i in range(n):
        agents.append(Agent(constants.HONEST_AGENT,
                            caps[i],
                            hashes[i],
                            report_type))
    return agents


def random_node_capacities(n, low, high, report_type):
    agents = []
    caps = sorted(np.random.randint(low, high + 1, n))
    hashes = np.random.randint(low, high + 1, n)

    for i in range(n):
        agents.append(Agent(constants.HONEST_AGENT,
                            caps[i],
                            hashes[i],
                            report_type))
    return agents


def explicit_honest_agents(caps, hashes, report_type):
    agents = []

    for i in range(len(caps)):
        agents.append(Agent(constants.HONEST_AGENT,
                            caps[i],
                            hashes[i],
                            constants.DIRECT_CAPACITY_REPORT))
    return agents


def setup_agents(options):
    if len(options["capacities"]) > 0 and len(options["hashes"]) > 0:
        return explicit_honest_agents(options["capacities"],
                                      options["hashes"],
                                      options["report_type"])

    if options["agent_mode"] == constants.HONEST_INCREASING_AGENTS:
        return increasing_node_capacities(options["num_agents"],
                                          options["low_capacity"],
                                          options["report_type"])

    if options["agent_mode"] == constants.HONEST_RANDOM_AGENTS:
        return random_node_capacities(options["num_agents"],
                                      options["low_capacity"],
                                      options["high_capacity"],
                                      options["report_type"])

    value_error("Unsupported agent type: {}", options["agent_mode"])


if __name__ == "__main__":
    agent_options = {
        "num_agents": 30,
        "low_capacity": 5,
        "high_capacity": 100,
        "agent_mode": constants.HONEST_RANDOM_AGENTS,
        "capacities": [],
        "report_type": constants.DIRECT_CAPACITY_REPORT,
    }

    agents = setup_agents(agent_options)
    initial_param = 1
    num_rounds = 5 * (int(np.ceil(np.log(30))) + 1)
    num_times = 100
    bounded_perc = 0.25

    decision_types = [
        # constants.SOCIAL_WELFARE_MAXIMIZING,
        # constants.MEDIAN_REPORT,
        # constants.LOWER_MEDIAN_REPORT,
        # constants.UPPER_MEDIAN_REPORT,
        # constants.WEIGHTED_MEDIAN_REPORT,
        constants.HASHPOWER_CAPACITY_MAXIMIZING,
        constants.HASHPOWER_CAPSQUARED_MAXIMIZING,
        constants.HASHPOWER_CAPSQRT_MAXIMIZING,
        # constants.LEADER_REPORT,
        # constants.BOUNDED_LEADER_REPORT,
    ]
    utility_types = [
        constants.LINEAR_UTILITY,
    ]

    # logging_mode = constants.DEBUG_LOGGING
    logging_mode = None
    # logging_mode = constants.LOG_DROPOUT

    sim = Simulator({
        "agents": agents,
        "num_rounds": num_rounds,
        "num_times": num_times,
        "initial_param": initial_param,
        "decision_types": decision_types,
        "utility_types": utility_types,
        "logging_mode": logging_mode,
        "bounded_percent": bounded_perc,
    })


    start_time = time.time()
    sim.start()
    print("--- %s seconds ---" % (time.time() - start_time))
