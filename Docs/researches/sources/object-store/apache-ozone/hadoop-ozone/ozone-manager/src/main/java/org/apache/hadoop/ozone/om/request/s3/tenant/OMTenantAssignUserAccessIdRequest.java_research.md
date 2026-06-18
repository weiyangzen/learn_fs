
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantAssignUserAccessIdRequest.java

Purpose: Assigns a user principal to a tenant by creating the tenant-scoped access ID, generated S3 secret, principal mapping, Ranger membership, and in-memory tenant-cache entry.

Important APIs and types: Extends `OMClientRequest`; uses `TenantAssignUserAccessIdRequest/Response`, `UpdateGetS3SecretRequest`, `S3SecretValue`, `OmDBAccessIdInfo`, `OmDBUserPrincipalInfo`, `OMMultiTenantManager`, `S3SecretManager`, `tenantAccessIdTable`, `principalToAccessIdsTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` checks tenant admin privilege, validates access ID length and delimiter rules, requires the default access ID format, verifies tenant existence, takes the Ranger authorizer write lock, assigns the user to the tenant role, generates a SHA-256 secret, and stores it in an embedded update-secret request. `validateAndUpdateCache` locks the tenant volume, verifies tenant/access ID absence and no same-user same-tenant duplicate, creates access ID metadata, updates principal mapping, updates the S3 secret manager under its own lock, updates tenant cache, builds a response containing the S3 secret, audits, and releases locks.

State and persistence behavior: Adds cache entries for tenant access ID, principal-to-access-ID, and S3 secret state at the Ratis transaction index. It also updates the multi-tenant manager cache and relies on response classes to flush DB changes.

Dependencies and integration points: Bridges tenant management, Ranger user-role membership, secret management, OM metadata tables, metrics, and audit logging.

Risks: Authorizer changes precede OM DB changes, so partial failure reconciliation matters. The duplicate check scans a user's existing access IDs and depends on all referenced access ID rows being present. Tests should cover custom access ID rejection, duplicate assignment, existing S3 secret, missing tenant, and principal mapping invalidation/creation.
