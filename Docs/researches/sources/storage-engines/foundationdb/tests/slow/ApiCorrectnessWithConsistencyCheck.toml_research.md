<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessWithConsistencyCheck.toml -->
# sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessWithConsistencyCheck.toml

## Purpose
Runs the API correctness workload with replica consistency checks on reads enabled, stressing read validation against the same operation mix.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): ApiCorrectnessWithConsistencyCheck. Workload entry points are `ApiCorrectness`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ApiCorrectness`(numKeys=5000, onlyLowerCase=True, shortKeysRatio=0.5, minShortKeyLength=1, maxShortKeyLength=3, minLongKeyLength=1, maxLongKeyLength=128, minValueLength=1).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation.
Clear/setup flags and state controls are declared on tests as: ApiCorrectnessWithConsistencyCheck: clearAfterTest=True, timeout=2100, runSetup=True.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: enable_replica_consistency_check_on_reads=True.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessWithConsistencyCheck.toml -->
