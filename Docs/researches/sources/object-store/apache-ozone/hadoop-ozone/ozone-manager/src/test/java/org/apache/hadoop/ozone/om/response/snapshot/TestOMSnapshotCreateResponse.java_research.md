# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotCreateResponse.java

Purpose: Tests `OMSnapshotCreateResponse` persistence, snapshot directory creation, and cleanup of bucket-scoped deleted/renamed side tables.

Important APIs/types/functions: Uses `OMSnapshotCreateResponse`, `SnapshotInfo`, `TransactionInfo`, `OmSnapshotManager.getSnapshotPath`, `snapshotInfoTable`, `deletedTable`, `deletedDirTable`, `snapshotRenamedTable`, `StandaloneReplicationConfig`, and table iterators.

Control flow: Parameterized test runs with 0, 1, 5, 10, and 25 scoped keys. It creates snapshot info with transaction info, populates deleted, deleted-dir, and snapshot-renamed tables with sentinel keys outside the target bucket plus keys inside the target bucket, commits create response, verifies snapshot directory and table row, then verifies only sentinel keys remain in each side table.

State/persistence: Adds one `SnapshotInfo` row, creates a filesystem snapshot directory, and removes deleted/deleted-dir/snapshot-rename rows within the snapshot bucket scope while preserving surrounding rows.

Dependencies/integration: Integrates mocked `OzoneManager`/`OmSnapshotManager`/local snapshot manager, OM metadata store, filesystem paths, and bucket-prefix cleanup rules.

Risks/test signals: Sentinel generation mutates the last character of bucket names, which is adequate for lexical range checks but synthetic. The test closes the metadata store in teardown, unlike many sibling tests. Strong signals are directory existence, exact snapshot row equality, and scoped cleanup.
