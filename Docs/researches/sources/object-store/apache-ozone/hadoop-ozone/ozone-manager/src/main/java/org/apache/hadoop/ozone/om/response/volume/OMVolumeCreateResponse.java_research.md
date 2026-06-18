<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeCreateResponse.java

Purpose: Persists a new volume and updates the owner's user-volume list.

Important APIs/types/functions: Extends `OMClientResponse`. Success constructor stores `OmVolumeArgs` and `PersistedUserVolumeInfo`; failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes volume and user rows. `getOmVolumeArgs` is test-visible.

Control flow and persistence: Computes `dbVolumeKey = getVolumeKey(volume)` and `dbUserKey = getUserKey(owner)`, then batches `VolumeTable.put` and `UserTable.put`. Cleanup metadata names `VOLUME_TABLE`, though user table is also mutated.

Dependencies and integration: Used by create-volume request handling and owner volume-list management.

Risks and test signals: Atomicity between volume and user table is required to avoid orphan volumes or missing owner listings. Tests should verify both rows, duplicate volume failure no-op, owner list content, and ACL/quota fields in `OmVolumeArgs`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeCreateResponse.java -->
