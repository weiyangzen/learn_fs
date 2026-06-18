# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDeletingServiceIntegrationTest.java

## Purpose
Large integration suite for snapshot deletion, snapshot deep cleaning, active DB to snapshot DB movement, snapshot-chain rewiring, and locking with concurrent key deletion. It covers both object-store and FSO bucket layouts.

## Important APIs and Types
The class uses `MiniOzoneCluster`, `SnapshotDeletingService`, `KeyDeletingService`, `DirectoryDeletingService`, `OmSnapshot`, `OmSnapshotManager`, `SnapshotInfo`, `SnapshotChainManager`, `SnapshotUtils`, `MultiSnapshotLocks`, `ReclaimableKeyFilter`, `OMLockDetails`, `OMMetadataManager` tables, `RepeatedOmKeyInfo`, `OmKeyInfo`, `OmDirectoryInfo`, and Mockito construction mocking. Main tests include `testMultipleSnapshotKeyReclaim`, `testSnapshotSplitAndMove`, `testSnapshotWithFSO`, and parameterized `testSnapshotDeletingServiceWaitsForKeyDeletingService`.

## Control Flow
Setup configures small block/chunk sizes, short deletion service intervals, snapshot deep cleaning, filesystem snapshot support, and a default bucket. Helper `createSnapshotDataForBucket` creates keys, snapshots, overwrites, deletes, and then deletes an intermediate snapshot to exercise reclaim and snapshot-chain changes. FSO testing suspends deletion services, creates keys/directories/snapshots, performs overwrites, deletes, key renames and dir renames, resumes services for deep cleaning, inspects snapshot DB tables, deletes snapshots, and verifies rows move to the next snapshot or active DB. The locking test constructs a `KeyDeletingTask`, mocks `ReclaimableKeyFilter` and `MultiSnapshotLocks`, races snapshot deletion against key deletion, and asserts snapshot GC waits for key deletion to finish.

## State and Persistence
Persistent state spans active key/file/directory tables, active deleted table, active deleted dir table, active renamed table, per-snapshot RocksDB metadata tables, snapshot info rows, snapshot cache, and snapshot chain predecessor IDs. Runtime state includes retained `OmSnapshot` suppliers that must be closed and suspended/resumed deletion services.

## Dependencies and Integration Points
This integrates OM snapshot APIs, object-store and FSO metadata layouts, key and directory deleting services, snapshot deleting service, snapshot cache, snapshot chain manager, active DB and checkpointed snapshot DBs, Ratis double-buffer flushing, and lock ordering for snapshot garbage collection.

## Risks and Edge Cases
The class is marked unhealthy and some tests are flaky. It is order-dependent through `@TestMethodOrder` and a `runIndividualTest` flag. Tests suspend services and hold snapshot references, so cleanup in `@AfterEach` is essential. Construction mocking of lock/filter classes is sensitive to implementation changes. Table row counts encode detailed garbage-collection semantics and can fail if cleanup batching changes without semantic regressions.

## Test Signals
Signals include deleted keys being reclaimed or retained according to snapshot references, deleted snapshot rows disappearing, next snapshot predecessor IDs rewired, snapshot cache purged, deleted entries split/moved into the next snapshot DB, FSO deleted dir/deleted key/renamed tables moved across snapshots and active DB correctly, deep-clean flags set, and snapshot deletion acquiring locks only after concurrent key deletion work finishes.
