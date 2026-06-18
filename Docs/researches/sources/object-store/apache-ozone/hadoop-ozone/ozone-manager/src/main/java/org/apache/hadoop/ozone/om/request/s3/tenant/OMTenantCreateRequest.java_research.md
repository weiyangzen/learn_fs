
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantCreateRequest.java

Purpose: Creates a tenant and its backing volume while provisioning default tenant roles/policies in Ranger and OM tenant metadata.

Important APIs and types: Extends `OMVolumeRequest`; uses `CreateTenantRequest/Response`, `CreateVolumeRequest`, `OmDBTenantState`, `OmVolumeArgs`, user volume lists, `OMMultiTenantManager`, `VOLUME_LOCK`, `USER_LOCK`, and `@DisallowedUntilLayoutVersion(MULTITENANCY_SCHEMA)`.

Control flow: `preExecute` checks cluster-admin privilege, validates tenant and volume names, verifies tenant and optionally volume non-existence, performs volume create ACL checks, generates volume timestamps and default role names, takes the Ranger authorizer write lock, creates Ranger tenant roles/policies, and embeds a `CreateVolumeRequest`. `validateAndUpdateCache` locks volume and user, creates or reuses the backing volume with ref-count handling, updates owner volume list when needed, verifies tenant absence, writes tenant state, updates the tenant cache, builds the response, audits, updates tenant/volume metrics, and releases all locks.

State and persistence behavior: Adds or updates volume table, user table, and tenant state table cache entries at the transaction index. It increments volume ref count for pre-existing forced volumes and creates in-memory tenant cache state.

Dependencies and integration points: Reuses volume-create helpers, integrates with Ranger authorizer operations, OM multi-tenant cache, audit logging, object ID allocation, metrics, layout-version gating, and RPC user identity.

Risks: Ranger side effects are performed before Ratis cache mutation; failures rely on background sync cleanup. Forced creation assumes volume ref count becomes exactly one. Tests should cover invalid delimiters, existing tenant, forced existing volume, user-name resolution failure, ACL failure auditing, ref-count behavior, and authorizer lock release.
