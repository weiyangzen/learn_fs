<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessSwitchover.toml -->
# sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessSwitchover.toml

## Purpose
Exercises API correctness while an AtomicSwitchover workload moves traffic to the extra single database, with a Status workload observing the transition.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): ApiCorrectnessTest. Workload entry points are `ApiCorrectness`, `AtomicSwitchover`, `Status`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ApiCorrectness`(numKeys=2500, onlyLowerCase=True, shortKeysRatio=0.5, minShortKeyLength=1, maxShortKeyLength=3, minLongKeyLength=1, maxLongKeyLength=64, minValueLength=1); `AtomicSwitchover`; `Status`(testDuration=30.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: ApiCorrectnessTest: clearAfterTest=False, simBackupAgents='BackupToDB', timeout=2100, runSetup=True.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToDB.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
Status workload validates status reporting during the scenario; correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessSwitchover.toml -->
