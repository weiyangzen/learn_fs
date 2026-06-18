<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/encode.rs -->
# sources/object-store/rustfs/crates/crypto/src/jwt/encode.rs

## Purpose
Provides HS512 JWT encoding using a shared secret.

## Important APIs, types, and functions
`encode(token_secret, claims)` creates a `Header::new(Algorithm::HS512)` and signs arbitrary JSON `Claims` with `EncodingKey::from_secret`.

## Control flow
The function is a direct wrapper around `jsonwebtoken::encode`, mapping errors into crate `Error`.

## State and persistence behavior
No state.

## Dependencies and integration points
Integrates with session/auth token issuance and the decode helper's HS512 expectations.

## Risks and edge cases
Claims are not enriched or validated here; callers must include expiration, subject, issuer, and audience as needed. Secret entropy is not enforced.

## Test signals
Tests should cover encode/decode roundtrip, expected HS512 header, and failure with non-serializable or invalid claims if applicable.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/encode.rs -->
