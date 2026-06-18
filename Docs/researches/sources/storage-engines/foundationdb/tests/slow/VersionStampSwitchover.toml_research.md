<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/VersionStampSwitchover.toml -->
# sources/storage-engines/foundationdb/tests/slow/VersionStampSwitchover.toml

## Purpose
Validates VersionStamp behavior across AtomicSwitchover and attrition in extra single database mode.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): VersionStampCorrectnessTest. Workload entry points are `VersionStamp`, `AtomicSwitchover`, `Attrition`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `VersionStamp`(testDuration=60.0); `AtomicSwitchover`(switch1delay=20.0, switch2delay=20.0, stopDelay=20.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: VersionStampCorrectnessTest: clearAfterTest=False, simBackupAgents='BackupToDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToDB.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/VersionStampSwitchover.toml -->
