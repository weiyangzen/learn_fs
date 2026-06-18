# sources/storage-engines/foundationdb/fdbserver/core/SimulatorSupport.cpp

## sources/storage-engines/foundationdb/fdbserver/core/SimulatorSupport.cpp

Purpose: provides a tiny helper for checking whether the current simulated process is unreliable.

Important API: `isSimulatorProcessUnreliable`.

Control flow and state: the function returns true only when `g_network->isSimulated()` and the current simulator process reports `!isReliable()`. It reads simulator state and does not mutate anything.

Dependencies and integration: depends on `fdbrpc/simulator.h`, `SimulatorProcessInfo`, and Flow network globals. Callers can use it to gate behavior that should differ for unreliable simulated processes.

Risks and tests: it assumes `g_simulator->getCurrentProcess()` is valid whenever the network is simulated. Test signal is simulation-only coverage that calls this from reliable and unreliable process contexts; production should always return false because `isSimulated()` is false.
