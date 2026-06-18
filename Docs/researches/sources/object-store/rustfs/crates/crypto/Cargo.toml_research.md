<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/Cargo.toml -->
# sources/object-store/rustfs/crates/crypto/Cargo.toml

## Purpose
Declares the `rustfs-crypto` crate metadata, dependencies, feature gates, and library settings.

## Important APIs, types, and functions
Default features are `crypto` and `fips`. Optional crypto dependencies include AES-GCM, Argon2, ChaCha20Poly1305, PBKDF2, rand, and sha2. JWT/RSA/serde/serde_json/thiserror are unconditional. Doctests are disabled.

## Control flow
Cargo feature selection controls whether encryption code is active and whether FIPS selects PBKDF2/AES-GCM paths.

## State and persistence behavior
No runtime state. Feature choices alter compiled algorithms and fallback behavior.

## Dependencies and integration points
Integrates with workspace dependency versions, JWT code, encryption/decryption modules, and tests requiring crypto feature dependencies.

## Risks and edge cases
Defaulting to both `crypto` and `fips` means default encryption chooses PBKDF2/AES-GCM instead of non-FIPS Argon2/ChaCha selection. Optional dependency drift can change cryptographic behavior.

## Test signals
Cargo feature-matrix builds and encryption/JWT tests are the key signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/Cargo.toml -->
