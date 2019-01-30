import numpy as np
import constants
from errors import value_error


class Agent(object):
    """An agent represents an atomic participant in a governance simulation"""

    def __init__(self, ttype, capacity, report_type):
        super(Agent, self).__init__()
        self.ttype = ttype
        self.capacity = capacity
        self.hash_power = 3 * capacity
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
