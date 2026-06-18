<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledApiCorrectness.toml -->
# sources/storage-engines/foundationdb/tests/slow/SwizzledApiCorrectness.toml

## Purpose
Runs a smaller API correctness workload while swizzled clogging, rollback, attrition, and ChangeConfig run.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): ApiCorrectnessTest. Workload entry points are `ApiCorrectness`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ApiCorrectness`(numKeys=2000, onlyLowerCase=True, shortKeysRatio=0.5, minShortKeyLength=1, maxShortKeyLength=3, minLongKeyLength=1, maxLongKeyLength=128, minValueLength=1); `RandomClogging`(testDuration=120.0, swizzle=1); `Rollback`(testDuration=120.0, meanDelay=10.0); `Attrition`(testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `ChangeConfig`(maxDelayBeforeChange=120.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: ApiCorrectnessTest: clearAfterTest=True, timeout=2100, runSetup=True.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledApiCorrectness.toml -->
