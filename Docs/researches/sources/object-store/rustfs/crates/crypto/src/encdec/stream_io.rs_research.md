<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/stream_io.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/stream_io.rs

## Purpose
Implements sio-go compatible fragmented stream encryption/decryption for IAM config data.

## Important APIs, types, and functions
Public APIs are `encrypt_stream_io` and `decrypt_stream_io`. Format header is salt(32) + alg_id(1) + nonce_prefix(8). Body uses DARE-style 16 KiB fragments, 12-byte nonces composed from prefix plus little-endian sequence number, 16-byte AEAD tags, and associated data derived by encrypting an empty block with sequence zero. Algorithm selection mirrors `encrypt_data`: PBKDF2/AES-GCM under FIPS, otherwise native-AES based Argon2id AES-GCM or ChaCha20Poly1305.

## Control flow
Decrypt validates the 41-byte header, derives key, selects AEAD, then iterates fragments using ciphertext chunk size 16384+tag, setting associated-data first byte to `0x80` for the last fragment. Encrypt builds the header, then chunks plaintext into 16 KiB fragments, marks the last fragment, encrypts in place detached, and appends tag per fragment.

## State and persistence behavior
No mutable global state. The stream_io byte format is a persisted interoperability contract for IAM/config encrypted blobs.

## Dependencies and integration points
Integrates with sio-go compatibility expectations, `ID` key derivation, AES-GCM, ChaCha20Poly1305, rand, and crate errors.

## Risks and edge cases
Fragment boundaries, final-fragment marker, nonce sequence, and associated-data construction are all compatibility-sensitive. Empty plaintext currently emits only a header with no final encrypted fragment; decrypt returns empty, but cross-implementation behavior should be checked. Sequence number overflow is not handled for extremely large streams.

## Test signals
Tests cover stream_io roundtrip, >16 KiB fragmentation, wrong password failure, empty data, and header format. Cross-language tests with sio-go vectors would be a stronger signal.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/stream_io.rs -->
