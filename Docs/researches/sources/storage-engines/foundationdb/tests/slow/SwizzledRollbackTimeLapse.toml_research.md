<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapse.toml -->
# sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapse.toml

## Purpose
Long Cycle workload under swizzled clogging, rollback, attrition-to-zero, and coordinator changes.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): SwizzledRollbackTimeLapse. Workload entry points are `Cycle`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=500.0, testDuration=300.0, nodeCount=10000); `RandomClogging`(testDuration=300.0, swizzle=1); `Rollback`(testDuration=300.0, meanDelay=10.0); `Attrition`(testDuration=300.0); `Attrition`(machinesToKill=10, machinesToLeave=0, reboot=True, testDuration=300.0); `Attrition`(machinesToKill=10, machinesToLeave=0, reboot=True, testDuration=300.0); `ChangeConfig`(maxDelayBeforeChange=300.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: SwizzledRollbackTimeLapse: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapse.toml -->
