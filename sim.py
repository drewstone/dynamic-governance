import statistics
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt  # noqa
import numpy as np

import logger
from gov import Government
from scipy.stats import gaussian_kde


class Simulator(object):
    def __init__(self, options):
        super(Simulator, self).__init__()
        self.initial_param = options["initial_param"]
        self.active = options["agents"]
        self.num_rounds = options["num_rounds"]
        self.num_times = options["num_times"]
        self.logging_mode = options["logging_mode"]
        self.utility_types = options["utility_types"]
        self.decision_types = options["decision_types"]
        self.bounded_perc = options["bounded_percent"]
        self.suppress_perc = options["suppress_percent"]
        self.mutation_rule = options["mutation_rule"]

        # initialize government
        self.dropout = True
        self.mine = True

    def start(self):
        # initialize histories for plotting
        self.history = {}
        self.govs = {}
        self.actives = {}
        self.inactives = {}
        for u_type in self.utility_types:
            for d_type in self.decision_types:
                key = "{}-{}".format(u_type, d_type)
                self.govs[key] = Government({
                    "initial_param": self.initial_param,
                    "utility_type": u_type,
                    "decision_type": d_type,
                    "bounded_percent": self.bounded_perc,
                    "suppress_percent": self.suppress_perc,
                })

                self.actives[key] = self.active
                self.inactives[key] = list()

        for _ in range(self.num_times):
            for i in range(self.num_rounds):
                self.run_round(i)

        self.plot_history()

    def run_round(self, i):
        if not self.dropout:
            leader = statistics.sample_by_hashpower(self.active)
        else:
            leader = None

        for u_type in self.utility_types:
            for d_type in self.decision_types:
                self.run(self.govs["{}-{}".format(u_type, d_type)], leader, i)
        
        self.actives = self.mutate_active_agents()

    def run(self, gov, leader, round):
        if leader is None:
            leader = statistics.sample_by_hashpower(self.actives[gov.prefix])

        t_key = "{}-throughput".format(gov.prefix)
        if t_key not in self.history:
            self.history[t_key] = 0

        logger.init(self.logging_mode, gov, self.actives[gov.prefix])

        r_key = "{}-{}".format(gov.prefix, round)
        logger.round(self.logging_mode, round, gov, self.history[t_key])
        param, payments = self.step(gov, leader, self.actives[gov.prefix], self.inactives[gov.prefix])
        # increment throughput based on leader election
        if leader.capacity < param:
            increment = 0
        else:
            increment = param

        self.history[t_key] += increment

        if r_key in self.history:
            self.history[r_key].append(increment)
        else:
            self.history[r_key] = [increment]

        self.mutate_active_agents(gov)

    def step(self, gov, leader, active, inactive):
        # gather reports for current param
        reports = list(map(lambda a: a.report(gov.param), active))
        # gather hash power reports
        hashes = list(map(lambda a: a.hash_power, active))
        # advance round and receive new param given reports
        return gov.advance_round(reports, hashes, leader)

    def mutate_active_agents(self, gov):
        if self.mutation_rule == "CYCLE_ONE_AGENT":
            let rand_inx = np.random.choice(np.arange(0, len(self.actives[gov.prefix])))
            return 
        elif self.mutation_rule == "CAPACITY_CYCLE":
        if self.dropout:
            self.inactives[gov.prefix] = self.inactives[gov.prefix] + list(
                filter(lambda a: a.capacity < param,
                        self.actives[gov.prefix]))
            self.actives[gov.prefix] = list(
                filter(lambda a: a.capacity >= param,
                        self.actives[gov.prefix]))

            logger.dropout(self.logging_mode, self.actives[gov.prefix], self.inactives[gov.prefix])
            logger.payments(self.logging_mode, payments)
        else:
            return self.actives
            

    def plot_history(self):
        for u_type in self.utility_types:
            for d_type in self.decision_types:
                self.plot_chart(u_type, d_type)

    def plot_chart(self, u_type, d_type):
        means, stds, maxes, mins = [], [], [], []
        pX, pY = [], []

        # get statistics for each utility and decision type
        for i in range(self.num_rounds):
            history_key = "-".join([u_type, d_type, str(i)])

            for p in self.history[history_key]:
                pX.append(i)
                pY.append(p)

            means.append(np.mean(self.history[history_key]))
            stds.append(np.std(self.history[history_key]))
            maxes.append(np.max(self.history[history_key]))
            mins.append(np.min(self.history[history_key]))

        means = np.array(means)
        stds = np.array(stds)
        maxes = np.array(maxes)
        mins = np.array(mins)

        # xy = np.vstack([pX, pY])
        # z = gaussian_kde(xy)(xy)

        fig = plt.figure()
        title = "Throughput over {} simulation runs\n{} selection with {} utilities".format(self.num_times, d_type, u_type)
        plt.title(title)
        # plt.scatter(pX, pY, c=z, s=100, edgecolor='')
        # plt.colorbar()
        plt.errorbar(np.arange(len(means)), means, stds, fmt='ok', lw=3)
        plt.errorbar(np.arange(len(means)), means, [
                     means - mins, maxes - means], fmt='.k', ecolor='gray', lw=1)
        file_path = 'images/{}-{}.png'.format(d_type, u_type)
        fig.savefig(file_path, dpi=fig.dpi)