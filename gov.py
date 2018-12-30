class Government(object):
    def __init__(self, options):
        super(Government, self).__init__()
        self.parameter = options["initial_param"]
        self.report_type = options["report_type"]
        self.decision_type = options["decision_type"]

        # initialize government benchmarks and system parameters
        self.throughput = 0
        self.decentralization = 0
        self.round = 0
    
    def advance_round(self, reports):
        self.previous_parameter = self.parameter
        if self.report_type in ["directional", "random-directional"]:
            # throughput is increased by previous rounds parameter
            self.throughput += self.parameter
            # decentralization is increased by nodes with sufficient capacity
            self.decentralization += len(list(filter(lambda r: r != 0, reports)))
            # move parameter according to majority
            self.parameter = self.decide(reports)

            if self.parameter < 0: self.parameter = 0
        else:
            raise ValueError("Unsupported report type: {}".format(self.report_type))
        
        # increment round and return parameter
        self.round += 1
        return self.parameter

    def decide(self, reports):
        if self.decision_type == "majority":
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
        else:
            raise ValueError("Unsupported decision type: {}".format(self.decision_type))