
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantRevokeUserAccessIdRequest.java

Purpose: Revokes a tenant access ID, removing the principal mapping, access ID record, S3 secret cache entry, Ranger user-role membership, and tenant cache entry.

Important APIs and types: Extends `OMClientRequest`; uses `TenantRevokeUserAccessIdRequest/Response`, `OmDBAccessIdInfo`, `OmDBUserPrincipalInfo`, `S3SecretManager`, `OMMultiTenantManager`, `tenantAccessIdTable`, `principalToAccessIdsTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` loads access ID info, resolves tenant ID if missing, checks tenant existence and admin privilege, rejects revoking tenant admins until admin privilege is revoked, takes the authorizer lock, and calls Ranger `revokeUserAccessId`. Validation locks the tenant volume, removes the access ID from the principal set or tombstones the principal row if empty, tombstones the tenant access ID row, invalidates the S3 secret manager cache entry, updates tenant cache, builds the response, audits, and tracks failures.

State and persistence behavior: Mutates principal-to-access-IDs and tenant-access-ID cache entries, plus S3 secret manager cache invalidation. Response carries enough data for DB deletion of associated secret state.

Dependencies and integration points: Coordinates Ranger, OM tenant metadata, secret management, audit, metrics, and tenant-volume locking.

Risks: Uses `Objects.requireNonNull` for DB invariants in validation, so inconsistent metadata produces runtime failure. Ranger updates precede DB updates. Tests should cover admin-protected revoke, last access ID principal tombstone, multi-access principal update, missing access ID, and S3 secret removal.
