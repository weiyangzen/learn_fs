<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobCorrectnessHeavyChaos.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupS3BlobCorrectnessHeavyChaos.toml

## Purpose
Runs BackupS3BlobCorrectness with aggressive S3 chaos plus network clogging and rollback workloads.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupS3BlobCorrectnessHeavyChaos. Workload entry points are `Cycle`, `BackupS3BlobCorrectness`, `RandomClogging`, `Rollback`. Configuration keys include testClass='Backup', configuration=buggify=False, faultInjection=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=30000, transactionsPerSecond=2500.0, testDuration=30.0); `BackupS3BlobCorrectness`(backupAfter=35.0, restoreStartAfterBackupFinished=30.0, abortAndRestartAfter=0.0, stopDifferentialAfter=0.0, performRestore=True, backupRangesCount=-1, skipDirtyRestore=False, backupURL='blobstore://mocks3:mocksecret:mocktoken@127.0.0.1:8080/backup_container?bucket=backup_bucket&region=us-east-1&secure_connection=0&cwpf=1&cu=1'); `RandomClogging`(testDuration=400.0); `Rollback`(meanDelay=90.0, testDuration=400.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupS3BlobCorrectnessHeavyChaos: clearAfterTest=False, simBackupAgents='BackupToFile', waitForQuiescenceEnd=False, runConsistencyCheck=False.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile, blobstore.

## Risks
chaos rates can compound across many S3/blobstore operations: errorRate=0.25, throttleRate=0.3, delayRate=0.15, corruptionRate=0.01, maxDelay=10.0; failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts; bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobCorrectnessHeavyChaos.toml -->
