# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/FDBSimulationPolicy.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/FDBSimulationPolicy.h

Purpose: declares global simulation policy state and helpers used by FoundationDB simulation tests to configure replication, extra databases, backup/DR agents, TSS fault modes, consistency scan corruption, targeted restarts/delays, and restart/quiescence flags.

Important APIs/types: enums `FDBExtraDatabaseMode`, `FDBBackupAgentType`, `FDBTSSMode`, `FDBSimConsistencyScanState`, `FDBSimConsistencyScanCorruptionType`; struct `FDBSimulationPolicyState`; and functions `installFDBSimulationPolicy`, `fdbSimulationPolicyState`, `stringToFDBExtraDatabaseMode`, `updateFDBSimulationPolicy`, and `setFDBSimulationPolicyRemoteTLogPolicy`.

Control flow and state: the state struct carries desired coordinators, storage/tLog/remote/satellite replication policies, anti-quorums, region IDs, allowed fault behavior, backup/DR agent modes, disabled region strings, tester/restart flags, extra database list, consistency scan state and injected corruption fields, per-worker corruption map, and TSS mode. `updateConsistencyScanState` enforces monotonic transitions from an expected current state to a higher desired state and clears corruption details after corruption is found.

State and persistence behavior: simulation policy is process-global in-memory test harness state, not database persistence, but it drives database configuration and fault injection that affect persisted test data.

Dependencies and integration: depends on `DatabaseConfiguration`, replication policies, network addresses, UIDs, and optional string refs. Simulation setup, test workloads, consistency scan, TSS, backup agents, and region configuration code consume it.

Risks and tests: enum ordering matters for TSS fault modes because modes at or above `EnabledAddDelay` are injection modes. Consistency state transitions are monotonic and expected-current guarded. Tests should cover string mode parsing, configuration updates across restarts, consistency corruption lifecycle, remote TLog policy injection, and TSS mode behavior.
