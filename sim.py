import numpy as np
from gov import Government
import statistics
import logger
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt  # noqa


class Simulator(object):
    def __init__(self, options):
        super(Simulator, self).__init__()
        self.initial_param = options["initial_param"]
        self.active = options["agents"]
        self.inactive = list()
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
                for i in range(self.num_times):
                    self.run(self.initial_param, u_type, d_type)

        self.plot_history()

    def run(self, initial_param, u_type, d_type):
        gov = Government({
            "initial_param": initial_param,
            "utility_type": u_type,
            "decision_type": d_type,
            "bounded_percent": self.bounded_perc,
        })

        t_key = "{}-{}-throughput".format(u_type, d_type)
        self.history[t_key] = 0
        logger.init(self.logging_mode, gov, self.active)

        for i in range(self.num_rounds):
            r_key = "{}-{}-{}".format(u_type, d_type, i)
            logger.round(self.logging_mode, gov, self.history[t_key])

            # leader election proportional to agent capacities
            leader = statistics.sample_by_hashpower(self.active)
            param, payments = self.step(gov, leader)

            # increment throughput based on leader election
            if leader.capacity < param:
                increment = 0
            else:
                increment = param

            if r_key in self.history:
                self.history[r_key].append(increment)
            else:
                self.history[r_key] = [increment]

            # if nodes dropout based on param selection
            if self.dropout:
                self.inactive = self.inactive + list(
                    filter(lambda a: a.capacity < param,
                           self.active))
                self.active = list(
                    filter(lambda a: a.capacity >= param,
                           self.active))

                logger.dropout(self.logging_mode, self.active, self.inactive)
                logger.payments(self.logging_mode, payments)

    def step(self, gov, leader):
        # gather reports for current param
        reports = list(map(lambda a: a.report(gov.param), self.active))
        # gather hash power reports
        hashes = list(map(lambda a: a.hash_power, self.active))
        # advance round and receive new param given reports
        return gov.advance_round(reports, hashes, leader)

    def plot_history(self):
        means = {}
        stds = {}
        maxes = {}
        mins = {}

        # iterate over supported utility and decision types
        for u_type in self.utility_types:
            for d_type in self.decision_types:
                index_key = "-".join([u_type, d_type])
                if index_key not in means:
                    means[index_key] = []
                if index_key not in stds:
                    stds[index_key] = []
                if index_key not in maxes:
                    maxes[index_key] = []
                if index_key not in mins:
                    mins[index_key] = []

                # get statistics for each utility and decision type
                for i in range(self.num_rounds):
                    history_key = "-".join([u_type, d_type, str(i)])

                    means[index_key].append(np.mean(self.history[history_key]))
                    stds[index_key].append(np.std(self.history[history_key]))
                    maxes[index_key].append(np.max(self.history[history_key]))
                    mins[index_key].append(np.min(self.history[history_key]))

                means[index_key] = np.array(means[index_key])
                stds[index_key] = np.array(stds[index_key])
                maxes[index_key] = np.array(maxes[index_key])
                mins[index_key] = np.array(mins[index_key])

                fig = plt.figure()
                plt.title("Throughput over {} simulation runs\n"
                          .format(self.num_times) +
                          "{} selection with {} utilities"
                          .format(d_type, u_type))

                # plt.plot(means)
                plt.errorbar(np.arange(len(means[index_key])),
                             means[index_key],
                             stds[index_key],
                             fmt='ok',
                             lw=3)
                plt.errorbar(np.arange(len(means[index_key])),
                             means[index_key],
                             [means[index_key] - mins[index_key],
                                 maxes[index_key] - means[index_key]],
                             fmt='.k',
                             ecolor='gray',
                             lw=1)
                fig.savefig('{}-{}.png'.format(d_type, u_type), dpi=fig.dpi)
