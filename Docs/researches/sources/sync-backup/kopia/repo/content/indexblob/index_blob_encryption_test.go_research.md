# sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption_test.go_research.md`.

Purpose: verifies index blob encryption manager behavior across success, corrupted ciphertext, missing blobs, storage write faults, and encryptor failures.

Important fixtures: a map blob store is wrapped with `blobtesting.FaultyStorage`. A test `format.ContentFormat` creates hashing and encryption providers. `blobcrypto.StaticCrypter` supplies the crypter. `failingEncryptor` injects an encryption error while satisfying the encryptor interface.

Control flow and assertions: the test encrypts and writes a small payload, compares returned metadata with storage metadata, decrypts it back successfully, flips a ciphertext byte and expects decrypt failure, checks a missing blob returns `blob.ErrBlobNotFound`, injects a `PutBlob` fault and expects that error, then replaces the crypter encryptor with `failingEncryptor` and expects the encryption error.

State and persistence behavior: confirms successful writes create real storage objects and failed writes/encryption paths return errors instead of silent partial success.

Dependencies and integration: exercises `EncryptionManager.GetEncryptedBlob` and `EncryptAndWriteBlob`; indirectly relies on repository encryption/hash construction.

Risks and gaps: does not assert persistent cache behavior because the test uses a nil cache field, but it covers the core storage and cryptographic failure boundaries.
