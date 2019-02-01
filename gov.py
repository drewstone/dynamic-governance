import vcg
import constants
from errors import value_error
import statistics


class Government(object):
    def __init__(self, options):
        super(Government, self).__init__()
        self.previous_parameter = None
        self.parameter = options["initial_param"]
        self.decision_type = options["decision_type"]
        self.utility_type = options["utility_type"]

        if self.decision_type == constants.SOCIAL_WELFARE_MAXIMIZING:
            self.VCG = vcg.VCGMechanism(self.utility_type)

        self.round = 0

    def advance_round(self, reports, weights):
        self.previous_parameter = self.parameter

        # move parameter according to majority
        self.parameter, payments = self.decide(reports, weights)

        if self.parameter < 0:
            self.parameter = 0

        return self.parameter, payments

    def decide(self, reports, weights):
        if self.decision_type == constants.MAJORITY_VOTE_DECISION:
            return self.incremental_vote(reports)
        elif self.decision_type == constants.SOCIAL_WELFARE_MAXIMIZING:
            return self.vcg_selection(reports)
        elif self.decision_type == constants.MEDIAN_REPORT:
            return self.median_vote(reports)
        elif self.decision_type == constants.LOWER_MEDIAN_REPORT:
            return self.lower_median_vote(reports)
        elif self.decision_type == constants.UPPER_MEDIAN_REPORT:
            return self.upper_median_vote(reports)
        elif self.decision_type == constants.WEIGHTED_MEDIAN_REPORT:
            return self.weighted_median_vote(reports, weights)
        elif self.decision_type == constants.HASHPOWER_CAPACITY_MAXIMIZING:
            return self.hash_cap_selection(reports, weights)
        else:
            value_error("Unsupported decision type: {}", self.decision_type)

    def incremental_vote(self, reports):
            # count votes of all participants based on capacity
            lost_count = len(list(filter(lambda r: r == 0, reports)))
            fixed_count = len(list(filter(lambda r: r == 1, reports)))
            surplus_count = len(list(filter(lambda r: r == 2, reports)))

            # find majority group from number of reports
            temp_arr = [lost_count, fixed_count, surplus_count]
            majority_index = temp_arr.index(max(temp_arr))

            if majority_index == 0:
                return self.parameter - 1, None
            if majority_index == 1:
                return self.parameter, None
            else:
                return self.parameter + 1, None

    def vcg_selection(self, reports):
        # find social welfare maximizing parameter given capacity reports
        (max_welfare, max_param) = self.VCG.select(reports)
        # get payments for strategy-proofness
        payments = self.VCG.payments(reports, max_welfare, max_param)
        return max_param, payments

    def median_report(self, reports):
        if len(reports) % 2 == 0:
            median = 0.5 * \
                (reports[int(len(reports) / 2) - 1] +
                 reports[int(len(reports) / 2)])
        else:
            median = reports[int(len(reports) / 2)]

        return median, None

    def lower_median_report(self, reports):
        if len(reports) % 2 == 0:
            median = reports[int(len(reports) / 2) - 1]
        else:
            median = reports[int(len(reports) / 2)]

        return median, None

    def upper_median_vote(self, reports):
        median = reports[int(len(reports) / 2)]
        return median, None

    def weighted_median_vote(self, reports, weights):
        w_median = int(statistics.wtd_median(reports, weights))
        return w_median, None
