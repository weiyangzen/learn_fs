<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantDeleteResponse.java

Purpose: Removes tenant state and optionally updates the backing volume metadata after tenant deletion.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores volume name, nullable `OmVolumeArgs`, and tenant ID. The failure constructor calls `checkStatusNotOK()`. `addToDBBatch` deletes tenant state and conditionally writes volume args.

Control flow and persistence: Deletes `TenantStateTable[tenantId]`. If `volumeName` is non-empty, it requires `omVolumeArgs` to be non-null and to match the volume name, then writes `VolumeTable[getVolumeKey(volumeName)]` with updated volume metadata. Cleanup metadata names tenant and volume tables.

Dependencies and integration: Used by delete-tenant request handling, including flows where volume deletion or retained volume metadata has already been decided.

Risks and test signals: Preconditions intentionally fail on inconsistent volume metadata. Tests should cover tenant-only deletion, retained-volume update, mismatched volume-name assertion, null volume args when required, and failure no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantDeleteResponse.java -->
