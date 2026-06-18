# sources/object-store/garage/src/api/s3/encryption.rs

## Purpose
Centralizes S3 SSE-C handling for object metadata, inline object bytes, streamed blocks, copy-source decryption, and response headers. It supports plaintext and customer-provided AES256 keys, with newer objects using an object-specific encryption key derived from bucket ID, version ID, object key, and the customer key.

## Important APIs, Types, And Functions
`EncryptionParams` is either `Plaintext` or `SseC { client_key, client_key_md5, object_key, compression_level }`. `new_from_headers` parses upload SSE-C headers. `check_decrypt` and `check_decrypt_for_copy_source` validate request keys against stored object encryption metadata and return decrypted metadata. `encrypt_meta`, `encrypt_blob`, `decrypt_blob`, `encrypt_block`, `decrypt_block_stream`, and `get_block` implement metadata/inline/block encryption and decryption. `has_encryption_header` helps PUT/MPU decide whether MD5 ETags can be computed from plaintext. `OekDerivationInfo::derive_oek` creates per-object keys.

## Control Flow
Header parsing requires algorithm `AES256`, a base64 32-byte key, and a matching base64 MD5. Missing companion headers or unknown algorithms become bad requests. For encrypted stored metadata, `check_decrypt_common` requires the matching SSE-C headers, constructs the right key form depending on `use_oek`, decrypts the serialized metadata blob, and decodes `ObjectVersionMetaInner`. Plaintext objects reject decryption headers.

Block encryption optionally zstd-compresses the plaintext block, prefixes a random stream nonce, and encrypts 4096-byte plaintext chunks with AES-GCM stream mode. Decryption reads the nonce, buffers enough bytes to distinguish final and non-final chunks, decrypts chunk-by-chunk, and optionally wraps the plaintext stream in a zstd decoder.

## State And Persistence
The module does not write tables directly, but it defines persisted metadata shape through `ObjectVersionEncryption::SseC { inner, compressed, use_oek }`. It also determines stored block bytes and block hashes because encrypted/compressed bytes are what get hashed and stored. ETags for encrypted objects are random 16-byte hex strings rather than MD5s.

## Dependencies And Integration Points
Used by PUT, GET, COPY, MULTIPART, LIST parts, and POST object. Depends on AES-GCM, HMAC-SHA256, base64, md5, zstd, `garage_block`, `garage_net::stream`, `block_manager`, and Garage object table metadata encoding.

## Risks And Test Signals
Risks are high because chunk sizing and nonce layout are durable formats. Constants explicitly warn not to change encrypted stream chunk size. Decryption returns IO errors on malformed streams, and copy logic only reuses blocks when both sides are plaintext because Garage v2 object keys differ per version. Tests cover block encryption/decryption round trips with and without compression; header parsing, metadata migration, and malformed encrypted stream cases are not locally tested.
