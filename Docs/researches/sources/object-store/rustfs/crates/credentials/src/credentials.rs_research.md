<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/credentials.rs -->
# sources/object-store/rustfs/crates/credentials/src/credentials.rs

## Purpose
Implements credential generation, process-global active credentials, RPC authentication secret resolution/derivation, redacted formatting, and credential validity helpers.

## Important APIs, types, and functions
Key APIs are `init_global_action_credentials`, global access/secret getters, `gen_access_key`, `gen_secret_key`, `try_get_rpc_token`, deprecated `get_rpc_token`, `Masked`, `Credentials`, and methods `claims_or_empty`, `is_expired`, `is_temp`, `is_service_account`, `is_implied_policy`, `is_valid`, and `is_owner`. Errors use `CredentialsError`. RPC derivation uses HMAC-SHA256 over context `rustfs-rpc-secret:v1` plus access key, URL-safe base64 without padding.

## Control flow
Initialization chooses supplied keys or generates access length 20 and secret length 32, then sets a `OnceLock`. RPC token resolution first returns a cached valid global token, then tries non-empty/non-default `RUSTFS_RPC_SECRET`, otherwise derives from active access/secret credentials. Access key generation uses uppercase alphanumeric random chars and rejects length <3. Secret generation fills random bytes and encodes URL-safe no-padding base64, rejecting length <8.

## State and persistence behavior
Global credentials and RPC secret are one-shot process state in `OnceLock`s. `Credentials` serializes/deserializes JSON with MinIO-style camelCase aliases and optional RFC3339/legacy expiration via `serde_datetime`. No disk I/O occurs here, but serialized credentials are persisted by IAM/config layers.

## Dependencies and integration points
Integrates with `rustfs-credentials` constants, IAM service-account claims, RPC internode/auth setup, serde JSON, `time`, HMAC/SHA256, random generation, and base64-simd.

## Risks and edge cases
OnceLock makes tests/order and reconfiguration tricky; failed or default RPC env secrets intentionally produce a public error. `get_rpc_token` panics on missing secret and is deprecated. `is_owner` is hardcoded false, so owner semantics must live elsewhere. `is_valid` only checks status, key lengths, and expiration; it does not verify policy or signature.

## Test signals
Tests cover expiration/temp/service-account/implied-policy/validity, global credential flow, generation constraints, RPC secret derivation/default rejection/trimming, masked formatting including Unicode, debug redaction, and RFC3339 expiration serialization/deserialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/credentials.rs -->
