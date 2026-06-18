# sources/object-store/rustfs/crates/keystone/src/lib.rs

## Purpose
`lib.rs` is the public crate surface for RustFS Keystone integration. It documents supported features, declares modules, re-exports the primary types, and defines core shared data structures such as `KeystoneToken`, `EC2Credential`, `KeystoneVersion`, and `TokenCache`.

## Important APIs, Types, and Functions
Public modules are `auth`, `client`, `config`, `error`, `identity`, and `middleware`. Re-exports include `KeystoneAuthProvider`, `KeystoneClient`, `KeystoneConfig`, `RoleMapping`, `KeystoneError`, `Result`, `KeystoneIdentityMapper`, `KEYSTONE_CREDENTIALS`, and `KeystoneAuthLayer`. `KeystoneVersion` supports `V2_0` and `V3`. `KeystoneToken` stores token identity, project/domain, roles, and timestamps with helpers `is_expired`, `has_role`, and `is_admin`. `EC2Credential` stores EC2 access/secret/user/project/trust data and parses access keys. `TokenCache` wraps `moka::future::Cache<String, Arc<KeystoneToken>>`.

## Control Flow and Integration Points
Downstream code imports the crate-level re-exports to configure clients, validate tokens, install middleware, and inspect task-local Keystone credentials. Token expiry and role checks are shared by auth provider and callers. EC2 credential parsing supports `client.rs` fallback behavior after Keystone EC2 validation.

## State and Persistence Behavior
`TokenCache` stores token info in memory with capacity and TTL configured at construction. It supports async get/insert/invalidate/clear. The module itself has no disk persistence.

## Dependencies
The crate root uses `moka`, `serde`, `time`, `Arc`, and `Duration`. It relies on `time::OffsetDateTime` for token lifetimes.

## Risks and Edge Cases
`KeystoneToken::has_role` is case-sensitive, while `is_admin` checks only exact `admin` or `Admin`; `KeystoneAuthProvider::is_admin` is more permissive and also accepts `reseller_admin`. `EC2Credential::parse_access_key` always returns `Some`, even for empty strings, and only treats exactly one colon as a user/project separator. `TokenCache::clear` invalidates all entries but does not call `run_pending_tasks`, so invalidation timing follows moka's async behavior.

## Test Signals
There are no direct tests in `lib.rs`; shared types are covered indirectly by `auth.rs`, `client.rs`, middleware, and identity unit tests.
