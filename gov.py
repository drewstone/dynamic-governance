import vcg
import constants
from errors import value_error
import statistics


class Government(object):
    def __init__(self, options):
        super(Government, self).__init__()
        self.prev_param = None
        self.param = options["initial_param"]
        self.decision_type = options["decision_type"]
        self.utility_type = options["utility_type"]
        self.bounded_perc = options["bounded_percent"]

        if not self.bounded_perc:
            self.bounded_perc = 0.1

        if self.decision_type == constants.SOCIAL_WELFARE_MAXIMIZING:
            self.VCG = vcg.VCGMechanism(self.utility_type)

        self.round = 0

    def advance_round(self, reports, hashes, leader):
        self.prev_param = self.param

        # move parameter according to majority
        self.param, payments = self.decide(reports, hashes, leader)
        # safety check
        if self.param < 0:
            self.param = 0
        # return parameter and payments
        return self.param, payments

    def decide(self, reports, hashes, leader):
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
            return self.weighted_median_vote(reports, hashes)
        elif self.decision_type == constants.HASHPOWER_CAPACITY_MAXIMIZING:
            return self.fractional_hash_cap_selection(reports, hashes)
        elif self.decision_type == constants.FRACTIONAL_HASHCAP_MAXIMIZING:
            return self.hash_cap_selection(reports, hashes)
        elif self.decision_type == constants.LEADER_REPORT:
            return self.leader_report(leader)
        elif self.decision_type == constants.BOUNDED_LEADER_REPORT:
            return self.bounded_leader_report(leader)
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
            return self.param - 1, None
        if majority_index == 1:
            return self.param, None
        else:
            return self.param + 1, None

    def vcg_selection(self, reports):
        # find social welfare maximizing parameter given capacity reports
        (max_welfare, max_param) = self.VCG.select(reports)
        # get payments for strategy-proofness
        payments = self.VCG.payments(reports, max_welfare, max_param)
        return max_param, payments

    def median_vote(self, reports):
        if len(reports) % 2 == 0:
            median = 0.5 * \
                (reports[int(len(reports) / 2) - 1] +
                 reports[int(len(reports) / 2)])
        else:
            median = reports[int(len(reports) / 2)]

        return median, None

    def lower_median_vote(self, reports):
        if len(reports) % 2 == 0:
            median = reports[int(len(reports) / 2) - 1]
        else:
            median = reports[int(len(reports) / 2)]

        return median, None

    def upper_median_vote(self, reports):
        median = reports[int(len(reports) / 2)]
        return median, None

    def weighted_median_vote(self, reports, hashes):
        weight_sum = sum(hashes)
        weights = [1.0 * i / weight_sum for i in hashes]
        w_median = int(statistics.wtd_median(reports, weights))
        return w_median, None

    def hash_cap_selection(self, reports, hashes):
        max_cap = 0
        max_obj = 0
        for i in range(len(reports)):
            capacity = reports[i]
            summed_hashpower = 0
            for j in range(len(reports)):
                c = reports[j]
                h = hashes[j]

                if c >= capacity:
                    summed_hashpower += h * capacity

            if summed_hashpower > max_obj:
                max_cap = capacity
                max_obj = summed_hashpower

        return max_cap, None

    def fractional_hash_cap_selection(self, reports, hashes):
        max_cap = 0
        max_obj = 0
        total_sum = sum([hashes[i] for i in range(len(reports))])
        for i in range(len(reports)):
            capacity = reports[i]
            for j in range(len(reports)):
                hash_sum = sum([hashes[i] for i in range(
                    len(reports)) if reports[i] >= capacity])
                frac_utility = (1.0 * hash_sum / total_sum) * capacity

            if frac_utility > max_obj:
                max_cap = capacity
                max_obj = frac_utility

        return max_cap, None

    def leader_report(self, leader):
        return leader.capacity, None

    def bounded_leader_report(self, leader):
        if leader.capacity > self.prev_param * (1 + self.bounded_perc):
            return self.prev_param * (1 + self.bounded_perc), None
        elif leader.capacity < self.prev_param * (1 - self.bounded_perc):
            return self.prev_param * (1 - self.bounded_perc), None
        else:
            return leader.capacity, None
