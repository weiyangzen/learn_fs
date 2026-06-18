# sources/object-store/rustfs/crates/keystone/src/auth.rs

## Purpose
`auth.rs` implements `KeystoneAuthProvider`, the high-level bridge from Keystone tokens or EC2-style credentials into RustFS `Credentials`. It owns token caches, calls `KeystoneClient`, and constructs RustFS credential claims used by downstream auth and policy logic.

## Important APIs, Types, and Functions
`KeystoneAuthProvider::new` wraps a `KeystoneClient` in `Arc` and creates two `TokenCache` instances: one keyed by Keystone token string and one keyed by EC2 access/signature. `without_cache` disables cache checks for tests. `authenticate_with_token` validates an `X-Auth-Token`, rejects expired tokens, caches successful responses, and returns RustFS credentials. `authenticate_with_ec2` validates EC2 credentials through Keystone, converts the returned `EC2Credential` into a minimal `KeystoneToken`, caches it, and returns credentials. Helper methods include `invalidate_token`, `clear_caches`, `is_admin`, `get_project_id`, and `get_user_id`.

## Control Flow
Token authentication first checks `token_cache` when enabled, validates cache expiry with `KeystoneToken::is_expired`, then calls `client.validate_token`. After validation, it separately checks expiration and inserts the token into cache. EC2 authentication builds a cache key from `access_key:signature`, validates via `client.validate_ec2_credentials`, converts to a synthetic token, and caches the synthetic token.

## State and Persistence Behavior
All state is in-memory. `TokenCache` is a `moka::future::Cache` configured by constructor capacity/TTL. Cache entries store cloned `Arc<KeystoneToken>` values and can be invalidated per token or globally. No identity mapping is persisted.

## Dependencies and Integration Points
The provider depends on `KeystoneClient`, `KeystoneToken`, `EC2Credential`, `TokenCache`, and `KeystoneError` from the crate. It emits `rustfs_credentials::Credentials` with Keystone-specific claims in `serde_json::Value` form. Middleware calls `authenticate_with_token`; future SigV4 paths can call `authenticate_with_ec2`.

## Risks and Edge Cases
`ec2_to_keystone_token` is explicitly a placeholder: it sets username to `user_id`, project name to `project_id`, default role to `Member`, and a 24-hour expiry without fetching full Keystone user/project/role data. EC2 cache keys include the signature but not `string_to_sign`, which may be insufficient if the same access key/signature pair can arise over different signing strings. `keystone_token_to_credentials` uses an empty secret key and `keystone:<user_id>` access key, so downstream code must understand that session/token auth differs from normal S3 credentials. The token returned by `parse_token_v3` is currently empty, so `session_token` may be empty after live validation.

## Test Signals
Unit tests verify Keystone token conversion into RustFS credentials and admin role detection with case-insensitive `admin`. There are no tests using a mock Keystone server for success/failure cache paths or EC2 authentication.
