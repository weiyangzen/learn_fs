# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/snapshot/TestOMSnapshotRenameRequest.java

## Purpose
This class validates `OMSnapshotRenameRequest`, including server-side feature gating, snapshot-name validation, linked-bucket resolution, owner/admin authorization, successful metadata-table key migration, and failure statuses for existing or missing target snapshots.

## Important APIs and Types
It uses `OMSnapshotRenameRequest`, `OMSnapshotCreateRequest`, `SnapshotInfo`, `OMConfigKeys.OZONE_OM_SNAPSHOT_RENAME_ALLOWED_KEY`, `SnapshotStatus.SNAPSHOT_ACTIVE`, cache `CacheKey`/`CacheValue`, protobuf `RenameSnapshot` responses, and bucket/key helpers from `OMRequestTestUtils`.

## Control Flow and State
Setup creates two random snapshot names and enables snapshot rename in OM configuration. `testPreExecuteFailsWhenSnapshotRenameNotAllowed` unsets the config and expects `FEATURE_NOT_ENABLED` with a specific server-config message. Parameterized preExecute tests accept valid names, reject invalid names including underscores and uppercase, and verify linked buckets are resolved into target volume/bucket names. `testPreExecuteBadOwner` checks admin authorization failure for non-owner/non-admin callers.

`testValidateAndUpdateCache` creates a key to establish referenced sizes, adds an active snapshot cache entry under the old table key, runs validation, and asserts an `OK` `RenameSnapshot` response. The new snapshot table key contains a `SnapshotInfo` matching the response and preserving the original snapshot ID, while the old table key is removed. `testEntryExists` creates both old and new snapshots, then rename returns `FILE_ALREADY_EXISTS` and keeps both entries. `testEntryNotFound` returns `FILE_NOT_FOUND` when the old snapshot does not exist.

## Dependencies and Integration Points
The test integrates configuration gating, snapshot naming rules, ownership checks, linked bucket resolution, bucket size accounting, and snapshot info table cache mutation.

## Risks and Test Signals
Key risks are enabling rename despite config default, losing snapshot identity during rename, leaving stale old-name rows, overwriting an existing target snapshot, or accepting invalid S3-style names. Status, cache-presence, and snapshot-ID assertions detect those regressions.
