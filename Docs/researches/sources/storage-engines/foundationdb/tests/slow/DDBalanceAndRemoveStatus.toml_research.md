<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DDBalanceAndRemoveStatus.toml -->
# sources/storage-engines/foundationdb/tests/slow/DDBalanceAndRemoveStatus.toml

## Purpose
Adds a Status workload to the DDBalanceAndRemove scenario to validate status reporting during server removal.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DDBalance_Test. Workload entry points are `DDBalance`, `BackgroundSelector`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `RemoveServersSafely`, `Status`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `DDBalance`(testDuration=120.0, transactionsPerSecond=250.0, binCount=1000, writesPerTransaction=5, keySpaceDriftFactor=10, moversPerClient=10, actorsPerClient=100, nodes=100000); `BackgroundSelector`(testDuration=120.0); `RandomClogging`(testDuration=120.0, swizzle=1); `Rollback`(testDuration=120.0, meanDelay=10.0); `Attrition`(testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `RemoveServersSafely`(minDelay=0, maxDelay=100, kill1Timeout=30, kill2Timeout=6000); `Status`(testDuration=30.0).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: DDBalance_Test: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
Status workload validates status reporting during the scenario; correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DDBalanceAndRemoveStatus.toml -->
