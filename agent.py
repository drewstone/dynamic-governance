import numpy as np

class Agent(object):
	"""An agent represents an atomic participant in a governance simulation"""
	def __init__(self, type, capacity, report_type):
		super(Agent, self).__init__()
		self.type = type
		self.capacity = capacity
		self.report_type = report_type
	
	def report(self, parameter):
		if self.type == "random":
			return np.random.choice(self.feasible_reports())
		if self.type == "honest":
			return self.honest_report(parameter)

	def feasible_reports(self):
		if self.report_type in ["directional", "random-directional"]:
			return [0,1,2]
		else:
			raise ValueError("Unsupported report type {}".format(self.report_type))

	def honest_report(self, parameter):
		if self.report_type in ["directional", "random-directional"]:
			return (0 if self.capacity < parameter
				else 1 if self.capacity == parameter
				else 2)
		else:
			raise ValueError("Unsupported report type {}".format(self.report_type))