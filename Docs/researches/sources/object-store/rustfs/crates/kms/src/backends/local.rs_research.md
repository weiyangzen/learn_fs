# sources/object-store/rustfs/crates/kms/src/backends/local.rs

## Purpose
`local.rs` implements a local file-backed KMS backend. It stores master key metadata and encrypted or base64-encoded key material as JSON files and provides both the low-level `KmsClient` trait and the simplified `KmsBackend` wrapper.

## Important APIs, Types, and Functions
`LocalKmsClient` holds `LocalConfig`, an in-memory `RwLock<HashMap<String, MasterKeyInfo>>` cache, optional `Aes256Gcm` master cipher, and `AesDekCrypto`. `StoredMasterKey` is the on-disk JSON shape. Core helpers include `new`, `derive_master_key`, `master_key_path`, `decode_stored_key`, `load_master_key`, `save_master_key`, `get_key_material`, `encrypt_with_master_key`, and `decrypt_with_master_key`. `LocalKmsBackend::new` validates `KmsConfig` and wraps a client.

## Control Flow
Client construction creates the key directory and derives an AES-256-GCM cipher from configured `master_key` using SHA-256 plus a static salt. Key creation validates algorithm, generates key material, saves it atomically through a temp file and rename, and caches metadata. Data-key generation creates random DEK material, encrypts it with the master key via `AesDekCrypto`, wraps it in `DataKeyEnvelope`, and serializes the envelope as ciphertext. Decryption parses the envelope, checks encryption context compatibility, and decrypts the encrypted DEK. Listing scans `.key` files and applies status/usage filters. The backend wrapper converts between client-level `KeyInfo`/`MasterKeyInfo` and API-level metadata responses.

## State and Persistence Behavior
Master keys persist as `<key_id>.key` JSON under `LocalConfig.key_dir`. When `master_key` is configured, stored key material is encrypted with AES-256-GCM and a 12-byte nonce; otherwise raw key material is base64 encoded with a warning that keys are not encrypted at rest. Writes are atomic via `.tmp` then rename, with optional Unix file permissions applied to the temp file. Metadata is cached in memory but key material is re-read from disk for encryption/decryption.

## Dependencies and Integration Points
The backend depends on RustFS KMS config, types, error handling, `AesDekCrypto`, `generate_key_material`, `serde_json`, `jiff::Zoned`, `tokio::fs`, and crypto/base64/rand crates. It implements both `KmsClient` and `KmsBackend`, so it can be used by lower-level KMS code and the service manager.

## Risks and Edge Cases
Several low-level state transitions (`enable_key`, `disable_key`, `schedule_key_deletion`, `cancel_key_deletion`, `rotate_key`) regenerate key material, which can make existing encrypted data undecryptable if those methods are used directly. The simplified backend wrapper's scheduled deletion/cancel paths explicitly preserve existing key material, creating different safety semantics than the lower-level trait. `encrypt` returns raw AEAD ciphertext without carrying nonce, and tests note direct decrypt of `encrypt()` results is not implemented. `describe_key` can serve stale metadata from cache if files are changed externally. Key IDs are used directly in file names without visible path sanitization in this file.

## Test Signals
Unit tests cover key lifecycle, data-key generation/decryption with context, direct encryption response shape, and loading a legacy RFC3339 timestamp. They do not cover deletion wrapper semantics, path traversal, concurrent writes, cache invalidation, or encryption-at-rest failure modes.
