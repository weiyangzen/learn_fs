<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapseIncrement.toml -->
# sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapseIncrement.toml

## Purpose
Increment workload variant of SwizzledRollbackTimeLapse with expectedRate 0.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): SwizzledRollbackTimeLapse. Workload entry points are `Increment`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Increment`(transactionsPerSecond=100.0, testDuration=300.0, nodeCount=10000, expectedRate=0.0); `RandomClogging`(testDuration=300.0, swizzle=1); `Rollback`(testDuration=300.0, meanDelay=10.0); `Attrition`(testDuration=300.0); `Attrition`(machinesToKill=10, machinesToLeave=0, reboot=True, testDuration=300.0); `Attrition`(machinesToKill=10, machinesToLeave=0, reboot=True, testDuration=300.0); `ChangeConfig`(maxDelayBeforeChange=300.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: SwizzledRollbackTimeLapse: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapseIncrement.toml -->
