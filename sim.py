import numpy as np
import constants
from gov import Government
from errors import value_error


class Simulator(object):
    def __init__(self, options):
        super(Simulator, self).__init__()
        self.agents = options["agents"]
        self.num_rounds = options["num_rounds"]
        self.initial_param = options["initial_param"]
        self.step_type = options["step_type"]
        self.decision_type = options["decision_type"]
        self.logging_mode = options["logging_mode"]

        # initialize government
        self.gov = Government(options)

    def start(self):
        if self.logging_mode == constants.DEBUG_LOGGING:
            print("Agents = {}".format(
                list(map(lambda agent: agent.capacity, self.agents))))

        for i in range(self.num_rounds):
            _, payments = self.step()
            if self.logging_mode == constants.DEBUG_LOGGING:
                print("\nXXX\tRound {} | NEW_P = {}, OLD_P = {}, TPS = {}, " +
                      "DEC = {}\tXXX\n".format(self.gov.round,
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
            leader = self.agents[leader_index]
            return leader.capacity

        # elicit reports from all agents
        elif self.step_type == constants.ALL_REPORTS:
            # gather reports for current parameter
            reports = list(map(lambda a: a.report(
                self.gov.parameter), self.agents))

            # gather weights of agents
            caps = list(map(lambda a: a.capacity, self.agents))
            weight_sum = sum(caps)
            weights = [1.0 * i / weight_sum for i in caps]

            # advance round and receive new parameter given reports
            return self.gov.advance_round(reports, weights)
        else:
            value_error("Unsupported step type: {}", self.step_type)

    def plot(self):
        pass
