from constants import HONEST_RANDOM_AGENTS, DIRECT_CAPACITY_REPORT
from constants import ALL_REPORTS, SOCIAL_WELFARE_MAXIMIZING
from constants import DEBUG_LOGGING
from sim import Simulator

if __name__ == "__main__":
    num_agents = 10
    low_capacity = 5
    high_capacity = 100
    agent_mode = HONEST_RANDOM_AGENTS

    EXPLICIT_CAPACITIES = []
    # EXPLICIT_CAPACITIES = [5, 22, 30, 33, 74, 92, 93, 97, 97, 99]

    initial_param = 0
    num_rounds = 2
    report_type = DIRECT_CAPACITY_REPORT
    step_type = ALL_REPORTS
    decision_type = SOCIAL_WELFARE_MAXIMIZING
    logging_mode = DEBUG_LOGGING

    sim = Simulator({
        "num_agents": num_agents,
        "low_capacity": low_capacity,
        "high_capacity": high_capacity,
        "agent_mode": agent_mode,
        "num_rounds": num_rounds,
        "initial_param": initial_param,
        "report_type": report_type,
        "step_type": step_type,
        "decision_type": decision_type,
        "logging_mode": logging_mode,

        "EXPLICIT_CAPACITIES": EXPLICIT_CAPACITIES
    })

    sim.start()
