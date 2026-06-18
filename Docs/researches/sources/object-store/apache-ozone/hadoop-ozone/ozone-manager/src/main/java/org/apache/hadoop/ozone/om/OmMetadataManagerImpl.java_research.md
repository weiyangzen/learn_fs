# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataManagerImpl.java

Purpose: `OmMetadataManagerImpl` is the concrete OM metadata facade over RocksDB. It opens OM or snapshot checkpoint DB stores, initializes all OM column-family tables, provides key-format helpers, list/expiration scans, S3 secret storage, table-prefix mapping, and lock access.

Important APIs and types: constructors cover live OM DB, checkpoint metadata managers, read-only checkpoint DBs, and snapshot DBs. Table getters expose user, volume, bucket, key/file, open key/file, multipart, deleted, prefix, transaction, tenant, snapshot, rename, and compaction-log tables. Utility APIs build DB keys for object-store and FSO layouts, list buckets/volumes/keys/snapshots/open files/MPUs, check emptiness, count rows, get expired open keys/MPUs, and batch S3 secret changes.

Control flow: `start()` validates the transient inconsistent DB marker, opens a DBStore via `DBStoreBuilder`, initializes tables with full cache for live OM or partial cache for checkpoints/snapshots, then creates `SnapshotChainManager`. Listing methods merge cache and persisted RocksDB views, skipping cache tombstones and preserving sorted pagination. Expiration methods scan open-key and multipart tables, special-casing hsync and MPU keys to avoid data loss.

State and persistence: all OM metadata tables are persistent RocksDB column families. Table caches represent unflushed updates. `tableMap` indexes opened tables by name; table cache metrics are registered for live tables. Locks protect OM resources but iterator snapshots are used for some read scans.

Dependencies and integration points: central dependency for `OzoneManager`, request handlers, `KeyManager`, `SnapshotUtils`, `SnapshotChainManager`, S3 secret APIs, tenant manager, delete services, and checkpoint/snapshot readers. It integrates with `OMDBDefinition`, `DBStoreBuilder`, `OzoneManagerLock`, hierarchical locks, performance metrics, and protobuf helper types.

Risks: DB key construction must remain compatible across bucket layouts and table definitions. Cache/DB merge logic is subtle around tombstones, pagination, and concurrent flushes. Expired open-key logic must not delete active hsync leases or orphan MPU state. Startup terminates when a DB transient marker exists.

Test signals: cover live versus checkpoint initialization, table presence, key encoding for legacy/OBS/FSO, list pagination with cache overrides and tombstones, bucket/volume emptiness, snapshot listing continuation, expired hsync/open-key cleanup, incomplete MPU detection, table bucket prefixes, S3 batcher behavior, and store close/unregister cleanup.
