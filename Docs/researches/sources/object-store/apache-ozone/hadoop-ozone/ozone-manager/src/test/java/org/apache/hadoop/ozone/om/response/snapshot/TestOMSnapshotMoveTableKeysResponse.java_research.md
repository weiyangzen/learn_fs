# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotMoveTableKeysResponse.java

Purpose: Tests `OMSnapshotMoveTableKeysResponse`, which moves deleted and renamed table entries from one snapshot DB to the next snapshot or active DB.

Important APIs/types/functions: Extends `TestSnapshotRequestAndResponse`; uses `OMSnapshotMoveTableKeysResponse`, `SnapshotMoveKeyInfos`, `OmSnapshot`, `SnapshotUtils.getSnapshotInfo`, `SNAPSHOT_DB_CONTENT_LOCK`, `RepeatedOmKeyInfo`, `deletedTable`, `deletedDirTable`, `snapshotRenamedTable`, `CompletableFuture`, and lock spying.

Control flow: Test data populates active tables, creates snapshot checkpoint 1, then adds overlapping deleted/renamed data and optionally creates snapshot checkpoint 2. The test opens snapshot DB suppliers, captures read-lock acquisition IDs, serializes snapshot1 table contents into response protobuf payloads, runs `addToDBBatch` asynchronously, commits, verifies expected lock IDs, asserts snapshot1 side tables are empty, and verifies the next target metadata manager contains merged deleted, deleted-dir, and renamed entries.

State/persistence: Clears deleted/deleted-dir/snapshot-renamed rows from the source snapshot DB and merges them into either the next snapshot DB or active OM DB. Deleted key versions are merged so overlapping keys contain both old and new version ranges.

Dependencies/integration: Deep integration with snapshot checkpoint creation, snapshot DB metadata managers, OM locking, bucket object IDs, protobuf serialization of moved entries, and version ordering.

Risks/test signals: Asynchronous execution can obscure exceptions without the future plumbing, which this test handles. It validates counts and version ordering but not every individual key name. It is one of the strongest tests for snapshot table migration and lock ordering.
