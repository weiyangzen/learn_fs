<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SharedDefaultBackupCorrectness.toml -->
# sources/storage-engines/foundationdb/tests/slow/SharedDefaultBackupCorrectness.toml

## Purpose
Exercises default shared backups over file and DB backup agents in single extra database mode.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): SharedDefaultBackupToFileThenDB. Workload entry points are `Cycle`, `BackupAndRestoreCorrectness`, `BackupToDBCorrectness`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=500.0, testDuration=30.0); `BackupAndRestoreCorrectness`(backupTag='backup1', backupAfter=20.0, minBackupAfter=10.0, restoreAfter=60.0, shareLogRange=True, performRestore=True, allowPauses=False, defaultBackup=True); `BackupToDBCorrectness`(backupTag='backup2', backupAfter=20.0, minBackupAfter=10.0, restoreAfter=60.0, performRestore=False, shareLogRange=True, defaultBackup=True).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: SharedDefaultBackupToFileThenDB: clearAfterTest=False, simBackupAgents='BackupToFileAndDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFileAndDB.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SharedDefaultBackupCorrectness.toml -->
