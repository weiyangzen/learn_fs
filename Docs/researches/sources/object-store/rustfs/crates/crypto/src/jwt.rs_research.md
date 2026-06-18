<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt.rs -->
# sources/object-store/rustfs/crates/crypto/src/jwt.rs

## Purpose
Module root for JWT helpers and shared claims type.

## Important APIs, types, and functions
Declares `decode` and `encode` modules and re-exports `serde_json::Value` as `Claims`; includes a test module under `cfg(test)`.

## Control flow
No runtime flow; child modules call the `jsonwebtoken` crate.

## State and persistence behavior
No state.

## Dependencies and integration points
Used by authentication/session code that needs HS512 JWT encode/decode over arbitrary JSON claims.

## Risks and edge cases
`Claims` as generic JSON value gives flexibility but little static validation. Callers must enforce required claims, expiration, issuer, and audience semantics.

## Test signals
JWT encode/decode roundtrip and validation failure tests are expected signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt.rs -->
