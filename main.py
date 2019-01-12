import numpy as np
from agent import Agent
from errors import value_error
import constants
from sim import Simulator


def random_node_capacities(n, low, high):
    return np.random.randint(low, high + 1, n)


def increasing_node_capacities(n, start):
    return np.arange(start, start + n)


def all_honest_random(n, low, high, report_type):
    return list(map(
        lambda val: Agent(constants.HONEST_AGENT, val, report_type),
        random_node_capacities(n, low, high)))


def all_honest_increasing(n, start, report_type):
    return list(map(
        lambda val: Agent(constants.HONEST_AGENT, val, report_type),
        increasing_node_capacities(n, start)))


def explicit_honest_agents(capacities, report_type):
    return list(map(
        lambda val: Agent(constants.HONEST_AGENT, val, report_type),
        capacities))


def setup_agents(options):
    if len(options["capacities"]) > 0:
        return sorted(explicit_honest_agents(
            options["capacities"], options["report_type"]),
            key=lambda a: a.capacity)

    if options["agent_mode"] == constants.HONEST_INCREASING_AGENTS:
        return sorted(all_honest_increasing(options["num_agents"],
                                            options["low_capacity"],
                                            options["report_type"]),
                      key=lambda a: a.capacity)

    if options["agent_mode"] == constants.HONEST_RANDOM_AGENTS:
        return sorted(all_honest_random(options["num_agents"],
                                        options["low_capacity"],
                                        options["high_capacity"],
                                        options["report_type"]),
                      key=lambda a: a.capacity)

    value_error("Unsupported agent type: {}", options["agent_mode"])


if __name__ == "__main__":
    agent_options = {
        "num_agents": 10,
        "low_capacity": 5,
        "high_capacity": 100,
        "agent_mode": constants.HONEST_RANDOM_AGENTS,
        "capacities": [],
    }

    agents = setup_agents(agent_options)

    initial_param = 0
    num_rounds = 2
    report_type = [constants.DIRECT_CAPACITY_REPORT]
    step_type = constants.ALL_REPORTS
    decision_type = [constants.SOCIAL_WELFARE_MAXIMIZING,
                     constants.MEDIAN_REPORT]
    logging_mode = constants.DEBUG_LOGGING

    for d_type in decision_type:
        sim = Simulator({
            "agent": agents,
            "num_rounds": num_rounds,
            "initial_param": initial_param,
            "step_type": step_type,
            "decision_type": d_type,
            "logging_mode": logging_mode,
        })

        sim.start()
