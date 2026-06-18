# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMultiTenantManager.java

## Purpose
`OMMultiTenantManager` defines the Ozone Manager multi-tenancy contract. It covers tenant lifecycle service management, tenant/admin authorization checks, OM metadata access, tenant/user lookup APIs, Ranger synchronization access, standard tenant naming helpers, static configuration validation for enabling S3 multi-tenancy, and default Ranger policy builders.

## Important APIs, types, and functions
The interface declares lifecycle methods `start` and `stop`, accessors for `OMRangerBGSyncService`, `OMMetadataManager`, authorizer/cache operations, and `AuthorizerLock`, plus query/check methods such as `getUserNameGivenAccessId`, `isTenantAdmin`, `listUsersInTenant`, `getTenantForAccessID`, `checkAdmin`, `checkTenantAdmin`, `checkTenantExistence`, `getTenantVolumeName`, `getTenantUserRoleName`, `getTenantAdminRoleName`, `getTenantFromDBById`, `isUserAccessIdPrincipalOrTenantAdmin`, and `isTenantEmpty`.

Static naming helpers build conventional access ids, user/admin role names, and Ranger policy names from tenant id. `checkAndEnableMultiTenancy` validates OM and Ranger-related configuration when `ozone.om.multitenancy.enabled` is true. `getDefaultVolumeAccessPolicy` and `getDefaultBucketAccessPolicy` construct `MultiTenantAccessController.Policy` objects with default role/user ACLs and Ozone policy labels/descriptions.

## Control flow
Implementations own most runtime behavior. The static validation method reads the multi-tenancy enabled flag and a development skip flag. If multi-tenancy is disabled or dev skip is true, it returns the configured enabled value after skipping validation. Otherwise it requires Ozone security, Kerberos authentication, Ranger HTTPS address, Ranger service name, and either clear-text Ranger admin API credentials or OM Kerberos principal/keytab settings. It logs errors and throws a runtime exception if any hard requirement failed. Clear-text Ranger credentials are allowed but produce a warning. The keytab path existence check logs an error but does not flip the enabled flag in the code shown.

Default policy builders use the fluent `Policy.Builder`: the volume-access policy grants tenant user role READ, LIST, and READ_ACL on the tenant volume and tenant admin role ALL; the bucket-access policy grants user role CREATE on all buckets in the volume and grants the Ozone owner principal ALL.

## State and persistence behavior
The interface itself stores no state. Implementations are expected to persist tenant state in OM metadata tables and synchronize with Ranger or another authorizer. Comments state OM DB is the source of truth for multi-tenant state. Static methods only derive names, validate config, or construct policy objects.

## Dependencies and integration points
It integrates with `OzoneManager`, `OMMetadataManager`, `OMException`, `Tenant`, `TenantUserList`, `OMRangerBGSyncService`, `MultiTenantAccessController.Policy/Acl`, `OzoneOwnerPrincipal`, Hadoop security (`SecurityUtil`, `UserGroupInformation`, Kerberos auth method), and OM/Ranger configuration keys. It is central to S3 multi-tenancy request handlers and background Ranger reconciliation.

## Risks and edge cases
`checkAndEnableMultiTenancy` throws `RuntimeException`, so startup validation failures can abort OM. The development skip flag bypasses validation and is useful for unit tests but dangerous if enabled in real deployments. The keytab existence check only logs an error in the provided code and does not change `isS3MultiTenancyEnabled`, which may allow startup to continue despite an invalid file path. Static name builders do not sanitize tenant ids or principals; callers must validate allowed characters earlier. Default policy shapes encode broad access semantics and should remain synchronized with Ranger authorizer expectations.

## Test signals
Tests should cover validation for disabled mode, dev skip, missing security, non-Kerberos auth, missing Ranger address/service, clear-text credential fallback, missing principal/keytab, nonexistent keytab path behavior, default access id and role/policy names, generated volume and bucket policy ACLs/labels/descriptions, admin check behavior in implementations, tenant lookup persistence, and Ranger background sync lifecycle.
