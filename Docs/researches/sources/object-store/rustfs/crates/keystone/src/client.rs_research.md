# sources/object-store/rustfs/crates/keystone/src/client.rs

## Purpose
`client.rs` implements `KeystoneClient`, the HTTP client for Keystone token validation, EC2 credential validation/listing, and admin-token acquisition. It is the network-facing layer used by `KeystoneAuthProvider`.

## Important APIs, Types, and Functions
`KeystoneClient::new` configures a `reqwest::Client`, Keystone auth URL/version, optional admin credentials, admin token cache, domain, and TLS verification behavior. `validate_token` dispatches between v3 and v2.0; v3 is implemented by `validate_token_v3`, while v2.0 returns `UnsupportedVersion`. `parse_token_v3` extracts user, project, domain, roles, `expires_at`, and `issued_at` from Keystone JSON. `validate_ec2_credentials` posts to `/v3/ec2tokens`. `get_ec2_credentials` uses `get_admin_token` to list OS-EC2 credentials. `clear_admin_token` clears cached admin auth.

## Control Flow
For token validation, the client sends `GET {auth_url}/v3/auth/tokens` with both `X-Auth-Token` and `X-Subject-Token` set to the user token. 404 and 401 become `InvalidToken`; other non-success statuses become `AuthenticationFailed`; successful JSON is parsed into `KeystoneToken`. For admin operations, `get_admin_token` first checks an async `RwLock<Option<AdminToken>>`, authenticates with password if missing/expired, reads `X-Subject-Token` from response headers, parses token expiry from the body, and caches it.

## State and Persistence Behavior
Admin token state is process-local in `Arc<RwLock<Option<AdminToken>>>`. User token and EC2 caches live in `auth.rs`, not this client. No disk persistence occurs. Timeout is hard-coded to 30 seconds in the reqwest builder, independent of `KeystoneConfig::timeout_seconds`.

## Dependencies and Integration Points
The client depends on `reqwest`, `serde_json`, `time`, `tokio::sync::RwLock`, and tracing. It integrates with Keystone v3 endpoints `/v3/auth/tokens`, `/v3/ec2tokens`, and `/v3/users/{user}/credentials/OS-EC2`. `EC2Credential::parse_access_key` is used as a fallback to infer user/project identifiers from an access key.

## Risks and Edge Cases
`parse_token_v3` sets `KeystoneToken.token` to `String::new()` rather than preserving the subject token, which affects credentials' `session_token`. TLS verification can be disabled with `danger_accept_invalid_certs`, and only a warning protects production use. Admin auth requires username/password but AppCred or token auth are not supported. `validate_ec2_credentials` discards the returned body and infers user/project from the access key, so it may not reflect authoritative Keystone EC2 credential metadata. v2.0 is advertised by config but unsupported at runtime.

## Test Signals
The unit test only checks constructor field assignment. Network behavior, parsing variants, admin token caching, TLS behavior, and EC2 credential parsing are not covered by active tests.
