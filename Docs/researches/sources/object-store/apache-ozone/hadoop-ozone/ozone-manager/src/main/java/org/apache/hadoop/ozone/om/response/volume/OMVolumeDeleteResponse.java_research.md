<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeDeleteResponse.java

Purpose: Deletes a volume row and updates or removes the owner's user-volume list.

Important APIs/types/functions: Extends `OMClientResponse`. Success constructor stores volume name, owner, and updated `PersistedUserVolumeInfo`; failure constructor calls `checkStatusNotOK()`. `addToDBBatch` updates user table then deletes volume table row.

Control flow and persistence: If the updated owner volume list is empty, it deletes `UserTable[getUserKey(owner)]`; otherwise it writes the updated list. Then it deletes `VolumeTable[getVolumeKey(volume)]`. Cleanup metadata names `VOLUME_TABLE`.

Dependencies and integration: Used by delete-volume request handling after validation that the volume can be deleted.

Risks and test signals: Owner mapping and volume deletion must be atomic. Tests should cover deleting the last owner volume, deleting one of several volumes, failure no-op, and retry idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeDeleteResponse.java -->
