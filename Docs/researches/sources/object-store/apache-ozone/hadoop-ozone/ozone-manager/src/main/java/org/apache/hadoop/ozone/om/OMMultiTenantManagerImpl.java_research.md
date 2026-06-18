# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMultiTenantManagerImpl.java

Purpose: `OMMultiTenantManagerImpl` implements `OMMultiTenantManager` for Ozone Manager S3 multi-tenancy. It coordinates OM metadata tables, in-memory tenant cache, Ranger-backed authorizer state, tenant authorization checks, and the background Ranger reconciliation service.

Important APIs and types: the constructor loads tenant cache from DB, creates `MultiTenantAccessController`, installs `AuthorizerOp` and `CacheOp`, and starts `OMRangerBGSyncService`. Public APIs expose `getAuthorizerOp()`, `getCacheOp()`, `checkAdmin()`, `checkTenantAdmin()`, `checkTenantExistence()`, tenant role/name lookups, tenant emptiness checks, `getAllRolesFromCache()`, and `getAuthorizerLock()`. `AuthorizerOp` mutates Ranger roles/policies; `CacheOp` mutates `CachedTenantState`.

Control flow: tenant changes are split between pre-execute authorizer work and validate-and-update-cache work. `AuthorizerOp` requires the `AuthorizerLock` write lock, creates/deletes tenant roles and policies, updates user/admin roles, and wraps Ranger I/O failures as `TENANT_AUTHORIZER_ERROR`. `CacheOp` uses a write lock to mirror successful DB mutations into `tenantCache`. Read paths use the tenant DB tables and cache to list users, resolve access IDs, and evaluate tenant admin status.

State and persistence: OM DB tables are the durable source (`tenantStateTable`, `tenantAccessIdTable`, `principalToAccessIdsTable`). `tenantCache` is rebuilt from those tables on startup, and stores tenant role names plus accessId to principal/admin flags. Ranger state is external and eventually reconciled by the background sync service.

Dependencies and integration points: depends on `OzoneManager`, `OMMetadataManager`, Ranger-oriented `MultiTenantAccessController`, `AuthorizerLock`, `CachedTenantState`, tenant helper DB objects, RPC remote user context, and `OMRangerBGSyncService`.

Risks: the code relies on correct lock ordering between authorizer, cache, and DB update phases; partial Ranger failures are intentionally repaired later, so tests must cover idempotency and background reconciliation. Cache rebuild throws runtime exceptions on inconsistent DB rows. `getUserNameGivenAccessId` logs and returns null on I/O, which can flow into admin-role updates if callers fail validation.

Test signals: useful coverage includes tenant create/delete idempotency, Ranger failure wrapping, cache rebuild from DB tables, accessId revocation, delegated versus non-delegated tenant admin checks, orphaned accessId metadata, and concurrent read/write lock behavior.
