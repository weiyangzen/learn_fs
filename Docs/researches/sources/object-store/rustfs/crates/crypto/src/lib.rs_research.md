# sources/object-store/rustfs/crates/crypto/src/lib.rs

## Purpose
This is the public facade for the `rustfs-crypto` crate. It wires internal encryption, error, JWT, and license-token modules into a small crate API and enforces `#![deny(clippy::unwrap_used)]` at crate level.

## Important APIs, Types, and Functions
The file declares private modules `encdec`, `error`, and `jwt`, plus public module `license_token`. It publicly re-exports `decrypt_data`, `encrypt_data`, the `Error` type, JWT helpers as `jwt_decode` and `jwt_encode`, and license helpers `Token`, `sign_license_token`, `parse_signed_license_token`, and `parse_license_with_public_key`. Stream I/O encryption helpers are exported only when the `crypto` feature is enabled.

## Control Flow
There is no runtime control flow beyond module resolution and conditional compilation. The file decides which lower-level functions become part of the stable crate surface and which remain implementation details.

## State and Persistence
No state is stored here. Persistence and cryptographic state are delegated to the re-exported modules. The feature-gated stream I/O exports can change available API shape depending on Cargo features.

## Dependencies and Integration Points
Downstream crates should import crypto behavior through this file rather than reaching into internal modules. `jwt_encode` and `jwt_decode` integrate with the JWT submodule, while license verification integrates with RSA signing code in `license_token.rs`.

## Risks and Edge Cases
The facade can accidentally expose or hide APIs through re-export changes. Deprecation of legacy license encryption helpers is enforced in `license_token.rs`, but this facade does not re-export the deprecated `gencode` and `parse`, which nudges callers toward public-key verification.

## Test Signals
There are no tests in this file. Behavior is covered indirectly by tests in `jwt/tests.rs`, `license_token.rs`, and any downstream crate tests using the public re-exports.
