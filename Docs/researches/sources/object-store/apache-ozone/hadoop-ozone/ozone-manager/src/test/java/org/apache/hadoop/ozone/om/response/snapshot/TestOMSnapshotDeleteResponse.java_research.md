# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotDeleteResponse.java

Purpose: Tests `OMSnapshotDeleteResponse` marking an existing snapshot as deleted.

Important APIs/types/functions: Uses `OMSnapshotCreateResponse`, `OMSnapshotDeleteResponse`, `SnapshotInfo`, `SNAPSHOT_ACTIVE`, `SNAPSHOT_DELETED`, snapshot path creation, and `snapshotInfoTable`.

Control flow: The test creates OM metadata with mocked snapshot manager dependencies, seeds volume/bucket info, commits a snapshot create response, verifies the snapshot directory and active table row, mutates the same `SnapshotInfo` status to DELETED, commits delete response, and verifies the table still has one row with deleted status.

State/persistence: Snapshot delete is a status update in `snapshotInfoTable`; it does not remove the snapshot row or directory in this test.

Dependencies/integration: Integrates snapshot create and delete responses through the same metadata store and batch path.

Risks/test signals: Uses the same batch field across create and delete commits. It does not test missing snapshot, repeated delete, or local filesystem cleanup. Main signal is transition from ACTIVE to DELETED with row retention.
