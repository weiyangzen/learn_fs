<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotCreateResponse.java

Purpose: Persists new snapshot metadata and creates the corresponding OM snapshot checkpoint.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `SnapshotInfo`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes snapshot info then invokes `OmSnapshotManager.createOmSnapshotCheckpoint`.

Control flow and persistence: The method intentionally writes `SnapshotInfoTable[tableKey]` before checkpoint creation so RocksDB checkpoint differ listeners can track compaction changes around snapshot creation. The checkpoint creation also cleans selected tables. Cleanup metadata covers deleted, snapshot-renamed, and snapshot-info tables.

Dependencies and integration: Used by snapshot create request handling. Integrates active OM metadata, snapshot metadata, RocksDB checkpoint creation, and snapshot diff support.

Risks and test signals: Ordering is correctness-sensitive for SnapDiff performance. Tests should verify snapshot info persistence, checkpoint directory creation, relevant table cleanup, failure no-op, and behavior under compaction/listener timing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotCreateResponse.java -->
