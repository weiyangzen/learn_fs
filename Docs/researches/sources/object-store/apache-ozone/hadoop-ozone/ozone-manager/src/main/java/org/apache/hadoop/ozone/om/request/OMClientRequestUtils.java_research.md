# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/OMClientRequestUtils.java

## Purpose

`OMClientRequestUtils` is a small static utility class used by Ozone Manager client request handlers. It centralizes request precondition checks that are shared across request implementations: bucket-layout compatibility, snapshot-bucket detection, and selective failure logging.

## Important APIs, Types, And Functions

- `checkClientRequestPrecondition(BucketLayout dbBucketLayout, BucketLayout reqClassBucketLayout)` verifies that a request handler selected for filesystem-optimized or non-FSO handling matches the actual bucket layout. It throws `OMException(INTERNAL_ERROR)` on mismatch.
- `isSnapshotBucket(OMMetadataManager, OmKeyInfo)` builds the bucket snapshot key prefix from the key's volume and bucket, then checks both snapshot table cache and persisted table.
- `shouldLogClientRequestFailure(IOException)` suppresses client-request failure logs for `OMException.ResultCodes.KEY_NOT_FOUND` and logs all other exception classes/result codes.

## Control Flow And State

The layout check is pure validation. Snapshot detection first scans the in-memory table cache for non-null `SnapshotInfo` entries with the bucket prefix, then seeks the RocksDB-backed `snapshotInfoTable` and tests the next key prefix. This cache-then-DB pattern catches unflushed snapshot creates while avoiding false positives for cache tombstones. No table is mutated by this class.

## Dependencies And Integration Points

The utility depends on `OMMetadataManager`, Ozone metadata table iterators/cache iterators, `BucketLayout`, `OmKeyInfo`, `SnapshotInfo`, and `OMException`. It is an integration guard for request dispatch logic and snapshot-aware operations elsewhere in `om.request`.

## Risks And Test Signals

Important risk is prefix correctness: snapshot keys append `OM_KEY_PREFIX` to the bucket DB key to avoid matching buckets with common prefixes. Tests should cover cache-only snapshots, DB-only snapshots, tombstoned cache values, non-snapshot buckets with similar names, and bucket-layout mismatch behavior. Logging tests should confirm `KEY_NOT_FOUND` failures are intentionally quiet while other failures remain visible.
