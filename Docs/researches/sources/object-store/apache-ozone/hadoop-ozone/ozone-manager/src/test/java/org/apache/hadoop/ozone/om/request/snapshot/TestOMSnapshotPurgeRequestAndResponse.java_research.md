# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/snapshot/TestOMSnapshotPurgeRequestAndResponse.java

## Purpose
This test validates snapshot purge request and response behavior: removing snapshot rows, deleting local checkpoint directories, recording local snapshot transaction metadata, and repairing global/path snapshot chains. It extends the snapshot base fixture with checkpoint support.

## Important APIs and Types
Important collaborators include `OMSnapshotPurgeRequest`, `OMSnapshotPurgeResponse`, `SnapshotPurgeRequest`, `SnapshotInfo`, `SnapshotChainManager`, `OmSnapshotLocalDataManager`, `ReadableOmSnapshotLocalDataProvider`, `TransactionInfo`, `BatchOperation`, and `OmMetadataManagerImpl`.

## Control Flow and State
`createSnapshots` creates checkpointed snapshots and returns their snapshot table keys. `createPurgeKeysRequest` builds a `SnapshotPurge` OM request. `preExecute` wraps the request after pre-execution, and `purgeSnapshots` runs preExecute, validate, response DB update, and batch commit.

`testValidateAndUpdateCache` creates ten snapshots and checkpoint directories, verifies local property YAML exists, purges all keys at transaction index 200, then verifies snapshot table entries disappear, checkpoint directories are deleted, local snapshot data preserves the purge transaction info, and purge metrics increment. `testDuplicateSnapshotPurge` repeats validation after the DB rows are already deleted and verifies the response carries updated snapshot info without resurrecting table rows. Failure testing injects a mocked snapshot info table throwing `CodecException`, expecting `INTERNAL_ERROR` and failure metrics.

The parameterized chain tests cover single and multiple bucket cases, contiguous purge ranges, bucket-ordered and interleaved creation orders. They track expected transaction info and deep-clean flags, purge a subset, then validate remaining `SnapshotInfo` rows and `SnapshotChainManager` previous/next links for both global and path-specific chains.

## Dependencies and Integration Points
The class exercises the full purge pipeline: OM request validation, response DB batch application, RocksDB-backed tables, filesystem checkpoints, local snapshot metadata, and chain manager in-memory state.

## Risks and Test Signals
Risks include orphaned checkpoint directories, broken chain links after middle-range purges, stale deep-clean flags, missing transaction info on neighbor snapshots, and swallowed metadata-table failures. Directory existence checks, table counts, chain traversal assertions, local data reads, statuses, and metrics are the key signals.
