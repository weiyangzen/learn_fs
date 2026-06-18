# sources/security-integrity/cryfs/crates/crypto/src/symmetric/cipher_tests.rs

## Purpose
Comprehensive generic test suite for symmetric cipher correctness, interoperability, size accounting, nondeterminism, and backwards-compatible ciphertext formats.

## Important APIs, types, and functions
- Helper `key(num_bytes, seed)` creates deterministic `EncryptionKey`.
- `allocate_space_for_ciphertext<C>` creates `Data` with required overhead.
- Generic `enc_dec` tests cover encrypt/decrypt pairs, tamper, short ciphertext, and wrong key.
- Generic `basics` tests cover overhead size math and nonce nondeterminism.
- `backward_compatibility_test!` decrypts fixed ciphertext hex fixtures.

## Control flow
The suite instantiates test modules for default aliases, concrete OpenSSL/RustCrypto/libsodium backends, nonce-size variants, and selected cross-backend encrypt/decrypt pairs. Compatibility tests decrypt preencrypted `"Hello World"` ciphertexts with deterministic keys.

## State and persistence behavior
Fixed ciphertext hex strings encode the durable ciphertext layout contract for nonce prefix, ciphertext body, and tag suffix. Tests also model required `Data` reserved regions.

## Dependencies and integration points
Uses `generic-tests`, typenum `U12`/`U16`, `cryfs_utils::Data`, and all public cipher aliases. It is the main guard against backend format drift.

## Risks and edge cases
Libsodium AES-GCM tests are architecture-gated by x86/x86_64 but still may require runtime hardware support. Tests deliberately do not assert exact encryption output for fresh operations because nonces are random.

## Test signals
Signals include successful round trips, failed tamper/wrong-key/too-small decryptions, expected ciphertext length overheads, fresh encryption inequality, cross-backend interoperability, and exact legacy decryptability.
