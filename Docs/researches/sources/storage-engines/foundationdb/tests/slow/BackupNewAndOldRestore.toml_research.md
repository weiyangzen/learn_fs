<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupNewAndOldRestore.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupNewAndOldRestore.toml

## Purpose
Creates both partitioned-log and default-log backups, restores one of the two tags, then validates data with Cycle.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 4 `[[test]]` block(s): NewBackup, OldBackup, RestoreRandomBackup, CycleAfterRestore. Workload entry points are `Cycle`, `Backup`, `Cycle`, `Backup`, `Restore`, `Cycle`. Configuration keys include testClass='Backup', configuration=.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=30.0); `Backup`(mutationLogType=1, backupTag='newBackup', backupAfter=10.0, restoreAfter=60.0); `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=30.0, skipSetup=True); `Backup`(mutationLogType=0, backupTag='oldBackup', backupAfter=10.0, restoreAfter=60.0); `Restore`(backupTag1='newBackup', backupTag2='oldBackup'); `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=10.0, skipSetup=True).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: NewBackup: clearAfterTest=False, simBackupAgents='BackupToFile'; OldBackup: runConsistencyCheck=False, waitForQuiescence=False, clearAfterTest=False, simBackupAgents='BackupToFile'; RestoreRandomBackup: runConsistencyCheck=False, waitForQuiescence=False, simBackupAgents='BackupToFile', clearAfterTest=False; CycleAfterRestore: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupNewAndOldRestore.toml -->
