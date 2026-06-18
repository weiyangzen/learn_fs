<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/LongRunning.toml -->
# sources/storage-engines/foundationdb/tests/slow/LongRunning.toml

## Purpose
Long-running Cycle and Attrition scenario for sustained failure and workload pressure.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CycleTestWithKills. Workload entry points are `Cycle`, `Attrition`. Configuration keys include configuration=longRunningTest=True.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=2500.0, testDuration=10000.0); `Attrition`(testDuration=10000.0).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CycleTestWithKills: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/LongRunning.toml -->
