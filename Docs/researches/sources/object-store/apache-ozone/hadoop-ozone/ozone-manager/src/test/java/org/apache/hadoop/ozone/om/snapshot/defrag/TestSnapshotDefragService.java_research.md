# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/defrag/TestSnapshotDefragService.java

## Purpose
`TestSnapshotDefragService` validates `SnapshotDefragService`, which builds compacted/defragmented snapshot DB versions, performs full or incremental defrag, ingests non-incremental tables, atomically switches snapshot DB versions, and updates metrics/locks.

## Important APIs, Types, and Functions
- `SnapshotDefragService.start`, `pause`, `resume`, `needsDefragmentation`, `performFullDefragmentation`, `ingestNonIncrementalTables`, `createCheckpoint`, `createDefragCheckpointMetadataManager`, `atomicSwitchSnapshotDB`, `performIncrementalDefragmentation`, `checkAndDefragSnapshot`, and `triggerSnapshotDefragOnce`.
- `OmSnapshotLocalDataManager.WritableOmSnapshotLocalDataProvider` and `OmSnapshotLocalData` store local version/defrag metadata.
- `DeltaFileComputer`/`CompositeDeltaDiffComputer`, `SstFileSetReader`, and `RDBSstFileWriter` provide incremental delta discovery and SST generation.
- `TablePrefixInfo`, `COLUMN_FAMILIES_TO_TRACK_IN_SNAPSHOT`, and OM DB table constants define table/prefix scope.
- OM locks `BOOTSTRAP_LOCK` and `SNAPSHOT_DB_CONTENT_LOCK` protect service passes and snapshot DB switching.

## Control Flow
Setup mocks OM, snapshot manager, local data manager, metadata manager, locks, metrics, performance metrics, and layout version manager. It constructs the service while intercepting `CompositeDeltaDiffComputer` so tests can control delta files. Basic lifecycle tests check start/pause/resume. `needsDefragmentation` tests cover already-defragmented and requires-defrag provider states. Full defrag filters incremental tables by bucket prefix and compacts only tracked tables. Non-incremental ingestion dumps matching prefix ranges from the original snapshot DB and loads them into checkpoint tables.

Checkpoint tests create real temporary checkpoint metadata managers, write table contents, and verify `createCheckpoint` preserves incremental table content while clearing non-incremental tables and avoids RocksDB metrics registration for transient defrag managers. `atomicSwitchSnapshotDB` verifies next-version path replacement, local data version increment, and returned old-version cleanup value.

Incremental defrag builds large synthetic table contents for two snapshots with update/insert/delete/same/absent/non-delta patterns, mocks delta SST files and key readers, captures generated SST writer operations, and verifies version-specific behavior: version 0 dumps all incremental tables, later versions directly ingest single-delta tables and merge/dump multi-delta tables. It also checks processed-delta metrics.

`checkAndDefragSnapshot` tests cover deleted snapshots, already-defragged snapshots, full/incremental failures, and successful active snapshot flows with precise ordering under `SNAPSHOT_DB_CONTENT_LOCK`: needs check, checkpoint, full/incremental defrag, non-incremental ingestion, checkpoint close, atomic switch, old checkpoint cleanup, and metrics/perf updates. `triggerSnapshotDefragOnceFailure` verifies outer failure metric handling under bootstrap lock.

## State and Persistence Behavior
The service manages durable snapshot DB directories and version metadata. Full defrag compacts table contents by bucket prefix in a checkpoint DB. Incremental defrag writes SST delta files and ingests them into checkpoint tables. Atomic switch replaces the next snapshot DB version path and updates local data metadata. Tests also ensure transient defrag checkpoint DBs do not register generic RocksDB metrics.

## Dependencies and Integration Points
This test integrates snapshot local data, snapshot chain traversal, OM metadata managers, table prefixing, RocksDB checkpoint managers, SST readers/writers, delta-file computation, lock ordering, native SST reader loading, snapshot metrics, and OM performance metrics.

## Risks and Edge Cases
- Heavy mocking means many tests validate service orchestration rather than real RocksDB compaction internals.
- Incremental defrag correctness depends on delta SST key streams including tombstones and table prefixes.
- Atomic switching must maintain lock ordering and close checkpoint managers before replacing paths; tests explicitly assert this order.
- Metrics are part of the behavior contract and can regress independently from data correctness.

## Test Signals
Passing gives strong coverage that snapshot defrag decides when work is needed, creates correct checkpoints, handles full and incremental modes, ingests tables, switches DB versions atomically under locks, cleans old versions, skips deleted/already-defragged snapshots, and records success/failure metrics.
