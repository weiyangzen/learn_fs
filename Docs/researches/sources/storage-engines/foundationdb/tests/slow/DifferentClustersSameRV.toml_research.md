<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DifferentClustersSameRV.toml -->
# sources/storage-engines/foundationdb/tests/slow/DifferentClustersSameRV.toml

## Purpose
Exercises read-version behavior across different clusters while switching after a configured delay.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DifferentClustersSameRV. Workload entry points are `DifferentClustersSameRV`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `DifferentClustersSameRV`(testDuration=500, switchAfter=50, keyToRead='someKey', keyToWatch='anotherKey').

## State And Persistence Behavior
Persistent and simulated state touched: primarily transient workload state and simulation status.
Clear/setup flags and state controls are declared on tests as: DifferentClustersSameRV: clearAfterTest=False.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DifferentClustersSameRV.toml -->
