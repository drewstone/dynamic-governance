import numpy as np
import constants
from errors import value_error


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


class Agent(object):
    """An agent represents an atomic participant in a governance simulation"""

    def __init__(self, ttype, capacity, hash_power, report_type):
        super(Agent, self).__init__()
        self.ttype = ttype
        self.capacity = capacity
        self.hash_power = hash_power
        self.report_type = report_type

    def report(self, parameter):
        if self.ttype == constants.RANDOM_AGENT:
            return np.random.choice(self.feasible_reports())
        if self.ttype == constants.HONEST_AGENT:
            return self.honest_report(parameter)
        if self.ttype == constants.SELFISH_AGENT:
            return self.selfish_report(parameter)

    def feasible_reports(self):
        if self.report_type in [constants.DIRECTIONAL_REPORT,
                                constants.RANDOM_DIRECTIONAL_REPORT]:
            return [0, 1, 2]
        else:
            value_error("Unsupported report type {}", self.report_type)

    def honest_report(self, parameter):
        if self.report_type in [constants.DIRECTIONAL_REPORT,
                                constants.RANDOM_DIRECTIONAL_REPORT]:
            return (0 if self.capacity < parameter
                    else 1 if self.capacity == parameter
                    else 2)
        elif self.report_type == constants.DIRECT_CAPACITY_REPORT:
            return self.capacity
        else:
            value_error("Unsupported report type {}", self.report_type)

    def selfish_report(self, parameter):
        if self.report_type == constants.DIRECT_CAPACITY_REPORT:
            return self.capacity
        else:
            value_error("Unsupported report type {}", self.report_type)

    def __str__(self):
        return "{}".format(self.capacity)
