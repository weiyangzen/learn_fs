<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CommitBug.toml -->
# sources/storage-engines/foundationdb/tests/slow/CommitBug.toml

## Purpose
Targets the CommitBug workload while adding swizzled clogging, rollback, and repeated attrition.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CommitBugTest. Workload entry points are `CommitBug`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `CommitBug`; `RandomClogging`(testDuration=120.0, swizzle=1); `Rollback`(testDuration=120.0, meanDelay=10.0); `Attrition`(testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0).

## State And Persistence Behavior
Persistent and simulated state touched: cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CommitBugTest: clearAfterTest=True, runSetup=True.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CommitBug.toml -->
