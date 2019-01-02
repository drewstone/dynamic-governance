from sim import Simulator

if __name__ == "__main__":
    num_agents = 10
    low_capacity = 5
    high_capacity = 10
    agent_type = "honest-increasing"
    initial_param = 1
    num_rounds = 10
    report_type = "random-directional"
    step_type = "uniform-leader-election"
    decision_type = "majority"
    logging_mode = "debug"

    sim = Simulator({
        "num_agents": num_agents,
        "low_capacity": low_capacity,
        "high_capacity": high_capacity,
        "agent_type": agent_type,
        "num_rounds": num_rounds,
        "initial_param": initial_param,
        "report_type": report_type,
        "step_type": step_type,
        "decision_type": decision_type,
        "logging_mode": logging_mode
    })

    sim.start()
