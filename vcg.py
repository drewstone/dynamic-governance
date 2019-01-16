import constants
import copy


def linear_valuation_vcg(rs, inx, elt):
    return (len(rs) - inx) * elt


def proportional_valuation_vcg(rs, elt):
    # utilities are all 1 at their report with proportional utilties below
    return sum(list(map(lambda r: elt * 1.0 / r if r >= elt else 0.0, rs)))


class VCGMechanism(object):
    """docstring for VCGMechanism"""

    def __init__(self, utility_type):
        super(VCGMechanism, self).__init__()
        self.utility_type = utility_type

    def payments(self, reports, welfare, alternative):
        payments = []
        for inx, elt in enumerate(sorted(reports)):
            if sorted(reports)[inx] < alternative:
                payments.append((0, elt))
            else:
                reports_without_i = copy.deepcopy(reports)
                reports_without_i.remove(elt)
                (welfare_without_i, param) = self.select(reports_without_i)

                # TODO: Fix the right hand term summation
                if self.utility_type == constants.LINEAR_UTILITY:
                    payments.append((welfare_without_i -
                                     welfare -
                                     alternative,
                                     elt))
                elif self.utility_type == constants.PROPORTIONAL_UTILITY:
                    payments.append((welfare_without_i -
                                     welfare -
                                     alternative * 1.0 / elt,
                                     elt))
        return payments

    def select(self, reports):
        # reports are numbers (integers for simplicity)
        max_welfare = 0
        param = 0

        # find social welfare maximizing parameter given capacity reports
        for inx, elt in enumerate(sorted(reports)):
            if self.utility_type == constants.LINEAR_UTILITY:
                if linear_valuation_vcg(reports, inx, elt) > max_welfare:
                    max_welfare = linear_valuation_vcg(reports, inx, elt)
                    param = elt
            elif self.utility_type == constants.PROPORTIONAL_UTILITY:
                if proportional_valuation_vcg(reports, elt) > max_welfare:
                    max_welfare = proportional_valuation_vcg(reports, elt)
                    param = elt

        return max_welfare, param
