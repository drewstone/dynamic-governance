import numpy as np

class Government(object):
    def __init__(self, initial_parameter, report_type, decision_type):
        self.parameter = initial_parameter
        self.throughput = 0
        self.decentralization = 0
        self.round = 0
        self.report_type = report_type
        self.decision_type = decision_type
    
    def advance_round(self, reports):
        self.previous_parameter = self.parameter
        if self.report_type == "directional" or not self.report_type:
            # throughput is increased by previous rounds parameter
            self.throughput += self.parameter
            # decentralization is increased by nodes with sufficient capacity
            self.decentralization += len(list(filter(lambda r: r != 0, reports)))
            # move parameter according to majority
            self.parameter = self.decide(reports)
        
        self.round += 1
        return self.parameter

    def decide(self, reports):
        if self.decision_type == "majority" or not self.decision_type:
            # count votes of all participants based on capacity
            lost_count = len(list(filter(lambda r: r == 0, reports)))
            fixed_count = len(list(filter(lambda r: r == 1, reports)))
            surplus_count = len(list(filter(lambda r: r == 2, reports)))

            # find majority group from number of reports
            temp_arr = [lost_count, fixed_count, surplus_count]
            majority_index = temp_arr.index(max(temp_arr))

            if  majority_index == 0:
                return self.parameter - 1
            if majority_index == 1:
                return self.parameter
            else:
                return self.parameter + 1


class Simulator(object):
    def __init__(self, capacities, initial_param, num_rounds, report_type, decision_type):
        self.node_capacities = capacities;
        self.gov = Government(initial_param, report_type, decision_type)
        self.num_rounds = num_rounds
        self.report_type = report_type
    
    def start(self):
        print("Node capacities = {}".format(self.node_capacities))
        for i in range(num_rounds):
            self.step()

    def step(self):
        reports = self.node_reports(self.gov.parameter)
        parameter = self.gov.advance_round(reports)

        print("Round {} | NEW_P = {}, OLD_P = {}, TPS = {}, DEC = {}".format(
            self.gov.round,
            self.gov.parameter,
            self.gov.previous_parameter,
            self.gov.throughput,
            self.gov.decentralization))


    def node_reports(self, parameter):
        # directional reports for increasing, decreasing, or fixing parameter
        if self.report_type == "directional":
            # {0,1,2} if the capacity is {<, ==, >} current paramter
            return list(map(
                lambda c: 0 if c < parameter
                          else 1 if c == parameter
                          else 2,
                self.node_capacities
                )
            )


def random_node_capacities(n, low, high):
    return np.random.randint(low, high+1, n)

def increasing_node_capacities(n, start):
    return np.arange(start, start + n)

if __name__ == "__main__":
    capacities = increasing_node_capacities(10, 5)
    initial_param = 1
    num_rounds = 10
    report_type = "directional"
    decision_type = "majority"
    logging_mode = "debug"

    sim = Simulator(capacities,
                    initial_param,
                    num_rounds,
                    report_type,
                    decision_type,
                    logging_mode)
    
    sim.start()