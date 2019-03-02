import statistics
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt  # noqa
import numpy as np
import agent
import constants
import logger
from gov import Government
from scipy.stats import gaussian_kde

class Simulator(object):
    def __init__(self, options):
        super(Simulator, self).__init__()
        self.initial_param = options["initial_param"]
        self.agent_options = options["agent_options"]
        self.num_rounds = options["num_rounds"]
        self.num_times = options["num_times"]
        self.logging_mode = options["logging_mode"]
        self.utility_types = options["utility_types"]
        self.decision_types = options["decision_types"]
        self.bounded_perc = options["bounded_percent"]
        self.suppress_perc = options["suppress_percent"]
        self.mutation_rule = options["mutation_rule"]

        # initialize government
        self.mine = True
        # setup agents
        self.active = agent.setup_agents(self.agent_options)

    def start(self):
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

        # initialize histories for plotting
        self.total_history = {}
        for execution_number in range(self.num_times):
            self.history = {}
            for i in range(self.num_rounds):
                for u_type in self.utility_types:
                    for d_type in self.decision_types:
                        sim_type = "{}-{}".format(u_type, d_type)
                        if i == 0:
                            self.history[sim_type] = {}
                            self.govs[sim_type].reset()
                        self.run(self.govs[sim_type])

            self.total_history[execution_number] = self.history

        self.gather_statistics()

    def run(self, gov):
        leader = statistics.sample_by_hashpower(self.actives[gov.prefix])

        if "throughput" not in self.history[gov.prefix]:
            self.history[gov.prefix]["throughput"] = 0.0

        logger.init(self.logging_mode, gov, self.actives[gov.prefix])

        # logger.round(self.logging_mode, execution_number, gov, self.history[t_key])
        param = self.step(gov, leader, self.actives[gov.prefix], self.inactives[gov.prefix])
        # increment throughput based on leader election
        if leader.capacity < param:
            increment = 0
        else:
            increment = param

        self.history[gov.prefix]["throughput"] += increment

        if "pts" in self.history[gov.prefix]:
            self.history[gov.prefix]["pts"].append(increment)
        else:
            self.history[gov.prefix]["pts"] = [increment]

    def step(self, gov, leader, active, inactive):
        # gather reports for current param
        reports = list(map(lambda a: a.report(gov.param), active))
        # gather hash power reports
        hashes = list(map(lambda a: a.hash_power, active))
        # advance round and receive new param given reports
        param, payments =  gov.advance_round(reports, hashes, leader)
        # mutate agents after gov has advanced round
        self.mutate_active_agents(gov, payments)
        return param

    def mutate_active_agents(self, gov, payments):
        if self.mutation_rule == constants.CYCLE_ONE_AGENT:
            rand_inx = np.random.choice(np.arange(0, len(self.actives[gov.prefix])))
            mutate_options = self.agent_options.copy()
            mutate_options.update({ "num_agents": 1 })
            self.actives[gov.prefix][rand_inx] = agent.setup_agents(mutate_options)[0]
        elif self.mutation_rule == constants.CAPACITY_CYCLE:
            self.inactives[gov.prefix] = self.inactives[gov.prefix] + list(
                filter(lambda a: a.capacity < gov.param,
                        self.actives[gov.prefix]))
            self.actives[gov.prefix] = list(
                filter(lambda a: a.capacity >= gov.param,
                        self.actives[gov.prefix]))

            logger.dropout(self.logging_mode, self.actives[gov.prefix], self.inactives[gov.prefix])
            logger.payments(self.logging_mode, payments)
        else:
            return self.actives

    def gather_statistics(self):
        for execution_number in range(self.num_times):
            for u_type in self.utility_types:
                for d_type in self.decision_types:
                    sim_type = "{}-{}".format(u_type, d_type)
                    if "means" not in self.total_history[execution_number][sim_type]:
                        self.total_history[execution_number][sim_type].update({
                            "means": [],
                            "stds": [],
                            "maxes": [],
                            "mins": [],
                        });

                    self.total_history[execution_number][sim_type]["means"].append(np.mean(self.total_history[execution_number][sim_type]["pts"]))
                    self.total_history[execution_number][sim_type]["stds"].append(np.std(self.total_history[execution_number][sim_type]["pts"]))
                    self.total_history[execution_number][sim_type]["maxes"].append(np.max(self.total_history[execution_number][sim_type]["pts"]))
                    self.total_history[execution_number][sim_type]["mins"].append(np.min(self.total_history[execution_number][sim_type]["pts"]))

                    # self.plot_chart(u_type, d_type)
                    self.total_history[execution_number][sim_type]["pts"] = np.array(self.total_history[execution_number][sim_type]["pts"])
                    self.total_history[execution_number][sim_type]["means"] = np.array(self.total_history[execution_number][sim_type]["means"])
                    self.total_history[execution_number][sim_type]["stds"] = np.array(self.total_history[execution_number][sim_type]["stds"])
                    self.total_history[execution_number][sim_type]["maxes"] = np.array(self.total_history[execution_number][sim_type]["maxes"])
                    self.total_history[execution_number][sim_type]["mins"] = np.array(self.total_history[execution_number][sim_type]["mins"])
                    print("Execution Num: {}, Throughput: {}, Type: {}".format(
                        execution_number + 1, self.total_history[execution_number][sim_type]["throughput"], sim_type))

                    if sim_type not in self.total_history:
                        self.total_history[sim_type] = {}

                    if "mean_throughput" not in self.total_history[sim_type]:
                        self.total_history[sim_type]["mean_throughput"] = self.total_history[execution_number][sim_type]["throughput"] * 1.0
                    else:
                        fractional_term = (self.total_history[execution_number][sim_type]["throughput"] * 1.0 - self.total_history[sim_type]["mean_throughput"]) /(execution_number + 1)
                        self.total_history[sim_type]["mean_throughput"] = self.total_history[sim_type]["mean_throughput"] + (fractional_term)

        for u_type in self.utility_types:
            for d_type in self.decision_types:
                sim_type = "{}-{}".format(u_type, d_type)
                print("Mean throughput: {}, Type: {}".format(self.total_history[sim_type]["mean_throughput"], sim_type))

    def plot_chart(self, u_type, d_type):
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