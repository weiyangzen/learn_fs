# sources/object-store/rustfs/crates/kms/src/service.rs

## Purpose
Implements S3-compatible object encryption/decryption on top of `KmsManager`, including SSE-S3, SSE-KMS-style behavior, and SSE-C customer-key encryption.

## Important APIs, Types, And Functions
`DataKey` holds a 32-byte plaintext key and 12-byte nonce and zeroizes key material on drop. `ObjectEncryptionService` delegates master-key APIs to `KmsManager` and provides `create_data_key`, `decrypt_data_key`, `encrypt_object`, `decrypt_object`, `encrypt_object_with_customer_key`, `decrypt_object_with_customer_key`, `metadata_to_headers`, and `headers_to_metadata`. `EncryptionResult` combines ciphertext and `EncryptionMetadata`. Helpers build canonical object encryption context and maintain an internal key-id header.

## Control Flow
`encrypt_object` reads the whole async reader into memory, determines the KMS key id from argument or default, builds encryption context, auto-creates an SSE-S3 key when using `AES256` and missing, requires non-AES/SSE-KMS keys to already exist, generates a DEK, creates the object cipher, generates an IV, serializes context as AAD, encrypts, and returns metadata containing IV/tag/context/encrypted data key. `decrypt_object` optionally validates expected context, parses algorithm, decrypts the encrypted data key through KMS using stored context, reconstructs AAD, and decrypts object ciphertext.

SSE-C validates a 32-byte customer key and optional MD5, uses the customer key directly for AES-256-GCM, stores no encrypted data key, marks `key_id` as `sse-c`, and requires that marker during decrypt.

## State And Persistence
Object encryption metadata is the persistence bridge: algorithm, key id, key version, IV, tag, context, timestamp, original size, and encrypted data key must be stored with the object. `metadata_to_headers` serializes this metadata into S3-facing and internal headers; `headers_to_metadata` reconstructs it, defaulting timestamp/size values unavailable from headers.

## Dependencies And Integration
Uses `KmsManager`, object cipher helpers, KMS types, base64, `jiff::Zoned`, `tokio::io::AsyncRead`, serde JSON for AAD/context, and `zeroize`. Integrates with S3 metadata/header handling via standard `x-amz-server-side-encryption` headers plus RustFS internal headers.

## Risks And Edge Cases
The implementation reads whole objects into memory despite crate-level documentation mentioning streaming; large objects need a streaming path. Context JSON serialization order for `HashMap` is not guaranteed across maps; this code decrypts using the stored metadata context, so round trips work, but independently reconstructed context bytes would be risky. `metadata_to_headers` uses `unwrap_or_default` for context serialization, which can silently emit an empty/invalid context header on serialization error. `decrypt_data_key` returns a zero nonce placeholder and relies on callers to restore stored nonce.

## Test Signals
Tests cover SSE-S3 encrypt/decrypt with auto-created default key, SSE-C encrypt/decrypt, metadata/header round trip with internal key id preservation, context validation failures, and `decrypt_data_key` rejecting mismatched object encryption context.
