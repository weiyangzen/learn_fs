# sources/object-store/rustfs/crates/policy/src/utils.rs

## Purpose

Provides JWT helper functions for generating and extracting signed claim tokens using HMAC SHA-512.

## Important APIs, Types, and Functions

- `generate_jwt<T: Serialize>(claims, secret)` creates a JWT with `Algorithm::HS512`.
- `extract_claims<T: DeserializeOwned + Clone>(token, secret)` decodes and validates a JWT with the same HS512 algorithm.

## Control Flow

Token generation creates a new HS512 header and signs serialized claims with `EncodingKey::from_secret(secret.as_bytes())`. Extraction calls `jsonwebtoken::decode` with `DecodingKey::from_secret` and `Validation::new(Algorithm::HS512)`, returning `TokenData<T>` or a jsonwebtoken error.

## State and Persistence

No state or persistence. Secrets are caller-supplied strings used only during the call.

## Dependencies and Integration Points

Depends on `jsonwebtoken` and `serde`. Used by authentication or tests needing signed policy/IAM claims.

## Risks and Edge Cases

- Security rests entirely on caller-provided secret strength and lifecycle.
- `Validation::new` enforces standard jsonwebtoken defaults for the algorithm; callers should confirm issuer/audience/expiration requirements are configured elsewhere if needed.
- The round-trip extraction test is commented out, so decoding behavior is not locally exercised.

## Test Signals

Inline active test verifies that `generate_jwt` returns a non-empty token for a simple claims struct. A decode round-trip test exists but is commented out.
