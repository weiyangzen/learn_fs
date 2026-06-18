## sources/sync-backup/kopia/internal/blobcrypto/blob_crypto_test.go

Purpose: verifies blob crypto naming, encryption/decryption round trips, and failure paths.

Important APIs/types/functions: `TestBlobCrypto`, `badEncryptor`, and `TestBlobCrypto_Invalid`.

Control flow, state, and persistence: tests create a `StaticCrypter` from default format hashing/encryption, encrypt different payloads with prefix/suffix, decrypt with matching IDs, assert mismatched IDs and invalid payloads fail, and simulate bad hash/encryptor behavior.

Dependencies and integration points: exercises hashing, encryption, format configuration, and `gather.WriteBuffer`.

Risks and test signals: strong correctness signal for ID-derived IV behavior. Does not cover all encryption algorithms, but uses defaults representative of repository format.
