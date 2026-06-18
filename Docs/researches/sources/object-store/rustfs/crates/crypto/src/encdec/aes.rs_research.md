<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/aes.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/aes.rs

## Purpose
Detects whether the current CPU has native AES acceleration needed for algorithm selection.

## Important APIs, types, and functions
`native_aes()` checks AES/PCLMUL on x86/x86_64, AES on aarch64, returns false on powerpc64, checks AES/AESCBC/AESCTR plus AESGCM or GHASH on s390x, and false on other targets.

## Control flow
Uses `cfg_select!` to compile target-specific feature detection. No caching is performed.

## State and persistence behavior
No persistent state; each call queries CPU feature macros.

## Dependencies and integration points
Used by non-FIPS encryption and stream_io code to choose Argon2id+AES-GCM when hardware support exists, otherwise Argon2id+ChaCha20Poly1305.

## Risks and edge cases
Incorrect feature detection can choose a slow or unsupported algorithm. Returning false on powerpc64 may force ChaCha even where AES exists. This module is absent under `fips`.

## Test signals
Cross-architecture build tests and runtime algorithm-id tests on representative CPUs are useful signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/aes.rs -->
