<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignUserAccessIdResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignUserAccessIdResponse.java

Purpose: Applies tenant user assignment by creating/updating the access ID record, principal-to-access-ID mapping, and associated S3 secret.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `S3SecretValue`, principal, access ID, `OmDBAccessIdInfo`, `OmDBUserPrincipalInfo`, and `S3SecretManager`. `addToDBBatch` writes secret state when response status is `OK`, then writes tenant access ID and principal mapping. Test-visible accessors expose access-ID info and secret.

Control flow and persistence: Secret persistence uses `S3SecretManager` batcher when available or `storeSecret` for non-batch stores. It then puts `TenantAccessIdTable[accessId]` and `PrincipalToAccessIdsTable[principal]`. Cleanup metadata covers `S3_SECRET_TABLE`, `TENANT_ACCESS_ID_TABLE`, and `PRINCIPAL_TO_ACCESS_IDS_TABLE`.

Dependencies and integration: Used by tenant user assignment request handling. Integrates tenant metadata and S3 credential storage.

Risks and test signals: Non-batch secret writes are not atomic with table updates. Tests should cover batch and non-batch secret managers, principal mapping accumulation, access ID table content, status-not-OK secret no-op, and replay/idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignUserAccessIdResponse.java -->
