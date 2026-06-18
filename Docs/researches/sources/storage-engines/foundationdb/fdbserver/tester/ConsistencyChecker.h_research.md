# sources/storage-engines/foundationdb/fdbserver/tester/ConsistencyChecker.h

Purpose: Declares the consistency and audit entry points used by the tester orchestrator.

Important APIs/types/functions: Forward declares `AuditType`, `ClusterControllerFullInterface`, and `ServerDBInfo`. Declares `checkConsistency`, `auditStorageCorrectness`, `checkConsistencyUrgentSim`, and `runConsistencyCheckerUrgentHolder`.

Control flow: Header-only declarations; runtime flow is in `ConsistencyChecker.cpp`.

State and persistence behavior: No state in the header. Function signatures expose the stateful dependencies: `Database`, tester interfaces, server DB info async vars, and optional tester vectors.

Dependencies and integration points: Includes `fdbclient/NativeAPI.actor.h` and `fdbserver/tester/WorkloadUtils.h` for `Database`, `Future`, `TesterInterface`, and `TestSpec`-related types. Used by `test.cpp` to run post-workload checks and urgent checker modes.

Risks: The broad `checkConsistency` signature must stay aligned with call sites in `test.cpp`. Forward declarations reduce compile coupling but require complete types in implementation.

Test signals: Compile/link coverage ensures implementation matches declarations; functional signals come through tester runs.
