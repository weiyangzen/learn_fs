<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeAclOpResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeAclOpResponse.java

Purpose: Persists updated volume ACL metadata after add/remove/set ACL operations.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores updated `OmVolumeArgs`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes to `VolumeTable`; `getOmVolumeArgs` is test-visible.

Control flow and persistence: Performs `VolumeTable.put(getVolumeKey(volume), omVolumeArgs)` in the OM batch. Cleanup metadata names `VOLUME_TABLE`.

Dependencies and integration: Used by volume ACL request handling. The request layer computes the ACL mutation and supplies the full volume args.

Risks and test signals: Whole-volume rewrite can overwrite owner/quota fields if stale. Tests should cover ACL add/remove/set, retained non-ACL fields, failure no-op, and correct volume DB key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeAclOpResponse.java -->
