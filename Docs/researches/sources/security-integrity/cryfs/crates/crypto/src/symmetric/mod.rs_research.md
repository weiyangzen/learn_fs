# sources/security-integrity/cryfs/crates/crypto/src/symmetric/mod.rs

## Purpose
Top-level symmetric encryption module defining cipher traits, public aliases, error types, and max key-size guarantees.

## Important APIs, types, and functions
- `Cipher` trait with `encrypt`, `decrypt`, and overhead accessors.
- `CipherDef` trait with `new`, `KEY_SIZE`, and overhead constants.
- `InvalidKeySizeError`.
- Re-exports `EncryptionKey`, AES-GCM aliases, XChaCha20-Poly1305 aliases, and `DefaultNonceSize`.
- `MAX_KEY_SIZE = 56` with `const_assert!` checks.

## Control flow
Traits define the runtime encryption/decryption contract. Concrete aliases select backends. Compile-time assertions verify supported ciphers do not exceed the maximum KDF-derived key size.

## State and persistence behavior
The module defines ciphertext shape expectations: prefix overhead stores nonce/IV and suffix overhead stores authentication tag. `MAX_KEY_SIZE` affects KDF strategy and backwards compatibility when switching ciphers.

## Dependencies and integration points
Used by CryFS encryption layers, KDFs, benchmarks, and tests. Integrates `Data`, `derive_more`, `static_assertions`, and backend modules.

## Risks and edge cases
The `Cipher::encrypt` API requires callers to provide `Data` with adequate reserved overhead; misuse can panic in backends. No associated data is part of the trait, so authenticated metadata must be handled by surrounding layers.

## Test signals
`cipher_tests.rs` validates the trait contract across all exported ciphers and backend combinations.
