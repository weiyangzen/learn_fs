<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ClogWithRollbacks.toml -->
# sources/storage-engines/foundationdb/tests/slow/ClogWithRollbacks.toml

## Purpose
Compares short Cycle scenarios with and without RandomClogging, Rollback, and Attrition to expose rollback behavior under clogged networks.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 4 `[[test]]` block(s): CloggedCycleTest, UncloggedRollbackCycleTest, CloggedRollbackCycleTest, UncloggedCycleTest. Workload entry points are `Cycle`, `RandomClogging`, `RandomClogging`, `Attrition`, `Attrition`, `Cycle`, `Rollback`, `Cycle`, `RandomClogging`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Cycle`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `Cycle`(transactionsPerSecond=5000.0, testDuration=5.0); `RandomClogging`(testDuration=5.0); `RandomClogging`(testDuration=5.0, scale=0.1, clogginess=2.0); `Attrition`(machinesToKill=3, machinesToLeave=0, reboot=True, testDuration=5.0); `Attrition`(machinesToKill=3, machinesToLeave=0, reboot=True, testDuration=5.0); `Cycle`(transactionsPerSecond=5000.0, testDuration=5.0); `Rollback`(testDuration=5.0, multiple=False); `Cycle`(transactionsPerSecond=5000.0, testDuration=5.0); `RandomClogging`(testDuration=5.0); `RandomClogging`(testDuration=5.0, scale=0.1, clogginess=2.0); `Rollback`(testDuration=5.0, multiple=False); `Attrition`(machinesToKill=3, machinesToLeave=0, reboot=True, testDuration=5.0); `Attrition`(machinesToKill=3, machinesToLeave=0, reboot=True, testDuration=5.0); `Cycle`(transactionsPerSecond=5000.0, testDuration=10.0).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CloggedCycleTest: default flags; UncloggedRollbackCycleTest: default flags; CloggedRollbackCycleTest: default flags; UncloggedCycleTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ClogWithRollbacks.toml -->
