<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotDeleteResponse.java

Purpose: Persists an updated `SnapshotInfo` record for a delete-snapshot request, typically marking snapshot lifecycle state rather than immediately purging physical data.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores snapshot table key and updated `SnapshotInfo`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes the updated snapshot info.

Control flow and persistence: Performs one batched put to `SnapshotInfoTable[tableKey]`. Actual checkpoint deletion and chain cleanup are handled later by purge/deleting services.

Dependencies and integration: Used by snapshot delete request handling and feeds `SnapshotDeletingService`/purge flows that consume snapshot state.

Risks and test signals: The response must not remove snapshot metadata prematurely. Tests should verify state transition fields, table key correctness, later purge eligibility, and failure no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotDeleteResponse.java -->
