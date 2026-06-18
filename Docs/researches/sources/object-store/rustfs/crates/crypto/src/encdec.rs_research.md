<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec.rs

## Purpose
Module hub for encryption/decryption support.

## Important APIs, types, and functions
Conditionally includes `aes` when not `fips`, exposes crate-private `id` and `stream_io` under test or `crypto`, and always includes crate-private `decrypt` and `encrypt`. Test module is enabled under `cfg(test)`.

## Control flow
No runtime flow; compile-time cfg controls algorithm helper availability.

## State and persistence behavior
No state directly.

## Dependencies and integration points
Integrates encryption, decryption, algorithm id, stream_io compatibility, and AES hardware detection modules.

## Risks and edge cases
Cfg boundaries are important: non-crypto builds make encrypt/decrypt pass-through functions in child modules, while crypto builds perform real AEAD. Feature tests must catch accidental plaintext behavior in production builds.

## Test signals
Feature-matrix compilation and encdec tests validate module availability.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec.rs -->
