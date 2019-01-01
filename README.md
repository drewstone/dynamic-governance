# dynamic-governance
This repo contains a simulation environment for dynamic parameter adjustment over a multi-agent system. The goal of this project is to analyze the dynamics of a multi-agent system that attempts to adjust a system parameter that governs the throughput and decentralization of such a decentralized system.

Some behavior we want to support:
- Honest behavior (agents submit truthful values)
- Strategic behavior (agents submit values that maximize individual utility)
- Byzantine/malicious behavior (agents submit random/malicious values)

Overall, the question we want to ask is: How can we use adapative governance to optimize a distributed system. When there is a system designer (termed the "mechanism designer") with various goals, we want to optimize these goals given agent input. For a set of altruistic, rational/strategic, and even byzantine agents, we want to define a protocol that elicits informational reports to seed the mechanism designer's governance process.