<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveDeletedKeysResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveDeletedKeysResponse.java

Purpose: Moves deleted-key, renamed-key, and deleted-directory records from one snapshot toward the next snapshot or active DB, and updates the originating snapshot after reclaim processing.

Important APIs/types/functions: Extends `OMClientResponse` and is built with `Builder`. Key fields are `fromSnapshot`, optional `nextSnapshot`, `nextDBKeysList`, `reclaimKeysList`, `renamedKeysList`, `movedDirs`, and `bucketId`. Helpers include `processKeys`, `processDirs`, `processReclaimKeys`, `deleteDirsFromSnapshot`, and static `createRepeatedOmKeyInfo`.

Control flow and persistence: It obtains `OmSnapshotManager` from `OmMetadataManagerImpl`, opens the from snapshot, optionally opens the next snapshot and writes to its RocksDB store in a dedicated batch, or writes to active OM batch when there is no next snapshot. It moves renamed keys to `SnapshotRenamedTable`, merges deleted entries into `DeletedTable`, moves deleted dirs, updates from-snapshot deleted entries or deletes them, flushes snapshot DB WAL/data, and finally writes updated `SnapshotInfo` records to active `SnapshotInfoTable`.

Dependencies and integration: Used by snapshot deleted-key movement requests and snapshot deep-cleaning. Depends on `OmSnapshot`, `RDBStore`, `SnapshotUtils.createMergedRepeatedOmKeyInfoFromDeletedTableEntry`, and snapshot-local metadata managers.

Risks and test signals: This crosses multiple RocksDB instances, so atomicity is not a single OM batch. Tests should cover next-snapshot and active-DB targets, empty reclaimed key lists, moved directory deletion, snapshot info updates, WAL flush behavior, and retry/idempotency after partial snapshot DB writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveDeletedKeysResponse.java -->
