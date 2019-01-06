import copy
import constants
from errors import value_error


def social_maximizing_alternative(reports):
    # reports are numbers (integers for simplicity)
    max_welfare = 0
    param = 0

    # find social welfare maximizing parameter given capacity reports
    for inx, elt in enumerate(sorted(reports)):
        if (len(reports) - inx) * elt > max_welfare:
            max_welfare = (len(reports) - inx) * elt
            param = elt

    return (max_welfare, param)


def vcg_payments(reports, welfare, alternative):
    payments = []
    for inx, elt in enumerate(sorted(reports)):
        if sorted(reports)[inx] < alternative:
            payments.append(0)
        else:
            reports_without_i = copy.deepcopy(reports)
            reports_without_i.remove(elt)
            (welfare_without_i, param) = social_maximizing_alternative(
                reports_without_i)
            payments.append(welfare_without_i - (welfare - alternative))
    return payments


class Government(object):
    def __init__(self, options):
        super(Government, self).__init__()
        self.previous_parameter = None
        self.parameter = options["initial_param"]
        self.report_type = options["report_type"]
        self.decision_type = options["decision_type"]

        # initialize government benchmarks and system parameters
        self.throughput = 0
        self.decentralization = 0
        self.round = 0

    def advance_round(self, reports):
        self.previous_parameter = self.parameter
        # throughput is increased by previous rounds parameter
        self.throughput += self.parameter
        # decentralization is increased by nodes with sufficient capacity
        self.decentralization += len(
            list(filter(lambda r: r != 0, reports)))
        # move parameter according to majority
        self.parameter, _ = self.decide(reports)

        if self.parameter < 0:
            self.parameter = 0

        # increment round and return parameter
        self.round += 1
        return self.parameter

    def decide(self, reports):
        if self.decision_type == constants.MAJORITY_VOTE_DECISION:
            # count votes of all participants based on capacity
            lost_count = len(list(filter(lambda r: r == 0, reports)))
            fixed_count = len(list(filter(lambda r: r == 1, reports)))
            surplus_count = len(list(filter(lambda r: r == 2, reports)))

            # find majority group from number of reports
            temp_arr = [lost_count, fixed_count, surplus_count]
            majority_index = temp_arr.index(max(temp_arr))

            if majority_index == 0:
                return self.parameter - 1
            if majority_index == 1:
                return self.parameter
            else:
                return self.parameter + 1
        elif self.decision_type == constants.SOCIAL_WELFARE_MAXIMIZING:
            # find social welfare maximizing parameter given capacity reports
            (max_welfare, max_param) = social_maximizing_alternative(reports)
            print(max_welfare, max_param)
            payments = vcg_payments(reports, max_welfare, max_param)
            return max_param, payments
        else:
            value_error("Unsupported decision type: {}", self.decision_type)
