# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestDirectoryDeletingServiceWithFSO.java

## Purpose
Comprehensive integration tests for `DirectoryDeletingService` and related key/snapshot deletion services in FILE_SYSTEM_OPTIMIZED buckets. It validates empty and recursive directory purge, batching, multi-level cleanup, namespace/byte accounting, direct file deletion, double-buffer blockage, and snapshot retention interactions.

## Important APIs and Types
The class uses `MiniOzoneCluster`, Hadoop `FileSystem`, `Path`, FSO `BucketLayout`, `DirectoryDeletingService`, `KeyDeletingService`, `SnapshotDeletingService`, `DeletingServiceMetrics`, `OMMetadataManager`, `OzoneManagerDoubleBuffer`, `OzoneManagerStateMachine`, `OmSnapshotManager`, `OMFileRequest`, `OmKeyInfo`, `OmDirectoryInfo`, `RepeatedOmKeyInfo`, `SnapshotInfo`, `ReclaimableDirFilter`, and `ReclaimableKeyFilter`. Helper methods include `assertSubPathsCount`, `assertTableRowCount`, `checkPath`, `cleanupTables`, and `createFileKey`.

## Control Flow
Setup starts a three-datanode cluster, creates an FSO bucket, configures an `o3fs` URI, sets small iterate batch size, and records deletion metrics. Tests create directory trees via `FileSystem`, delete paths recursively, and poll OM metadata tables until expected row counts and service counters converge. Snapshot-focused tests suspend/resume services, create snapshots, rename and delete directories, run service tasks manually or through spies, and verify cleanup is deferred or moved between active and snapshot DBs as expected.

## State and Persistence
The key persistent state is active OM directory/file tables, deleted directory table, deleted key table, snapshot info table, snapshot renamed table, bucket namespace and byte counters, and double-buffered Ratis-applied transactions. Snapshot tests verify that deleted rows remain when referenced by snapshots and are later purged or moved only when safe.

## Dependencies and Integration Points
This file spans OM filesystem API, FSO metadata layout, async deletion services, key block deletion service, snapshot manager, Ratis double buffer, bucket accounting, and object-store snapshot APIs. It also uses Mockito to intercept snapshot manager and directory deletion service behavior in a concurrency-sensitive scenario.

## Risks and Edge Cases
The test suite is timing-sensitive with two-minute polling windows. Some scenarios manipulate OM metadata tables directly and stop the double-buffer daemon, which is powerful but brittle. Cleanup manually removes DB rows after snapshot-retention tests to protect later tests. Asynchronous services and suspended services must be resumed in all paths to avoid suite pollution.

## Test Signals
Signals include expected active/deleted table counts after empty, batched, and multi-level deletes; moved file/dir and purged dir counters; deletion metrics; namespace never becoming negative during blocked double-buffer processing; direct file deletes being handled by `KeyDeletingService`; snapshot-protected rows remaining in deleted tables; renamed-table cleanup only after safe snapshot flushing; and snapshot deleting service eventually restoring clean snapshot table counts after restart.
