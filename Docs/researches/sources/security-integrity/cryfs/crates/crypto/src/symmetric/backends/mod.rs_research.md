# sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/mod.rs

## Purpose
Aggregator module for symmetric cipher backend implementations.

## Important APIs, types, and functions
- Public submodules `aead`, `cipher`, `libsodium`, and `openssl`.

## Control flow
No runtime control flow.

## State and persistence behavior
No state.

## Dependencies and integration points
Concrete cipher aliases in `aesgcm.rs` and `xchacha20poly1305.rs` refer to these backend modules.

## Risks and edge cases
All backend modules are compiled together; TODO notes indicate future feature-gating and production backend choice work.

## Test signals
Covered indirectly by the shared cipher tests instantiated for aliases using each backend.
