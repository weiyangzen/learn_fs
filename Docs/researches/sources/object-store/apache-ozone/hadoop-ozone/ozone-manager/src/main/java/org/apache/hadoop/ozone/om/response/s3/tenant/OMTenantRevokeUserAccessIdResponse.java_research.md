<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeUserAccessIdResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeUserAccessIdResponse.java

Purpose: Applies tenant user access-ID revocation by deleting the secret and access-ID record and updating or removing the principal mapping.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores access ID, principal, updated `OmDBUserPrincipalInfo`, and `S3SecretManager`. `addToDBBatch` deletes secret state on `OK`, deletes `TenantAccessIdTable[accessId]`, and updates or deletes `PrincipalToAccessIdsTable[principal]`.

Control flow and persistence: Secret deletion uses the batcher when supported or direct `revokeSecret` otherwise. Principal mapping is retained only if the updated access-ID set is non-empty. Cleanup metadata covers secret, tenant access ID, and principal mapping tables.

Dependencies and integration: Used by tenant revoke-user request handling and S3 credential storage.

Risks and test signals: Non-batch secret deletion is not atomic with table changes. The method asserts non-null access ID and contains a TODO about status checking. Tests should cover last-access-ID removal, multi-access-ID update, batch/non-batch secret managers, failure behavior, and idempotent retries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeUserAccessIdResponse.java -->
