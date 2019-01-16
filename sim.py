import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import statistics
import constants
from gov import Government
from errors import value_error



class Simulator(object):
    def __init__(self, options):
        super(Simulator, self).__init__()
        self.active_agents = options["agents"]
        self.inactive_agents = list()
        self.num_rounds = options["num_rounds"]
        self.num_times = options["num_times"]
        self.step_type = options["step_type"]
        self.logging_mode = options["logging_mode"]

        # initialize government
        self.gov = Government(options)
        self.dropout = False
        self.mine = True

        # initialize benchmarks and system parameters
        self.throughput = 0
        self.decentralization = 0

        # initialize histories for plotting
        self.history = {}

    def start(self):
        for i in range(self.num_times):
            self.run()
            self.throughput = 0
            self.decentralization = 0
            self.gov.reset()

        self.plot_history()

    def run(self):
        if self.logging_mode == constants.DEBUG_LOGGING:
            print("Agents = {}".format(
                list(map(lambda agent: agent.capacity, self.active_agents))))
            print("Starting parameter: {}".format(self.gov.parameter))

        for i in range(self.num_rounds):
            parameter, payments = self.step()

            if self.logging_mode == constants.DEBUG_LOGGING:
                print("\nRound {} | OLD_P = {}, NEW_P = {}, TPS = {}\n"
                      .format(self.gov.round,
                              self.gov.previous_parameter,
                              self.gov.parameter,
                              self.throughput))

            # assuming no agents dropout, mining non-empty and empty blocks
            if self.mine and not self.dropout:
                # leader election proportional to agent capacities
                leader = statistics.sample_proportional_to_capacity(
                    self.active_agents)

                # increment throughput based on leader election
                if leader.capacity < parameter:
                    self.throughput += 0
                else:
                    self.throughput += parameter

                if i in self.history:
                    self.history[i].append(self.throughput)
                else:
                    self.history[i] = [self.throughput]

            # if nodes dropout based on parameter selection
            if self.dropout:
                self.inactive_agents = self.inactive_agents + list(
                    filter(lambda a: a.capacity < parameter,
                           self.active_agents))
                self.active_agents = list(
                    filter(lambda a: a.capacity >= parameter,
                           self.active_agents))

                print("Active agents: {}".format(
                    list(map(lambda a: a.capacity, self.active_agents))))
                print("Inactive agents: {}".format(
                    list(map(lambda a: a.capacity, self.inactive_agents))))

                if payments:
                    payment_logs = list(map(lambda p: "Param {} => {}"
                                            .format(p[1], p[0]), payments))
                    print("\t\t\tPayments\n" + "\n".join(payment_logs))

    def step(self):
        # sample a leader uniformly at random
        if self.step_type == constants.UNIFORM_LEADER_ELECTION:
            leader = self.active_agents[np.random.choice(
                np.arange(0, len(self.active_agents)))]
            return leader.capacity, None

        # sample a leader proportional to an agent's capacity
        elif self.step_type == constants.WEIGHTED_LEADER_ELECTION:
            caps = list(map(lambda a: a.capacity, self.active_agents))
            weight_sum = sum(caps)
            distribution = [1.0 * i / weight_sum for i in caps]
            leader_index = np.random.choice(
                np.arange(0, len(caps), p=distribution))
            leader = self.active_agents[leader_index]
            return leader.capacity, None

        # elicit reports from all agents
        elif self.step_type == constants.ALL_REPORTS:
            # gather reports for current parameter
            reports = list(map(lambda a: a.report(
                self.gov.parameter), self.active_agents))

            # gather weights of agents
            caps = list(map(lambda a: a.capacity, self.active_agents))
            weight_sum = sum(caps)
            weights = [1.0 * i / weight_sum for i in caps]

            # advance round and receive new parameter given reports
            return self.gov.advance_round(reports, weights)
        else:
            value_error("Unsupported step type: {}", self.step_type)

    def plot_history(self):
        fig = plt.figure()
        plt.title("Throughput over {} simulation runs".format(self.num_times))

        means = []
        stds = []
        maxes = []
        mins = []
        for key in self.history.keys():
            means.append(np.mean(self.history[key]))
            stds.append(np.std(self.history[key]))
            maxes.append(np.max(self.history[key]))
            mins.append(np.min(self.history[key]))

        means = np.array(means)
        stds = np.array(stds)
        maxes = np.array(maxes)
        mins = np.array(mins)

        plt.plot(means)
        plt.errorbar(np.arange(len(means)), means, stds, fmt='ok', lw=3)
        plt.errorbar(np.arange(len(means)), means, [means - mins, maxes - means],
                     fmt='.k', ecolor='gray', lw=1)
        fig.savefig('temp.png', dpi=fig.dpi)
