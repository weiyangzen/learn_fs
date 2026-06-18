<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CloggedCycleTest.toml -->
# sources/storage-engines/foundationdb/tests/slow/CloggedCycleTest.toml

## Purpose
Runs Cycle traffic under two RandomClogging profiles and a coordinator ChangeConfig event.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CloggedCycleTest. Workload entry points are `Cycle`, `RandomClogging`, `RandomClogging`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=1250.0, testDuration=30.0); `RandomClogging`(testDuration=30.0); `RandomClogging`(testDuration=30.0, scale=0.1, clogginess=2.0); `ChangeConfig`(maxDelayBeforeChange=30.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CloggedCycleTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CloggedCycleTest.toml -->
