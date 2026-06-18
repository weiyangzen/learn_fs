
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotCreateRequest.java

Purpose: Creates filesystem snapshots for a bucket, including snapshot identity, chain linkage, referenced-size metadata, and snapshot table persistence.

Important APIs and types: Extends `OMClientRequest`; uses `CreateSnapshotRequest/Response`, `SnapshotInfo`, `SnapshotChainManager`, `OmMetadataManagerImpl`, `BUCKET_LOCK`, `SNAPSHOT_LOCK`, `@RequireSnapshotFeatureState`, and `@DisallowedUntilLayoutVersion(FILESYSTEM_SNAPSHOT)`.

Control flow: Constructor derives initial `SnapshotInfo`. `preExecute` validates name, resolves linked buckets, checks bucket owner/admin authorization, enforces snapshot limit, assigns UUID and creation time, and rewrites the request. Validation takes a bucket read lock and snapshot write lock, checks duplicate table key, sets create/last transaction info, estimates referenced sizes from bucket usage and replication config, atomically updates snapshot chain and snapshot info cache, returns snapshot info, decrements in-flight count, audits, and updates metrics.

State and persistence behavior: Adds a `SnapshotInfo` cache entry with transaction metadata and previous global/path snapshot IDs. It also mutates in-memory `SnapshotChainManager`; failure during cache update attempts to roll back the chain.

Dependencies and integration points: Integrates bucket link resolution, admin authorization, quota/replication sizing, snapshot limit accounting, chain management, OM metrics, audit, and double-buffered persistence.

Risks: Chain and table cache must remain atomic; the class contains explicit synchronization and rollback for that reason. `getBucketInfo` reads cache directly and can return null if bucket metadata is inconsistent. Tests should cover duplicate names, linked bucket resolution, owner/admin checks, chain predecessor fields, in-flight decrement on failure, and referenced-size estimation.
