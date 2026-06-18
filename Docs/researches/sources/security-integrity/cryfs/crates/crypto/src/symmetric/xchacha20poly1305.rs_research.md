# sources/security-integrity/cryfs/crates/crypto/src/symmetric/xchacha20poly1305.rs

## Purpose
Defines XChaCha20-Poly1305 type aliases for RustCrypto and libsodium backends, selecting libsodium as default.

## Important APIs, types, and functions
- `AeadXChaCha20Poly1305` maps to the generic RustCrypto AEAD adapter.
- `LibsodiumXChaCha20Poly1305` maps to the libsodium backend.
- `XChaCha20Poly1305` aliases libsodium as default.

## Control flow
No runtime control flow; backend behavior is in the referenced adapters.

## State and persistence behavior
XChaCha20 ciphertexts use 24-byte nonce prefix and 16-byte tag suffix. Default backend changes must keep this format interoperable.

## Dependencies and integration points
Publicly re-exported by `symmetric/mod.rs` and instantiated in tests/benchmarks.

## Risks and edge cases
Defaulting to libsodium introduces native dependency/runtime initialization needs, but interoperability tests ensure the RustCrypto format matches.

## Test signals
Cipher tests verify libsodium and RustCrypto XChaCha20 cross-decrypt each other's ciphertexts and can decrypt legacy fixed ciphertexts.
