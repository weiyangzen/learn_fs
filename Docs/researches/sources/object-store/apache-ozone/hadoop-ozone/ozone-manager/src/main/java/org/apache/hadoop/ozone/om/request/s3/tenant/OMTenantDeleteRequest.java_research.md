
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantDeleteRequest.java

Purpose: Deletes an empty tenant, removes Ranger tenant policies/roles, invalidates tenant state, and decrements the backing volume ref count.

Important APIs and types: Extends `OMVolumeRequest`; uses `DeleteTenantRequest/Response`, `OmDBTenantState`, `OmVolumeArgs`, `OzoneTenant`, `OMMultiTenantManager`, `tenantStateTable`, `volumeTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` checks cluster-admin privilege, verifies the tenant has no access IDs, loads tenant metadata and volume name, checks volume ACLs when enabled, takes the authorizer write lock, and calls Ranger `deleteTenant`. Validation verifies tenant existence, reads the backing volume name, locks the volume, invalidates tenant state in cache, decrements volume ref count when applicable, updates tenant cache, returns volume name/ref count, audits, and updates metrics.

State and persistence behavior: Adds a tombstone cache entry for tenant state and an updated volume table entry with decremented ref count. The tenant cache is updated immediately; Ranger state is changed before DB mutation.

Dependencies and integration points: Coordinates OM tenant metadata, volume metadata, Ranger authorizer cleanup, tenant cache, ACL framework, audit, and metrics.

Risks: Deleting non-empty tenants is blocked only by multi-tenant manager state, so stale cache/DB mismatches matter. Empty volume names are rejected in preExecute, but validation still has a `decVolumeRefCount` branch for empty values. Tests should cover non-empty tenants, missing tenant, ACL rejection audit, volume ref count decrement, and Ranger failure paths.
