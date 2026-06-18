<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/tests.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/tests.rs

## Purpose
Test suite for the encryption/decryption and stream_io compatibility modules.

## Important APIs, types, and functions
Uses `encrypt_data`, `decrypt_data`, `encrypt_stream_io`, and `decrypt_stream_io` with fixed password constants and `test-case` parameterization.

## Control flow
Tests run roundtrips over small, empty, binary, unicode, large, and varied-password inputs; verify wrong-password and corrupted/truncated/header-invalid data fail; verify ciphertext differs for repeated encryption; inspect minimum envelope structure; spawn concurrent encryption threads; and validate stream_io roundtrip, fragmentation, wrong password, empty data, and header id.

## State and persistence behavior
No persistent state. Some tests touch global CPU/feature-dependent algorithm choices only through envelope id allowances.

## Dependencies and integration points
Integrates with the entire encdec module, random generation, AEAD error handling, and thread safety.

## Risks and edge cases
Tests are strong for functional roundtrip but do not include external known-answer vectors or cross-language sio-go fixtures. Randomized outputs mean tests assert properties rather than exact ciphertext.

## Test signals
Passing this suite signals correct local encryption, decryption, tamper detection, concurrency safety, and stream_io header/fragment behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/tests.rs -->
