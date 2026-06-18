# sources/storage-engines/tikv/components/encryption/src/master_key/kms.rs

Purpose: Implements a master-key backend that obtains and decrypts data keys through a cloud KMS provider, caches the current plaintext data key, and encrypts metadata with AES-256-GCM.

Important APIs and types: `KmsBackend::new`, `encrypt_content`, `decrypt_content`, async counterparts, and test-only `clear_state` are main APIs. Internal `State` stores `MemAesGcmBackend` plus cached KMS ciphertext key. Test module `fake` provides `FakeKms` and vector fixtures.

Control flow: Sync APIs lock a single-thread Tokio runtime and block on async work. Encryption lazily calls `KmsProvider::generate_data_key` with timeout and retry, builds a memory GCM backend, encrypts plaintext, and adds KMS vendor and ciphertext-key metadata. Decryption validates vendor, parses ciphertext key, reuses cached state if the ciphertext key matches, otherwise calls KMS `decrypt_data_key`, builds state, decrypts, and caches it.

State and persistence behavior: Cached state is held in an async mutex and avoids repeated KMS decrypts for the same encrypted data key. Durable state lives only in `EncryptedContent` metadata: method/IV/tag from GCM plus KMS vendor and ciphertext key.

Dependencies and integration: Depends on `cloud::kms`, `tikv_util::stream::{retry, with_timeout}`, Tokio runtime, thread hooks, and `MemAesGcmBackend`. It satisfies both sync `Backend` and async `AsyncBackend`, so it works for key dictionaries and multi-master-key restore.

Risks: A runtime mutex serializes sync API calls. Missing KMS vendor returns `WrongMasterKey` to allow fallback to non-KMS backends; vendor mismatch returns `Other`. KMS decrypt failures are wrapped as `WrongMasterKey`, which may hide transient/cloud detail except through the nested message. Timeout is fixed at 10 seconds.

Test signals: Tests cover state caching identity, known-vector encryption/decryption through fake KMS, missing/invalid vendor, missing ciphertext key, and wrong KMS data-key behavior after clearing cache.
