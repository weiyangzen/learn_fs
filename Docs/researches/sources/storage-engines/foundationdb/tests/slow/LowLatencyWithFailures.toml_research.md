<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/LowLatencyWithFailures.toml -->
# sources/storage-engines/foundationdb/tests/slow/LowLatencyWithFailures.toml

## Purpose
Tests LowLatency read behavior during controlled attrition while disabling a recovery fault-injection path that would violate latency expectations.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): Clogged. Workload entry points are `Cycle`, `LowLatency`, `Attrition`. Configuration keys include configuration=minimumReplication=2.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=1000.0, testDuration=300.0); `LowLatency`(testDuration=300.0, maxGRVLatency=50.0, testWrites=False); `Attrition`(machinesToKill=1, machinesToLeave=3, reboot=True, testDuration=300.0, waitForVersion=True, allowFaultInjection=False, killDc=False).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: Clogged: connectionFailuresDisableDuration=60.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: cc_recovery_init_req_allow_drop_in_sim=False.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/LowLatencyWithFailures.toml -->
