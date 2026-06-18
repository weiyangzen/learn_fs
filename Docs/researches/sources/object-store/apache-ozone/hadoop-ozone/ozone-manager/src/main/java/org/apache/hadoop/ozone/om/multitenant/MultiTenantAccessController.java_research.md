# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/MultiTenantAccessController.java

## Purpose
`MultiTenantAccessController` abstracts tenant access-control operations over Ranger or a development in-memory backend. It defines policy and role models, ACL mapping, and factory selection.

## Important APIs and Types
The interface declares policy CRUD (`createPolicy`, `getPolicy`, `getLabeledPolicies`, `updatePolicy`, `deletePolicy`), role CRUD (`createRole`, `getRole`, `updateRole`, `deleteRole`), and `getRangerServicePolicyVersion`. Static `getRangerAclStrings` maps Ozone ACL enum values to Ranger strings. Nested classes model `Acl`, `Role`, `Role.Builder`, `Policy`, and `Policy.Builder`.

## Control Flow
`Acl.allow` and `Acl.deny` construct immutable allow/deny values. `Role.Builder` accumulates role name, user and role admin maps, description, id, and creator. `Role.equals` treats absent role IDs as compatible but compares IDs when both are present. `Policy.Builder` accumulates resource sets, labels, user ACLs, role ACLs, description, id, and enabled flag; `build` requires a non-empty name. `create(ConfigurationSource)` chooses `InMemoryMultiTenantAccessController` when dev skip Ranger is set, otherwise reflectively loads `RangerClientMultiTenantAccessController`.

## State and Persistence Behavior
The interface and nested model classes are in-memory value objects. Persistence is implemented by concrete controllers: Ranger-backed controller persists to Ranger; in-memory controller does not. Policy version is the external synchronization signal used by OM tenant code.

## Dependencies and Integration Points
It depends on `IAccessAuthorizer.ACLType`, `ConfigurationSource`, `ReflectionUtils`, and `OMMultiTenantManagerImpl.OZONE_OM_TENANT_DEV_SKIP_RANGER`. Tenant create/delete/admin/access-id requests use these types to express desired Ranger state.

## Risks and Edge Cases
Builders expose mutable maps/sets into constructed objects rather than defensive immutable copies, so callers retaining builder references can mutate built roles/policies. `Policy.Builder.setId(Long)` unboxes into a primitive long and will throw on null. The reflective class name creates a runtime dependency not visible to the compiler in this file.

## Test Signals
Tests should cover ACL string mapping, equality semantics with optional role IDs, policy name validation, builder mutation behavior, factory selection based on configuration, and Ranger-client class loading failures.
