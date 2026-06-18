<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupCorrectnessPartitioned.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupCorrectnessPartitioned.toml

## Purpose
Combines Cycle traffic with BackupAndRestorePartitionedCorrectness over all ranges to validate partitioned backup correctness.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupAndRestorePartitioned. Workload entry points are `Cycle`, `BackupAndRestorePartitionedCorrectness`. Configuration keys include testClass='Backup', configuration=.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=30.0); `BackupAndRestorePartitionedCorrectness`(backupAfter=10.0, restoreAfter=60.0, backupRangesCount=-1).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupAndRestorePartitioned: clearAfterTest=False, simBackupAgents='BackupToFile'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupCorrectnessPartitioned.toml -->
