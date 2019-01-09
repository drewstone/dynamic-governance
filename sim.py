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


def explicit_honest_agents(capacities, report_type):
    return list(map(
        lambda val: Agent(constants.HONEST_AGENT, val, report_type),
        capacities))


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

        print(options["EXPLICIT_CAPACITIES"])
        if self.agent_mode == constants.HONEST_INCREASING_AGENTS:
            if len(options["EXPLICIT_CAPACITIES"]) > 0:
                self.agents = sorted(explicit_honest_agents(
                    options["EXPLICIT_CAPACITIES"], self.report_type),
                    key=lambda a: a.capacity)
            else:
                self.agents = sorted(all_honest_increasing(self.num_agents,
                                                           self.low_capacity,
                                                           self.report_type),
                                     key=lambda a: a.capacity)
        elif self.agent_mode == constants.HONEST_RANDOM_AGENTS:
            if len(options["EXPLICIT_CAPACITIES"]) > 0:
                self.agents = sorted(explicit_honest_agents(
                    options["EXPLICIT_CAPACITIES"], self.report_type),
                    key=lambda a: a.capacity)
            else:
                self.agents = sorted(all_honest_random(self.num_agents,
                                                       self.low_capacity,
                                                       self.high_capacity,
                                                       self.report_type),
                                     key=lambda a: a.capacity)
        else:
            value_error("Unsupported agent type: {}", self.agent_mode)

    def start(self):
        if self.logging_mode == constants.DEBUG_LOGGING:
            print("Agents = {}".format(
                list(map(lambda agent: agent.capacity, self.agents))))

        for i in range(self.num_rounds):
            _, payments = self.step()
            if self.logging_mode == constants.DEBUG_LOGGING:
                print("\nXXX\tRound {} | NEW_P = {}, OLD_P = {}, TPS = {}, DEC = {}\tXXX\n"
                      .format(self.gov.round,
                              self.gov.parameter,
                              self.gov.previous_parameter,
                              self.gov.throughput,
                              self.gov.decentralization))

                if payments:
                    payment_logs = list(map(lambda p: "Param {} => {}"
                                            .format(p[1], p[0]), payments))
                    print("\t\t\tPayments\n" + "\n".join(payment_logs))

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
            return self.gov.advance_round(reports)
        else:
            value_error("Unsupported step type: {}", self.step_type)

    def plot(self):
        pass
