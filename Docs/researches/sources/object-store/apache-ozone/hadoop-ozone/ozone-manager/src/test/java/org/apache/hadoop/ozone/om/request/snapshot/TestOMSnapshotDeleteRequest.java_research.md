# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/snapshot/TestOMSnapshotDeleteRequest.java

## Purpose
This class validates `OMSnapshotDeleteRequest`, mostly mirroring create-request preExecute behavior while focusing on snapshot deletion semantics. It proves deletion marks a snapshot as deleted rather than removing it immediately, and that repeated or missing deletes return the correct error status and metrics.

## Important APIs and Types
It uses `OMSnapshotDeleteRequest`, `OMSnapshotCreateRequest` as a setup helper, `SnapshotInfo`, `SnapshotStatus.SNAPSHOT_ACTIVE`, `SnapshotStatus.SNAPSHOT_DELETED`, cache `CacheKey`/`CacheValue`, linked-bucket `ResolvedBucket`, and protobuf statuses such as `OK` and `FILE_NOT_FOUND`.

## Control Flow and State
Parameterized `preExecute` tests accept and reject the same snapshot-name shapes used by create. Linked bucket tests stub `OzoneManager.resolveBucketLink` so the pre-executed delete request contains resolved volume and bucket names. Authorization tests verify admin authorization blocks delete if the request has no owner/admin permission.

`testValidateAndUpdateCache` manually adds an active `SnapshotInfo` cache entry, invokes validation at transaction index 2, and asserts the OM response is successful, command type is `DeleteSnapshot`, and the cached snapshot remains present but changes to `SNAPSHOT_DELETED`. Metrics reflect one deletion and active count decrement. `testEntryNotExist` confirms a missing snapshot returns `FILE_NOT_FOUND` and increments delete-fail metrics. `testEntryExist` creates a real snapshot, deletes it, checks deletion time is set and active count reaches zero, then deletes again and expects `FILE_NOT_FOUND` while the deleted marker remains.

## Dependencies and Integration Points
The tests integrate snapshot create and delete request classes, the snapshot info table cache, OM metrics, bucket ownership checks, and linked bucket resolution.

## Risks and Test Signals
The main risks are accidentally hard-deleting snapshot table rows during logical delete, failing to set deletion time/status, miscounting active snapshots, or treating an already-deleted snapshot as deletable. Status checks and table-state assertions provide direct signals.
