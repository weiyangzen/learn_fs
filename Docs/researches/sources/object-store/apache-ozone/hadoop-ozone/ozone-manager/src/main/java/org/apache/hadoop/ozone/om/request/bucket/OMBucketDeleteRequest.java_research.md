# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketDeleteRequest.java

## Purpose

`OMBucketDeleteRequest` deletes an empty bucket and updates volume namespace accounting. It protects buckets that contain keys, incomplete multipart uploads, or snapshots, and blocks old clients from deleting bucket layouts they cannot understand.

## Important APIs, Types, And Functions

- `validateAndUpdateCache(OzoneManager, ExecutionContext)` performs ACL validation, lock acquisition, existence checks, emptiness checks, snapshot checks, cache tombstone writes, and response construction.
- `bucketContainsSnapshot(...)` checks snapshot presence in both cache and persisted table using the bucket snapshot prefix.
- `blockBucketDeleteWithBucketLayoutFromOldClient(...)` validates bucket-layout support for older clients.

## Control Flow And State

The request increments delete metrics, checks bucket delete ACLs, then acquires volume read and bucket write locks. It loads `OmBucketInfo`, rejects missing/non-empty buckets, rejects incomplete MPUs, and rejects snapshot-containing buckets. On success it writes a tombstone cache entry to the bucket table, decrements the in-memory bucket metric, decrements the volume's used namespace, writes the updated volume cache entry, and returns `OMBucketDeleteResponse`. Locks are released before audit logging.

## Dependencies And Integration Points

It depends on `OMMetadataManager` bucket, volume, MPU, and snapshot APIs; `OzoneManagerLock` bucket/volume lock levels; `SnapshotInfo`; `OMBucketDeleteResponse`; and request validation infrastructure for old-client layout guards.

## Risks And Test Signals

Important edge cases include cache-only snapshots, tombstoned snapshots, incomplete MPU detection, volume namespace decrement, and bucket emptiness across layouts. Tests should cover snapshot prefix collisions, bucket recreation with same name, FSO delete metrics, lock detail propagation, and error responses for missing bucket, non-empty bucket, incomplete MPU, snapshot containment, and old-client layout rejection.
