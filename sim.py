import statistics
import threading

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

        # initialize government
        self.dropout = False
        self.mine = True

    def start(self):
        # initialize histories for plotting
        self.history = {}

        for u_type in self.utility_types:
            for d_type in self.decision_types:
                self.run_many_times(self.initial_param, u_type, d_type)

        self.plot_history()

    def run_many_times(self, initial_param, u_type, d_type):
        for _ in range(self.num_times):
            self.run(self.initial_param, u_type, d_type)

    def run(self, initial_param, u_type, d_type):
        gov = Government({
            "initial_param": initial_param,
            "utility_type": u_type,
            "decision_type": d_type,
            "bounded_percent": self.bounded_perc,
        })

        active = self.active
        inactive = list()

        t_key = "{}-{}-throughput".format(u_type, d_type)
        self.history[t_key] = 0
        logger.init(self.logging_mode, gov, active)

        for i in range(self.num_rounds):
            r_key = "{}-{}-{}".format(u_type, d_type, i)
            logger.round(self.logging_mode, i, gov, self.history[t_key])
            # leader election proportional to agent capacities
            leader = statistics.sample_by_hashpower(active)
            param, payments = self.step(gov, leader, active, inactive)
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

            # if nodes dropout based on param selection
            if self.dropout:
                inactive = inactive + list(
                    filter(lambda a: a.capacity < param,
                           active))
                active = list(
                    filter(lambda a: a.capacity >= param,
                           active))

                logger.dropout(self.logging_mode, active, inactive)
                logger.payments(self.logging_mode, payments)

    def step(self, gov, leader, active, inactive):
        # gather reports for current param
        reports = list(map(lambda a: a.report(gov.param), active))
        # gather hash power reports
        hashes = list(map(lambda a: a.hash_power, active))
        # advance round and receive new param given reports
        return gov.advance_round(reports, hashes, leader)

    def plot_history(self):
        threads = []
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

        xy = np.vstack([pX, pY])
        z = gaussian_kde(xy)(xy)

        fig = plt.figure()
        title = "Throughput over {} simulation runs\n{} selection with {} utilities".format(self.num_times, d_type, u_type)
        plt.title(title)
        plt.scatter(pX, pY, c=z, s=100, edgecolor='')
        plt.colorbar()
        # plt.errorbar(np.arange(len(means)), means, stds, fmt='ok', lw=3)
        # plt.errorbar(np.arange(len(means)), means, [
        #              means - mins, maxes - means], fmt='.k', ecolor='gray', lw=1)
        file_path = 'images/{}-{}.png'.format(d_type, u_type)
        fig.savefig(file_path, dpi=fig.dpi)
