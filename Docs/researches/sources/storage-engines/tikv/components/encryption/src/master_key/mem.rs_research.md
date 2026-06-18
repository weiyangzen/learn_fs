# sources/storage-engines/tikv/components/encryption/src/master_key/mem.rs

Purpose: Provides the in-memory AES-256-GCM backend shared by file and KMS master-key backends. It encrypts/decrypts `EncryptedContent` using a plaintext master key held in memory.

Important APIs and types: `MemAesGcmBackend::new`, `encrypt_content`, and `decrypt_content`. The backend stores a `cloud::kms::PlainKey` typed as AES-GCM-256.

Control flow: Construction validates the raw key through `PlainKey::new`. Encryption writes metadata `method=aes256-gcm`, IV bytes, and GCM tag, and stores ciphertext content. Decryption checks method, IV, and tag metadata before authenticating and decrypting the content.

State and persistence behavior: The only runtime state is the plaintext key. Serialized state appears in `EncryptedContent` metadata and content fields. Authentication failures are classified as `WrongMasterKey`; malformed or unsupported metadata is `Other`.

Dependencies and integration: Used directly by `FileBackend` and internally by `KmsBackend::State`. It depends on crate `AesGcmCrypter`, `AesGcmTag`, `Iv`, master-key metadata keys, and cloud key wrappers.

Risks: The method mismatch path intentionally does not fallback as wrong master key, because unsupported future formats should fail clearly. Tag mismatch is ambiguous between corruption, attack, and wrong key, so it returns `WrongMasterKey` for manager fallback compatibility.

Test signals: Tests verify an external AES-GCM test vector, successful authentication, missing method, invalid method, missing tag, and mismatched tag classification.
