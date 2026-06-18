<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotSetPropertyResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotSetPropertyResponse.java

Purpose: Persists property changes for one or more snapshots, including size/deep-clean metadata submitted by background services.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores a collection of updated `SnapshotInfo`; the failure constructor calls `checkStatusNotOK()` and sets the collection to null. `addToDBBatch` iterates updated snapshots and writes each row.

Control flow and persistence: Performs `SnapshotInfoTable.put(tableKey, updatedSnapInfo)` for every updated snapshot. Cleanup metadata names `SNAPSHOT_INFO_TABLE`.

Dependencies and integration: Used by explicit snapshot property requests and by deletion services through `submitSetSnapshotRequests`.

Risks and test signals: Multiple snapshot rows may be updated in one batch; stale entries can regress size or deep-clean flags. Tests should cover multiple updates, exclusive size deltas, deep-clean flags, empty collection handling if allowed, and failure no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotSetPropertyResponse.java -->
