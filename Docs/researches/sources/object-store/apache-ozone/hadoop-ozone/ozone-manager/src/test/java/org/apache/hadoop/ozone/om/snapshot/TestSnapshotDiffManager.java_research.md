# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDiffManager.java

## Purpose
`TestSnapshotDiffManager` is the main unit/integration-style test for `SnapshotDiffManager`. It covers object-id map generation, diff report generation and pagination, job lifecycle state transitions, cancellation, listing, startup recovery, executor saturation, submit APIs, and report-only APIs.

## Important APIs, Types, and Functions
- `SnapshotDiffManager.addToObjectIdMap`, `generateDiffReport`, `createPageResponse`, `getSnapshotDiffReport`, `submitSnapshotDiff`, `cancelSnapshotDiff`, `getSnapshotDiffJobList`, `getSnapshotDiffJobs`, and `loadJobsOnStartUp`.
- Persistent RocksDB column families for `SNAP_DIFF_JOB_TABLE_NAME`, `SNAP_DIFF_REPORT_TABLE_NAME`, and `SNAP_DIFF_PURGED_JOB_TABLE_NAME`.
- `SnapshotDiffJob`, `SnapshotDiffResponse`, `SubmitSnapshotDiffResponse`, `CancelSnapshotDiffResponse`, and `ListSnapshotDiffJobResponse`.
- `SstFileSetReader`, `TablePrefixInfo`, `PersistentMap<byte[], byte[]>`, and `SnapshotTestUtils.StubbedPersistentMap`.
- Snapshot model and OM integration: `SnapshotInfo`, `OmSnapshotManager`, `SnapshotCache`, `OMMetadataManager`, bucket layout, key tables, and codecs for `DiffReportEntry`.

## Control Flow
`@BeforeEach` builds a temporary RocksDB store, diff job/report column families, mocked OM metadata tables, snapshot info rows for several job statuses, bucket layout data, and an `OmSnapshotManager` backed by `SnapshotCache`. Object-id map tests mock `SstFileSetReader` to return keys with and without tombstones, then verify old/new object-id maps and object-id check sets across directory/file/key tables and native-library toggles. Diff generation tests build old/new object-id maps with create/delete/rename/modify patterns, mock key comparison logic, generate reports, and assert type ordering and entries. Pagination tests write report entries into RocksDB and verify page size, token, and job isolation.

Job lifecycle tests submit and cancel snapshot diff jobs, list jobs by status, reload in-progress jobs at startup, simulate full thread pools, and verify submit/report-only behavior for `IN_PROGRESS`, `DONE`, `FAILED`, `CANCELLED`, `REJECTED`, and absent jobs. Helper methods create random snapshot contexts, populate snapshot info mocks, and configure bucket/key-table mocks for running diff operations.

## State and Persistence Behavior
Diff jobs and report entries are persisted in RocksDB through `PersistentMap` and raw column-family writes. Job keys are formed from from/to snapshot UUIDs separated by `DELIMITER`; report keys encode job id, diff type ordering, and index. State transitions are central: new/queued jobs become `IN_PROGRESS`, completed jobs become `DONE`, failed/cancelled/rejected jobs can be resubmitted by `submitSnapshotDiff`, and cancelled jobs remain visible until cleanup. Rejected jobs caused by executor saturation are removed from the job table.

## Dependencies and Integration Points
This test touches much of the snapshot diff stack: RocksDB codecs, SST key readers, OM snapshot cache, bucket layout/key-table selection, HDFS `SnapshotDiffReport` entry types, JMX-adjacent job models, and Ozone configuration for thread pool size, full diff forcing, native library loading, and max changed keys.

## Risks and Edge Cases
- Many tests use mocks for metadata and snapshots; they validate manager control flow but not a full end-to-end OM database diff.
- Native tombstone behavior is mocked via `SstFileSetReader`; real RocksDB SST parsing remains a separate risk.
- Thread-pool saturation tests are timing-sensitive and depend on sleep durations and executor behavior.
- Report key ordering must remain compatible with paging tokens and persisted report entries.

## Test Signals
Passing provides strong signals that diff manager persistence, job state machine, cancellation semantics, pagination, object-id delta generation, startup recovery, and submission short-circuit behavior remain compatible with snapshot diff clients.
