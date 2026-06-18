<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/VersionStampBackupToDB.toml -->
# sources/storage-engines/foundationdb/tests/slow/VersionStampBackupToDB.toml

## Purpose
Validates VersionStamp data with BackupToDB agents while aborting backup and killing/rebooting machines.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): VersionStampBackupToDB. Workload entry points are `VersionStamp`, `BackupToDBAbort`, `Attrition`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `VersionStamp`(failIfDataLost=False, validateExtraDB=True, testDuration=60.0); `BackupToDBAbort`(abortDelay=40.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: VersionStampBackupToDB: simBackupAgents='BackupToDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToDB.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/VersionStampBackupToDB.toml -->
