<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ddbalance.toml -->
# sources/storage-engines/foundationdb/tests/slow/ddbalance.toml

## Purpose
Baseline DDBalance with BackgroundSelector, swizzled RandomClogging, and coordinator ChangeConfig.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DDBalance_Test. Workload entry points are `DDBalance`, `BackgroundSelector`, `RandomClogging`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `DDBalance`(testDuration=120.0, transactionsPerSecond=250.0, binCount=1000, writesPerTransaction=5, keySpaceDriftFactor=10, moversPerClient=10, actorsPerClient=100, nodes=100000); `BackgroundSelector`(testDuration=120.0); `RandomClogging`(testDuration=120.0, swizzle=1); `ChangeConfig`(maxDelayBeforeChange=120.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: DDBalance_Test: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ddbalance.toml -->
