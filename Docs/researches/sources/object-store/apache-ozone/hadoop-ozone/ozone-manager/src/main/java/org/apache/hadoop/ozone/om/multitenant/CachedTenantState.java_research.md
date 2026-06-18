# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/CachedTenantState.java

## Purpose
`CachedTenantState` is an in-memory representation of tenant metadata needed by OM multi-tenancy logic: tenant id, role names, and access-id to user/admin mappings.

## Important APIs and Types
The main type stores `tenantId`, `tenantUserRoleName`, `tenantAdminRoleName`, and `HashMap<String, CachedAccessIdInfo>`. Nested `CachedAccessIdInfo` stores `userPrincipal` and mutable `isAdmin`.

## Control Flow
The constructor initializes identifiers and an empty access map. Getters expose role names, tenant id, and the mutable access map. `isTenantEmpty` checks whether the access map is empty. Equality compares identifiers and access map contents; nested equality compares principal and admin flag.

## State and Persistence Behavior
This class is explicitly in-memory cache state. It does not load or save data; callers populate it from OM tenant metadata and update it as tenant access IDs and admin status change.

## Dependencies and Integration Points
It is used by OM multi-tenant manager code to cache state derived from OM DB tables and authorizer roles/policies. It only depends on Java collections.

## Risks and Edge Cases
`getAccessIdInfoMap` exposes the mutable backing map. `hashCode` omits `accessIdInfoMap` even though `equals` includes it, which is legal only if identifiers define stable bucket placement; unequal hashes are not required for unequal objects, but equal objects must have same hash, and equal objects do because identifiers match. Concurrent callers need external synchronization.

## Test Signals
Tests should cover equality, mutable admin flag updates, empty detection, and map mutation behavior through the getter.
