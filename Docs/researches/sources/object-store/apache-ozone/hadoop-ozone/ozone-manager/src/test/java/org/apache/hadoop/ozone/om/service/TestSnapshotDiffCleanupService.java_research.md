# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDiffCleanupService.java

Purpose: Tests `SnapshotDiffCleanupService` cleanup of snapshot diff jobs and report rows in RocksDB column families. Important APIs and types include `ManagedRocksDB`, `ColumnFamilyHandle`, `CodecRegistry`, `SnapshotDiffJob`, `SnapshotDiffReportOzone.DiffReportEntry`, `SnapshotDiffResponse.JobStatus`, and snapshot diff cleanup config keys.

Control flow: Static setup opens a temporary RocksDB. Each test creates active job, purged job, and report column families, registers codecs, and constructs the service with mocked config. The main test inserts DONE, stale DONE, QUEUED, IN_PROGRESS, FAILED, and REJECTED jobs with report rows. First run moves terminal/stale jobs into the purged table; second run removes their report rows and purged markers. A separate test verifies zero-entry purged jobs can still remove stray report rows.

State and persistence behavior: This is real RocksDB column-family persistence with raw codec serialization. The service transitions rows from active job table to purged job table, then deletes report table entries.

Dependencies and integration points: Snapshot diff job status lifecycle, report retention duration, max purge count, filesystem snapshot enablement, RocksDB iterators, and codec compatibility. Risks include manual column-family lifecycle and exact table counts. Test signals are row counts, job presence/absence, purged entry counts, and report byte equality/nullness.
