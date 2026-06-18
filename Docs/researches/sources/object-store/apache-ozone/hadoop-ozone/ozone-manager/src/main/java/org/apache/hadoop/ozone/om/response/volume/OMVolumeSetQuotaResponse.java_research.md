<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetQuotaResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetQuotaResponse.java

Purpose: Persists updated volume quota settings.

Important APIs/types/functions: Extends `OMClientResponse`. Success constructor stores updated `OmVolumeArgs`; failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes the volume row.

Control flow and persistence: Performs `VolumeTable.put(getVolumeKey(volume), omVolumeArgs)`. Cleanup metadata names `VOLUME_TABLE`.

Dependencies and integration: Used by set-volume-quota request handling after validation of quota values and existing usage.

Risks and test signals: Whole-volume rewrite can regress ACL/owner fields if stale. Tests should verify quota bytes/namespace changes, retained owner/ACL metadata, invalid quota failure no-op, and correct DB key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetQuotaResponse.java -->
