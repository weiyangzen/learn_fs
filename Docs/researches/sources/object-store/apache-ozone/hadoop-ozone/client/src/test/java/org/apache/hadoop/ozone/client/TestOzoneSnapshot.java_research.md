# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneSnapshot.java

## Purpose
`TestOzoneSnapshot` verifies conversion from OM `SnapshotInfo` helper objects to public `OzoneSnapshot` DTOs.

## Important APIs, Types, And Functions
`getMockedSnapshotInfo` builds a Mockito `SnapshotInfo` with volume, bucket, name, creation time, status, UUID, path, checkpoint directory, referenced sizes, exclusive sizes, and deep-cleaning deltas. `testOzoneSnapshotFromSnapshotInfo` calls `OzoneSnapshot.fromSnapshotInfo` and compares it to an expected `OzoneSnapshot`.

## Control Flow
The test prepares a mocked `SnapshotInfo`, converts it, constructs the expected DTO, and uses `assertEquals`.

## State And Persistence Behavior
No persistent state is used; all data is in mocks and local values.

## Dependencies And Integration Points
It depends on `SnapshotInfo`, `OzoneSnapshot`, Mockito, JUnit, and `SNAPSHOT_ACTIVE`. It validates client-facing snapshot metadata mapping that `RpcClient.getSnapshotInfo` returns through `OzoneSnapshot.fromSnapshotInfo`.

## Risks And Edge Cases
The expected exclusive sizes include base exclusive size plus deep-cleaning deltas, so mapping changes in `OzoneSnapshot` must preserve that semantic or update this test. It does not cover null fields, inactive/deleted statuses, or multiple checkpoint versions.

## Test Signals
Provides direct DTO conversion coverage for snapshot size and identity fields.
