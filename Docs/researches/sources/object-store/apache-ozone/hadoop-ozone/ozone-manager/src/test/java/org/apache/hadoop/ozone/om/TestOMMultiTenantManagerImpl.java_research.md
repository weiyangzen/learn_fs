# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMultiTenantManagerImpl.java

Purpose: Tests `OMMultiTenantManagerImpl` cache behavior and tenant/user lookup APIs using a real `OmMetadataManagerImpl` and skip-Ranger mode.

Important APIs and types: `OMMultiTenantManagerImpl`, `CachedTenantState`, `OmDBTenantState`, `OmDBAccessIdInfo`, `TenantUserList`, `UserAccessIdInfo`, tenant/access-id tables, and cache operations `createTenant`, `assignUserToTenant`, `assignTenantAdmin`, and `revokeUserAccessId`.

Control flow: setup creates an OM metadata DB under a temp directory, seeds one tenant and one access ID directly in DB, mocks `OzoneManager`, and constructs the tenant manager. Tests add tenants and users through paired DB and cache operations, reconstruct the manager to verify cache reload, list users with/without prefix, revoke access IDs, and resolve tenant ID by access ID.

State and persistence: durable state is in tenant-state and tenant-access-id tables. In-memory state is `tenantCache`, which is rebuilt from those tables on manager construction and mutated through `getCacheOp`.

Dependencies and integration points: depends on multi-tenant helper naming conventions for default roles and bucket policies, OM metadata manager table layouts, Ranger sync interval config, and dev skip Ranger mode.

Risks and edge cases: cache reload must include tenants with no users and admin/delegated-admin flags; list prefix filtering must return empty lists without errors; revoking unknown access IDs must throw; revocation must keep tenant presence but remove user mapping.

Test signals: exact cache sizes and `CachedTenantState` equality, user/access-id pairs in `TenantUserList`, specific "Tenant 'tenant2' not found!" IOException, empty cache map after revocation, and `Optional` tenant lookup.
