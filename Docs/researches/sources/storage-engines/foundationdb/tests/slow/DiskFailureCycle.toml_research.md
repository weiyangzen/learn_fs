<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DiskFailureCycle.toml -->
# sources/storage-engines/foundationdb/tests/slow/DiskFailureCycle.toml

## Purpose
Combines Cycle traffic with disk failure injection that stalls, throttles, and corrupts files under triple replication.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DiskFailureCycle. Workload entry points are `Cycle`, `DiskFailureInjection`. Configuration keys include configuration=buggify=False, minimumReplication=3, minimumRegions=3, logAntiQuorum=0, storageEngineExcludeTypes=['memory', 'memory-radixtree', 'ssd-rocksdb-v1', 'ssd-sharded-rocksdb'].

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=2500.0, testDuration=30.0); `DiskFailureInjection`(testDuration=120.0, verificationMode=True, startDelay=3.0, throttleDisk=True, stallInterval=5.0, stallPeriod=5.0, throttlePeriod=30.0, corruptFile=True).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: DiskFailureCycle: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DiskFailureCycle.toml -->
