<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotRenameResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotRenameResponse.java

Purpose: Renames a snapshot by moving its snapshot-info table row from the old table key to the new table key with updated `SnapshotInfo`.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores old name/key, new name/key, and renamed info; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` performs a put then delete.

Control flow and persistence: Batches `SnapshotInfoTable.put(newName, renamedInfo)` followed by `SnapshotInfoTable.delete(oldName)`. Cleanup metadata names `SNAPSHOT_INFO_TABLE`.

Dependencies and integration: Used by snapshot rename request handling and consumed by snapshot chain lookup code that uses table keys.

Risks and test signals: The field names represent table keys rather than only display names, so request code must pass canonical keys. Tests should verify old row deletion, new row content, no orphan/duplicate snapshot info, chain lookup behavior, and failure no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotRenameResponse.java -->
