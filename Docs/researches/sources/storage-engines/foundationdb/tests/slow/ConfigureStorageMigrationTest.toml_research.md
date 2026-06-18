<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ConfigureStorageMigrationTest.toml -->
# sources/storage-engines/foundationdb/tests/slow/ConfigureStorageMigrationTest.toml

## Purpose
Runs ConfigureDatabase with storage migration enabled under network clogging and extra machines.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CloggedConfigureDatabaseTest. Workload entry points are `ConfigureDatabase`, `RandomClogging`, `RandomClogging`. Configuration keys include configuration=extraMachineCountDC=2.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ConfigureDatabase`(testDuration=300.0, allowTestStorageMigration=True); `RandomClogging`(testDuration=300.0); `RandomClogging`(testDuration=300.0, scale=0.1, clogginess=2.0).

## State And Persistence Behavior
Persistent and simulated state touched: cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CloggedConfigureDatabaseTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ConfigureStorageMigrationTest.toml -->
