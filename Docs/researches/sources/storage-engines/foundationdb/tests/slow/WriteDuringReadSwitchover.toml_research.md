<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/WriteDuringReadSwitchover.toml -->
# sources/storage-engines/foundationdb/tests/slow/WriteDuringReadSwitchover.toml

## Purpose
Runs WriteDuringRead during AtomicSwitchover to BackupToDB plus failure workloads and Status.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): WriteDuringReadTest. Workload entry points are `WriteDuringRead`, `AtomicSwitchover`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Status`. Configuration keys include configuration=StderrSeverity=30, extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `WriteDuringRead`(maximumTotalData=1000000, testDuration=240.0, slowModeStart=60.0, minNode=1); `AtomicSwitchover`; `RandomClogging`(testDuration=60.0); `Rollback`(meanDelay=60.0, testDuration=60.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0); `Status`(testDuration=60.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: WriteDuringReadTest: clearAfterTest=False, simBackupAgents='BackupToDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToDB.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
Status workload validates status reporting during the scenario; correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/WriteDuringReadSwitchover.toml -->
