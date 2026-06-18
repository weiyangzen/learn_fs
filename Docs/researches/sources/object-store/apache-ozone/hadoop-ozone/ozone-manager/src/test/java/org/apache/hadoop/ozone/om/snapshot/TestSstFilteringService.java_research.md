# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSstFilteringService.java

## Purpose
`TestSstFilteringService` is an integration-style test for the background `SstFilteringService`, which removes irrelevant RocksDB SST files from snapshot checkpoints while preserving bucket-visible data. It also verifies service interactions with deleted snapshots and defrag-service enablement.

## Important APIs, Types, and Functions
- `KeyManager.getSnapshotSstFilteringService()` obtains the service.
- `SstFilteringService.getSnapshotFilteredCount`, `pause`, `resume`, `getBootstrapStateLock`, and `isSstFiltered`.
- `OmTestManagers` provides a runnable in-process OM, key manager, and write client.
- `RDBStore.getDb().flush(KEY_TABLE)` and `compactRange(KEY_TABLE)` force SST layout.
- Snapshot operations go through `OzoneManagerProtocol.createSnapshot` and `deleteSnapshot`.
- Helpers create volumes, buckets, keys, and list keys from active DB or `OmSnapshot` metadata.

## Control Flow
Class setup creates an OM with short container-report and SST-filtering intervals and DB profile `TEST`. `testIrrelevantSstFileDeletion` writes keys to one bucket, flushes and compacts, writes another bucket, snapshots the second bucket, waits for filtering, verifies active and snapshot key sets match, and checks that non-level-0 irrelevant SST files are removed from the snapshot directory while relevant ones remain. It also holds the bootstrap lock to prove filtering pauses and later resumes. `testActiveAndDeletedSnapshotCleanup` pauses filtering, creates two snapshots, deletes one, resumes, and verifies only active snapshot SST files are reduced while deleted snapshot files remain but counts/flags advance. `testSstFilteringService` writes 150 random keys across three buckets with periodic flush/compaction, snapshots each bucket, waits for filtering, and validates each snapshot key set. `testSstFilteringDisabledWhenDefragEnabled` starts a separate OM with both SST filtering and defrag intervals enabled and asserts SST filtering is not started.

## State and Persistence Behavior
The tests create real OM metadata, key table entries, snapshots, checkpoint directories, and RocksDB SST files. Filtering changes checkpoint file contents and updates `SnapshotInfo`'s filtered state. Service counters track how many active snapshot checkpoints have been processed.

## Dependencies and Integration Points
This file integrates OM protocol operations, key manager services, RocksDB flush/compaction behavior, snapshot manager checkpoint paths, snapshot metadata readers, and configuration gating between SST filtering and snapshot defrag.

## Risks and Edge Cases
- Tests depend on RocksDB file-level behavior and background service timing; waits use bounded polling.
- Random bucket selection in `testSstFilteringService` means key distribution varies, though expected sets are tracked.
- File deletion expectations distinguish level-0 from compacted files, which can be sensitive to RocksDB behavior changes.

## Test Signals
Passing means SST filtering removes irrelevant checkpoint SST files without losing visible keys, skips deleted snapshots appropriately, honors bootstrap locking, marks snapshots filtered, and is disabled when defrag service is enabled.
