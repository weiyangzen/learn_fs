# sources/storage-engines/foundationdb/fdbserver/workloads/SaveAndKill.cpp

## Purpose
`SaveAndKillWorkload` records enough simulation topology and restart metadata to an INI file, then reboots all non-excluded non-spawned processes and stops the simulator. It supports restart/restore simulation workflows.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SaveAndKill`. Important options are `restartInfoLocation`, `testDuration`, and `isRestoring`. The main logic is in `start`, using `CSimpleIni`, `g_simulator`, `FDBSimulationPolicyState`, `DatabaseConfiguration`, process locality, `INetworkConnections::convertMockDNSToString`, `SERVER_KNOBS`, and `FLOW_KNOBS`.

## Control Flow
Setup disables swaps to all. `start` waits a random fraction of `testDuration`, loads the restart INI, writes restore flags and metadata such as processes per machine, listeners per process, desired coordinators, connection string, tester count, TSS mode, mock DNS, and encryption/auth knob state. It gathers currently rebooting and active processes by data folder, writes machine and process address/data/coordination folder sections, saves the INI, reboots each process, yields for 100 zero-delay turns, and stops the simulator.

## State And Persistence Behavior
The main persistent output is the restart info INI file. It captures machine grouping, locality, process class, IP/port mappings, data folders, and coordination folders. Runtime state changes include process reboots and simulator stop. It disables all failure-injection workloads to reduce nondeterministic topology changes while snapshotting restart metadata.

## Dependencies And Integration Points
It integrates with restart tests, snapshot restore flows, simulator process metadata, connection-string policy state, mock DNS, encryption header token knobs, and SimpleIni. It filters out spawned KV processes and processes marked `excludeFromRestarts`.

## Risks And Edge Cases
`processCount` is written as `allProcessesMap.size() - 1`, which assumes one process should be excluded from the count. Process deduplication by data folder intentionally merges rebooting and active process records. Because it kills processes and stops simulation, it must run in scenarios expecting a restart boundary.

## Test Signals
`check` returns true. Correctness is observed indirectly by whether subsequent restart/restore phases can consume the generated INI and restart the simulated cluster.
