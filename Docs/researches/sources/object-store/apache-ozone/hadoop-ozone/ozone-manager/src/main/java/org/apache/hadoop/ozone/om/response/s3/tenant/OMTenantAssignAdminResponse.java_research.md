<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignAdminResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignAdminResponse.java

Purpose: Persists an updated tenant access ID record after assigning tenant-admin privileges.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `accessId` and updated `OmDBAccessIdInfo`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes to `TenantAccessIdTable`. `getOmDBAccessIdInfo` is test-visible.

Control flow and persistence: Performs a single batched put of the access-ID record. The record is expected to contain the updated admin flag/role state prepared by the request layer. Cleanup metadata names `TENANT_ACCESS_ID_TABLE`.

Dependencies and integration: Used by `OMTenantAssignAdminRequest` and the tenant metadata model.

Risks and test signals: Because it rewrites the whole access-ID info, stale request data could overwrite other tenant-user fields. Tests should verify admin flag changes, retained tenant/user metadata, failure no-op, and table key equal to the access ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignAdminResponse.java -->
