# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/snapshot/TestOMSnapshotCreateRequest.java

## Purpose
This class validates `OMSnapshotCreateRequest`, covering snapshot-name validation, owner/admin authorization, linked-bucket resolution, metadata updates, snapshot-limit enforcement, and cleanup of snapshot-scoped deleted/renamed tables. It extends `TestSnapshotRequestAndResponse`, so each test runs against a real temporary OM metadata manager plus a mocked `OzoneManager` fixture.

## Important APIs and Types
Core types include `OMSnapshotCreateRequest`, `SnapshotInfo`, `OmSnapshotManager`, `OMClientResponse`, `OMResponse`, `OmBucketInfo`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `TableIterator`, `OMKeyRenameResponse`, and `OMKeyRenameResponseWithFSO`. Helpers construct `CreateSnapshot` requests, add keys to the open key table, simulate deleted keys/directories, and simulate rename responses for legacy and FSO layouts.

## Control Flow and State
`preExecute` tests accept UUID-like, three-character, and <=63-character names, reject illegal characters, numeric-only names, too-short names, and too-long names, and assert bucket links are resolved into target volume/bucket names. `testPreExecuteBadOwner` verifies admin authorization denies non-owner/non-admin callers.

`testValidateAndUpdateCache` creates a key, checks bucket referenced data and replicated bytes, runs validation, then asserts an `OK` `CreateSnapshot` response, a cached `SnapshotInfo`, referenced-size fields, transaction info for log index 1, and snapshot metrics. Duplicate creation returns `FILE_ALREADY_EXISTS` and increments failure metrics. Snapshot-limit tests rebuild `OmSnapshotManager` with small `OZONE_OM_FS_SNAPSHOT_MAX_LIMIT` values and verify both committed chain entries and in-flight preExecute reservations count toward the limit, while failed creation does not leak reservations.

The renamed/deleted table tests deliberately create records in two buckets, then create a snapshot scoped to one bucket and assert only that bucket's deleted-table, deleted-dir-table, or snapshot-renamed-table rows are cleaned.

## Dependencies and Integration Points
The class integrates OM request validation, bucket-link resolution, metadata table cache mutation, snapshot chain accounting, FSO path-key generation, rename responses, and snapshot metrics. It depends on `OMRequestTestUtils` and snapshot helpers to model realistic RocksDB table rows.

## Risks and Test Signals
The highest-risk areas are off-by-one snapshot limits, lingering in-flight reservations after failures, deleting/renaming table rows from the wrong bucket, and broken transaction metadata in `SnapshotInfo`. Assertions on metrics, table row counts, key prefixes, response statuses, and cached protobuf equivalence provide the main regression signals.
