# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/InMemoryMultiTenantAccessController.java

## Purpose
`InMemoryMultiTenantAccessController` is a development/testing implementation of `MultiTenantAccessController` that keeps policies and roles in local maps rather than talking to Ranger.

## Important APIs and Types
It implements policy CRUD, role CRUD, and `getRangerServicePolicyVersion`. Fields are `policies`, `roles`, `nextRoleID`, and `serviceVersion`.

## Control Flow
`createPolicy` rejects duplicate policy names and duplicate resource sets, stores the policy, creates missing roles referenced by role ACLs, and increments service version. `getLabeledPolicies` filters policies by label. `updatePolicy` and `deletePolicy` require existing names and increment service version. `createRole` rejects duplicates, builds a copy with the next role id, stores it, increments id and service version, and returns the input role rather than the id-enriched copy. `updateRole` finds by id, removes the old role name, stores the supplied role, and increments version. `deleteRole` removes by name.

## State and Persistence Behavior
All state is process-local and lost on restart. `serviceVersion` simulates Ranger policy version changes for synchronization logic but is not durable.

## Dependencies and Integration Points
`MultiTenantAccessController.create` selects this implementation when `OZONE_OM_TENANT_DEV_SKIP_RANGER` is true. It supports tenant OM requests and tests that should not require a Ranger service.

## Risks and Edge Cases
The class is not synchronized and is unsuitable for concurrent production use. Returning the original role from `createRole` means callers expecting the assigned id from the return value may be surprised, although `getRole` returns the stored id-enriched role. Duplicate resource detection uses exact set equality.

## Test Signals
Tests should cover duplicate policy/resource rejection, automatic role creation from policy ACLs, service version increments, role update by id, and the createRole return-value behavior.
