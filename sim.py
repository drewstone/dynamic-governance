import numpy as np
import constants
from agent import Agent
from gov import Government
from errors import value_error


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


class Simulator(object):
    def __init__(self, options):
        super(Simulator, self).__init__()
        self.num_agents = options["num_agents"]
        self.low_capacity = options["low_capacity"]
        self.high_capacity = options["high_capacity"]
        self.agent_mode = options["agent_mode"]
        self.num_rounds = options["num_rounds"]
        self.initial_param = options["initial_param"]
        self.report_type = options["report_type"]
        self.step_type = options["step_type"]
        self.decision_type = options["decision_type"]
        self.logging_mode = options["logging_mode"]

        # initialize government
        self.gov = Government(options)

        if self.agent_mode == constants.HONEST_INCREASING_AGENTS:
            self.agents = all_honest_increasing(self.num_agents,
                                                self.low_capacity,
                                                self.report_type)
        elif self.agent_mode == constants.HONEST_RANDOM_AGENTS:
            self.agents = all_honest_random(self.num_agents,
                                            self.low_capacity,
                                            self.high_capacity,
                                            self.report_type)
        else:
            value_error("Unsupported agent type: {}", self.agent_mode)

    def start(self):
        if self.logging_mode == constants.DEBUG_LOGGING:
            print("Agents = {}".format(
                list(map(lambda agent: agent.capacity, self.agents))))

        for i in range(self.num_rounds):
            self.step()
            if self.logging_mode == constants.DEBUG_LOGGING:
                print("Round {} | NEW_P = {}, OLD_P = {}, TPS = {}, DEC = {}"
                      .format(self.gov.round,
                              self.gov.parameter,
                              self.gov.previous_parameter,
                              self.gov.throughput,
                              self.gov.decentralization))

        self.plot()

    def step(self):
        # sample a leader uniformly at random
        if self.step_type == constants.UNIFORM_LEADER_ELECTION:
            leader = self.agents[np.random.choice(
                np.arange(0, len(self.agents)))]

        # sample a leader proportional to an agent's capacity
        elif self.step_type == constants.WEIGHTED_LEADER_ELECTION:
            caps = list(map(lambda a: a.capacity, self.agents))
            weight_sum = sum(caps)
            distribution = [1.0 * i / weight_sum for i in caps]
            leader_index = np.random.choice(
                np.arange(0, len(caps), p=distribution))
            leader = self.agent(leader_index)

        # elicit reports from all agents
        elif self.step_type == constants.ALL_REPORTS:
            # gather reports for current parameter
            reports = list(map(lambda a: a.report(
                self.gov.parameter), self.agents))
            # advance round and receive new parameter given reports
            self.gov.advance_round(reports)
        else:
            value_error("Unsupported step type: {}", self.step_type)

    def plot(self):
        pass
