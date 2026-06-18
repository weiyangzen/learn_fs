<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveTableKeysResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveTableKeysResponse.java

Purpose: Moves deleted keys, renamed entries, and deleted directory entries from one snapshot table set into the next snapshot or active DB, while removing the moved records from the source snapshot.

Important APIs/types/functions: Extends `OMClientResponse`. Constructor stores `fromSnapshot`, optional `nextSnapshot`, `bucketId`, deleted key list, deleted dir list, and renamed key list. Main helpers are `addKeysToNextSnapshot` and `deleteKeysFromSnapshot`.

Control flow and persistence: Acquires read locks on `SNAPSHOT_DB_CONTENT_LOCK` for source and optional next snapshot IDs. It opens snapshot RocksDB instances, writes moved records to the next snapshot store or active batch, commits and flushes snapshot DB batches, deletes moved records from the source snapshot DB, releases locks, then updates `SnapshotInfoTable` for source and next snapshots.

Dependencies and integration: Used by snapshot move-table-keys request handling. Depends on `OmSnapshotManager`, `OmSnapshot`, `RDBStore`, `IOzoneManagerLock`, and snapshot utility merge logic.

Risks and test signals: Lock ordering, null next snapshot handling, and multi-store commit/flush boundaries are critical. Tests should cover lock failure, no-next-snapshot active writes, deleted-dir protobuf conversion, rename deletion, snapshot info updates, and retry safety after partial movement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveTableKeysResponse.java -->
