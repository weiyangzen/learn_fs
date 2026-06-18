# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/SnapshotDiffCleanupService.java

Purpose: `SnapshotDiffCleanupService` is a single-threaded background service that removes persisted snapshot-diff reports and moves old terminal or stale jobs out of the active job table. It keeps snapshot diff metadata bounded after jobs are done, cancelled, failed, rejected, or old enough to be considered stale.

Important APIs and types: the constructor receives the RocksDB handle, column family handles for active jobs, purged jobs, and reports, and a `CodecRegistry`. `run()` is the testable cleanup operation. `getEntryFromPurgedJobTable()` exposes purge-table content for tests. Background execution is via nested `SnapshotDiffCleanUpTask`.

Control flow: `run()` intentionally removes reports first by calling `removeOlderJobReport()`, then calls `moveOldSnapDiffJobsToPurgeTable()`. This order avoids a window where a snapshot-diff request sees a completed active job moved to purge while its report has already disappeared. `SnapshotDiffCleanUpTask.call()` checks `shouldRun()`, increments `runCount`, and invokes `run()`.

RocksDB behavior: `moveOldSnapDiffJobsToPurgeTable()` iterates the active job column family, decodes `SnapshotDiffJob`, and for up to `maxJobToPurgePerTask` jobs writes the job ID and total diff entry count into the purged-job column family and deletes the active-job key. Jobs qualify if older than `maxAllowedTime` or status is `FAILED`, `REJECTED`, or `CANCELLED`; stale queued/in-progress jobs are intentionally purged by age. `removeOlderJobReport()` iterates purged jobs, deletes the report range from `jobId + DELIMITER + 0` to the lexicographically higher job prefix, then deletes the purged-job entry.

State and persistence behavior: this class writes directly to RocksDB using `ManagedWriteBatch` and `ManagedWriteOptions`, not Ratis. That is appropriate for local snapshot diff job/report metadata but means callers must understand the column families' replication and lifecycle semantics. `successRunCount` is present but never incremented, so it does not currently measure successful runs.

Dependencies and integration points: it depends on `SnapshotDiffJob`, Ozone snapshot diff statuses, RocksDB managed wrappers, and OM configuration keys for max jobs per task and report persistence time. It is owned by the snapshot manager and referenced by integration tests for snapshot diff lifecycle.

Risks: `shouldRun()` only checks suspension; a TODO notes that `ozoneManager.isLeaderReady()` was removed for Mockito-related test failures. In HA deployments, direct RocksDB cleanup without a leader check deserves scrutiny. Runtime exceptions are thrown for RocksDB/codec failures rather than being handled gracefully. The report-first cleanup protocol assumes a full cleanup interval passes before any consumer reads reports for purged jobs.

Test signals: `TestSnapshotDiffCleanupService`, `TestSnapshotDiffManager`, and `TestOmSnapshot` exercise job movement and report deletion. Tests should also pin `successRunCount` semantics if it becomes observable.
