import numpy as np

class Government(object):
    __init__(self, initial_parameter, report_type, decision_type):
        self.parameter = initial_parameter
        self.throughput = 0
        self.decentralization = 0
        self.round = 0
        self.report_type = report_type
        self.decision_type = decision_type
    
    def advance_round(self, reports):
        if self.report_type == "directional":
            # throughput is increased by previous rounds parameter
            self.throughput += self.parameter
            # decentralization is increased by nodes with sufficient capacity
            self.decentralization += len(list(map(lambda r: r != 0, reports)))
            # move parameter according to majority
            self.parameter = self.decide(reports)

    def decide(self, reports):
        if self.decision_type == "majority":
            # count votes of all participants based on capacity
            lost_count = len(list(map(lambda r: r == 0, reports)))
            fixed_count = len(list(map(lambda r: r == 1, reports)))
            surplus_count = len(list(map(lambda r: r == 2, reports)))

            # find majority group from number of reports
            temp_arr = [lost_count, fixed_count, surplus_count]
            majority_index = temp_arr.index(max(temp_arr))

            if  majority_index == 0:
                return self.parameter - 1
            if majority_index == 1:
                return self.parameter
            else:
                return self.parameter


class Simulator(object):
    __init__(self, capacities, initial_param, num_rounds, report_type):
        self.node_capacities = capacities;
        self.governor = Government(initial_param)
        self.num_rounds = num_rounds
        self.report_type = report_type
    
    def start(self):
        for i in range(num_rounds):

    
    def step(self):
        reports = self.node_reports(self.governor.parameter)
        parameter = self.governor.decide(reports)

    def node_reports(self, parameter):
        # directional reports for increasing, decreasing, or fixing parameter
        if self.report_type == "directional":
            # {0,1,2} if the capacity is {<, ==, >} current paramter
            reports = list(map(
                lambda c: 0 if c < parameter
                          else 1 if c == parameter
                          else 2,
                node_capacities
                )
            )


def random_node_capacities(n, low, high):
    return np.random.randint(low, high+1, n)

def increasing_node_capacities(n, start):
    return np.arange(start, start + n)

if __name__ == "__main__":
    print(random_node_capacities(10, 5, 10))
    print(increasing_node_capacities(10, 5))