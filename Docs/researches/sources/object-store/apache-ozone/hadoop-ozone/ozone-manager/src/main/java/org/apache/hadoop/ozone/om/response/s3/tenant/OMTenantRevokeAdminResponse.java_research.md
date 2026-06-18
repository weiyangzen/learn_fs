<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeAdminResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeAdminResponse.java

Purpose: Persists an updated tenant access ID record after revoking admin privileges.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `accessId` and `OmDBAccessIdInfo`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes to `TenantAccessIdTable`; `getOmDBAccessIdInfo` supports tests.

Control flow and persistence: A single batched put replaces the access-ID info with request-prepared data that removes admin state. Cleanup metadata names `TENANT_ACCESS_ID_TABLE`.

Dependencies and integration: Used by tenant admin revoke request handling. The class mirrors assign-admin persistence with different request semantics.

Risks and test signals: Risk is overwriting unrelated fields in the access-ID record. Tests should verify admin flag removal, retained tenant/principal data, failure no-op, and table key correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeAdminResponse.java -->
