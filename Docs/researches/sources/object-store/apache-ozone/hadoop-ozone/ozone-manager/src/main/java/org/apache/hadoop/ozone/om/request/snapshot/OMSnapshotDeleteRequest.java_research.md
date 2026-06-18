
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotDeleteRequest.java

Purpose: Marks an active bucket snapshot as deleted and records deletion time for later reclamation.

Important APIs and types: Extends `OMClientRequest`; uses `DeleteSnapshotRequest/Response`, `SnapshotInfo`, `BUCKET_LOCK`, `SNAPSHOT_LOCK`, snapshot feature/layout annotations, and `OMSnapshotDeleteResponse`.

Control flow: `preExecute` validates snapshot name, resolves linked buckets, checks bucket owner/admin authorization, and writes a leader-generated deletion timestamp into the request. Validation takes bucket and snapshot write locks, loads the snapshot info row, rejects missing/already-deleted/non-active snapshots, sets status to `SNAPSHOT_DELETED`, writes deletion time, updates the snapshot info cache, builds response, audits outside locks, and updates active/deleted/failure metrics.

State and persistence behavior: Mutates only the snapshot info table cache. It does not remove the snapshot from `SnapshotChainManager`; purge handles final chain cleanup.

Dependencies and integration points: Connects external snapshot delete API to snapshot deletion services, audit, metrics, linked bucket resolution, and authorization.

Risks: Delete is a mark phase, so clients may see `FILE_NOT_FOUND` for already-deleted snapshots pending reclamation. Tests should cover status transitions, timestamp preservation from `preExecute`, permission failures, linked buckets, and no chain removal before purge.
