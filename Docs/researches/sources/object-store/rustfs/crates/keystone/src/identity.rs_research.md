# sources/object-store/rustfs/crates/keystone/src/identity.rs

## Purpose
`identity.rs` maps Keystone identity concepts to RustFS authorization and multi-tenant storage concepts. It translates Keystone roles to policy names, applies/removes project ID bucket prefixes, and provides simplified role-based permission checks.

## Important APIs, Types, and Functions
`KeystoneIdentityMapper` stores an `Arc<KeystoneClient>`, a `role_policy_map`, and an `enable_tenant_prefix` flag. `new` seeds default mappings for `admin`, `Admin`, `Member`, `_member_`, `ResellerAdmin`, `SwiftOperator`, `objectstore:admin`, and `objectstore:creator`. Public methods include `add_role_mapping`, `add_role_mappings`, `map_roles_to_policies`, `apply_tenant_prefix`, `remove_tenant_prefix`, `is_project_bucket`, `extract_project_id`, `create_default_policies`, `has_permission`, and `is_tenant_prefix_enabled`.

## Control Flow
Role mapping is a direct hash lookup; unmapped roles are ignored. Bucket prefixing prepends `<project_id>:` when enabled and a project ID is present. `is_project_bucket` allows all buckets when prefixing is disabled, requires a matching prefix when a project ID is present, and allows only unprefixed buckets when no project ID is present. `has_permission` first grants admin/reseller-admin, then applies broad action prefix checks for mapped read-write and read-only policies.

## State and Persistence Behavior
The mapper is in-memory and mutable only through explicit role mapping methods. The stored client is currently unused but preserves room for future Keystone lookups.

## Dependencies and Integration Points
It depends on `rustfs_policy::policy::Policy` for parsing default policy JSON. It consumes roles produced in `KeystoneToken`/`Credentials` and bucket project IDs extracted by `KeystoneAuthProvider`.

## Risks and Edge Cases
Bucket prefixing uses a colon separator and simple string matching; bucket names containing colons may be treated as project-prefixed. `extract_project_id` returns the substring before the first colon without validating it. `create_default_policies` silently skips invalid policy JSON parse failures. `has_permission` is intentionally simplified and resource-agnostic: it ignores the `_resource` argument and grants based only on action prefixes.

## Test Signals
Unit tests cover tenant prefix apply/remove, project bucket checks, project ID extraction, role mapping, simplified permission checks, and custom mapping insertion. They do not validate parsed `Policy` semantics beyond successful creation.
