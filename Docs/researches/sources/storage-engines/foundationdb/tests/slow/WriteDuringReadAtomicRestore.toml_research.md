<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/WriteDuringReadAtomicRestore.toml -->
# sources/storage-engines/foundationdb/tests/slow/WriteDuringReadAtomicRestore.toml

## Purpose
Runs WriteDuringRead while AtomicRestore, clogging, rollback, and attrition interact with file backups.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): WriteDuringReadTest. Workload entry points are `WriteDuringRead`, `AtomicRestore`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`. Configuration keys include configuration=StderrSeverity=30.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `WriteDuringRead`(maximumTotalData=1000000, testDuration=240.0, slowModeStart=60.0, minNode=1, useSystemKeys=False); `AtomicRestore`(startAfter=10.0, restoreAfter=50.0, mutationLogType=0); `RandomClogging`(testDuration=60.0); `Rollback`(meanDelay=60.0, testDuration=60.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: WriteDuringReadTest: clearAfterTest=False, simBackupAgents='BackupToFile'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/WriteDuringReadAtomicRestore.toml -->
