import constants


def init(mode, gov, agents):
    if mode == constants.DEBUG_LOGGING:
        print("Agents = {}".format(
            list(map(lambda agent: agent.capacity, agents))))
        print("Starting param: {}".format(gov.param))


def round(mode, round, gov, throughput):
    if mode == constants.DEBUG_LOGGING:
        print("\nRound {} | OLD_P = {}, NEW_P = {}, TPS = {}, RULE = {}\n"
              .format(round,
                      gov.prev_param,
                      gov.param,
                      throughput,
                      gov.decision_type))


def dropout(mode, active, inactive):
    if mode == constants.DEBUG_LOGGING:
        print("Active agents: {}".format(
            list(map(lambda a: a.capacity, active))))
        print("Inactive agents: {}".format(
            list(map(lambda a: a.capacity, inactive))))


def payments(mode, payments):
    if mode == constants.DEBUG_LOGGING:
        if payments:
            payment_logs = list(map(lambda p: "Param {} => {}"
                                    .format(p[1], p[0]), payments))
            print("\t\t\tPayments\n" + "\n".join(payment_logs))
