<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/error.rs -->
# sources/object-store/rustfs/crates/crypto/src/error.rs

## Purpose
Defines the common error enum for crypto, JWT, encryption, signature, token, and I/O failures.

## Important APIs, types, and functions
`Error` variants include unexpected header, invalid algorithm id, invalid input, invalid key length, feature-gated digest/AEAD/Argon2 errors, JWT errors, I/O errors, invalid signature, and invalid token. It derives `thiserror::Error` for display/source behavior.

## Control flow
No control flow; other modules construct or convert into these variants through `From` on wrapped errors.

## State and persistence behavior
No state.

## Dependencies and integration points
Integrated by encdec, JWT encode/decode, and any RSA/signature/token code in the crate.

## Risks and edge cases
Feature-gated variants alter the enum shape across builds, so external matching should be cautious. Error messages are part of operator/debug behavior but should not leak secrets.

## Test signals
Compilation under feature combinations and tests for invalid headers/ids/JWT failures are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/error.rs -->
