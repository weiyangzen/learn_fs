<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantCreateResponse.java

Purpose: Persists tenant creation metadata and, when needed, the backing volume and owner user-volume mapping.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `OmVolumeArgs`, optional `PersistedUserVolumeInfo`, and `OmDBTenantState`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes tenant state, volume state, and optional user table state. `getOmDBTenantState` is test-visible.

Control flow and persistence: Writes `TenantStateTable[tenantId]`, `VolumeTable[getVolumeKey(volume)]`, and, if volume creation was not skipped, `UserTable[getUserKey(owner)]`. Cleanup metadata names tenant and volume tables, while user table mutation is also performed.

Dependencies and integration: Used by tenant create request flow and reuses volume-create style metadata updates.

Risks and test signals: The optional user-volume info path is important for existing volumes. Tests should cover new-volume tenant creation, skipped volume creation, tenant state fields, owner mapping, and failure no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantCreateResponse.java -->
