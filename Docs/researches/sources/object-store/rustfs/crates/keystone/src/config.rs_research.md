# sources/object-store/rustfs/crates/keystone/src/config.rs

## Purpose
`config.rs` defines environment-driven configuration for Keystone integration. It controls whether Keystone auth is enabled, how Keystone is contacted, cache behavior, tenant prefixing, implicit tenants, and optional role-to-policy mappings.

## Important APIs, Types, and Functions
`KeystoneConfig` contains fields for `enable`, `auth_url`, `version`, admin credentials/project/domain, `verify_ssl`, cache size/TTL, tenant prefixing, implicit tenants, timeout, and `role_mappings`. `RoleMapping` maps Keystone role names to RustFS policy names. `from_env` reads `RUSTFS_KEYSTONE_*` variables. `get_version`, `get_cache_ttl`, `get_timeout`, `get_admin_domain`, and `validate` provide typed access and validation. `Default` represents Keystone disabled with v3 defaults and caching/tenant prefix enabled.

## Control Flow
`from_env` first reads `RUSTFS_KEYSTONE_ENABLE`; if disabled, it returns `Default`. If enabled, it requires `RUSTFS_KEYSTONE_AUTH_URL`, then reads optional admin credentials and booleans/numerics with defaults. `validate` no-ops when disabled, requires non-empty `auth_url` when enabled, validates version, and warns if admin credentials are missing.

## State and Persistence Behavior
Configuration is immutable data after construction and has no persistence. Runtime caches and clients consume its values. `role_mappings` is present but `from_env` never populates it.

## Dependencies and Integration Points
The file uses `rustfs_utils` environment helpers and converts version strings to `KeystoneVersion` for `KeystoneClient`. `KeystoneAuthProvider` consumes cache settings and `KeystoneIdentityMapper` can consume tenant-prefix and role mapping fields.

## Risks and Edge Cases
`timeout_seconds` is exposed but `KeystoneClient::new` currently uses a fixed 30-second reqwest timeout, so the config value may be ignored unless wired elsewhere. Enabling v2.0 passes validation but token validation later returns `UnsupportedVersion`. Missing admin credentials only warn even though EC2 credential listing requires them. Environment configuration cannot define `role_mappings`.

## Test Signals
Unit tests cover defaults, version parsing, full environment loading via `temp_env`, and invalid version handling. They do not cover `validate` warnings or runtime consumption of timeout/role mappings.
