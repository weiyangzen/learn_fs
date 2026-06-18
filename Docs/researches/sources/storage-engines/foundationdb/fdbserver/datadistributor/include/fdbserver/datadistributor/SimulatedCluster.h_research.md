# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/SimulatedCluster.h

Purpose: declares a compact simulation configuration interface used by DD tests and mock global-state setup.

Important APIs and types: `simulationSetupAndRun()` is the fdbserver simulation entry point declared here. `SimulationStorageEngine` enumerates storage backends. `BasicTestConfig` contains replication, anti-quorum, simplification, region, role-count, machine-count, coordinator, storage-engine, and ASAN machine-count options. `BasicSimulationConfig` contains datacenter count, replication type, machine count, processes per machine, and `DatabaseConfiguration`. `generateBasicSimulationConfig()` converts test config to simulation config.

Control flow: callers fill `BasicTestConfig`, call `generateBasicSimulationConfig()`, and feed the result to mock or simulation setup. `simulationSetupAndRun()` is declared for `fdbserver -r simulation` usage.

State and persistence: the structs are value-only configuration state. There is no persistence.

Dependencies and integration: includes `DatabaseConfiguration` and Flow `Optional`. `MockGlobalState` consumes `BasicSimulationConfig` to create topology and initial servers.

Risks: this header does not enforce consistency beyond types; validation occurs in the implementation and downstream assertions. Some fields, such as `asanMachineCount`, are declared but not consumed by the current `generateBasicSimulationConfig()` implementation in this subset.

Test signals: compile coverage plus config-generation tests for replication modes, simple configs, single-region behavior, and optional override fields.
