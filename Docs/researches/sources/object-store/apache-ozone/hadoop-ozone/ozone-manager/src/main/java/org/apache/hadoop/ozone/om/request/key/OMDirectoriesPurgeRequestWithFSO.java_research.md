# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMDirectoriesPurgeRequestWithFSO.java

## Purpose

`OMDirectoriesPurgeRequestWithFSO` is an internal/system request used by OM deletion services to purge deleted FSO directories and their subpaths from metadata tables. It also updates bucket usage, snapshot transaction metadata, open hsync keys, deletion metrics, and system audit logs.

## Important APIs, Types, And Functions

- `validateAndUpdateCache(OzoneManager, ExecutionContext)` processes `PurgeDirectoriesRequest` batches.
- Snapshot validation uses `SnapshotUtils.getSnapshotInfo(...)` and `validatePreviousSnapshotId(...)` when expected previous snapshot ID is present.
- `ProcessedKeyInfo` holds reconstructed `OmKeyInfo`, delete-table key, volume, bucket, and pair key.
- `processDeleteKey(...)` converts protobuf key info into table keys and bucket identifiers.
- `getBucketLockKeySet(...)` computes distinct bucket write-lock keys either from explicit `BucketNameInfo` entries or from purged subfile/subdir key infos.

## Control Flow And State

The request optionally resolves a source snapshot and validates snapshot-chain expectations before acquiring all affected bucket write locks. It iterates each `PurgePathRequest`: marked-deleted subdirectories are tombstoned in the directory table and decrement key metrics/namespace; deleted subfiles are tombstoned in the file table, decrement bytes/namespace, and if they carry `HSYNC_CLIENT_ID`, their open-file entry is marked with `DELETED_HSYNC_KEY`; deleted root directory entries update snapshot namespace accounting. It updates deletion-service metrics, stores snapshot last transaction info or AOS last purge transaction info, copies bucket info for response persistence, releases locks, and returns `OMDirectoriesPurgeResponseWithFSO`.

## Dependencies And Integration Points

This class integrates with `OmMetadataManagerImpl`, directory/file/open-key/snapshot tables, snapshot chain manager, bucket locks over multiple buckets, `DeletingServiceMetrics`, `OMMetrics`, system audit logger, `TransactionInfo`, and `OMDirectoriesPurgeResponseWithFSO`. It is tightly coupled to FSO path-key formats and snapshot-aware deleted-directory cleanup.

## Risks And Test Signals

High-risk areas include multi-bucket lock acquisition, snapshot-chain invalidation, bucket recreation/object ID checks, hsync open-key deletion marking, byte/namespace decrement accuracy, duplicate deleted directory/subdir accounting, cache tombstones, and response persistence ordering. Tests should cover AOS and snapshot purge paths, expected previous snapshot mismatch, explicit and inferred bucket lock sets, deleted hsync files, bucket missing or recreated with different object ID, metrics increments, system audit only in debug mode, and open-key metadata returned in the response.
