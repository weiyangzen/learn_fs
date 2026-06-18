# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotRequestAndResponse.java

## Purpose
`TestSnapshotRequestAndResponse` is a base fixture for snapshot request/response tests. It prepares a mocked `OzoneManager`, real `OmMetadataManagerImpl`, metrics, snapshot manager, batch operation, volume/bucket state, and helpers for creating snapshot checkpoints and synthetic deleted/renamed key records.

## Important APIs, Types, and Functions
- `baseSetup()` initializes the OM test fixture.
- `createSnapshotCheckpoint(volume, bucket, snapshotName)` exercises `OMSnapshotCreateRequest.validateAndUpdateCache` and `OMSnapshotCreateResponse.addToDBBatch`, commits transaction info, and returns the checkpoint path.
- `getDeletedKeys`, `getRenameKeys`, and `getDeletedDirKeys` build table-key/value pairs for deleted key, rename, and deleted directory scenarios.
- Mocked `OzoneManager` methods cover bucket link resolution, metrics, snapshot feature flag, admin/owner checks, ACL authorizer, layout version manager, audit logger, default replication config, and snapshot manager access.

## Control Flow
Before each derived test, the fixture creates a temporary OM metadata DB, sets metadata directories, adds a random volume and bucket, opens a batch operation, and constructs `OmSnapshotManager`. Snapshot checkpoint helper builds a create snapshot request, runs pre-execute, validates/updates cache at transaction index 1, batches response writes and transaction info, commits, reads the resulting `SnapshotInfo`, and computes the expected checkpoint directory under the snapshot parent directory.

## State and Persistence Behavior
This base writes real OM metadata state into a temp RocksDB store. Snapshot checkpoint creation persists `SnapshotInfo` and transaction info, and creates a snapshot checkpoint directory. Helper key generators produce deterministic deleted and rename table keys that downstream tests can write into metadata tables.

## Dependencies and Integration Points
The class bridges request-layer code, response batch commits, audit/ACL/version mocks, metrics, replication config, bucket layout resolution, and snapshot manager behavior. It is not itself a test class with `@Test` methods but is a shared integration fixture.

## Risks and Edge Cases
- Because it centralizes many mocks, downstream tests can inherit assumptions about admin status, bucket layout, ACL behavior, and feature enablement.
- `stop()` clears inline mocks and closes batch operations; derived classes must avoid using fixture state after teardown.

## Test Signals
When used by subclasses, successful setup and checkpoint creation signal that snapshot request/response flows can be exercised against a real metadata manager with controlled OM dependencies.
