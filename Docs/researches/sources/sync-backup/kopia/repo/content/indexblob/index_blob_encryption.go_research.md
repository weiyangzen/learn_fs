# sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption.go_research.md`.

Purpose: handles encryption, decryption, caching, metadata logging, and storage writes for index blobs.

Important APIs and types: `Metadata` extends `blob.Metadata` with superseded blobs and implements structured log writing. `EncryptionManager` owns blob storage, a `blobcrypto.Crypter`, an optional persistent cache, and logger. `GetEncryptedBlob` cache-loads encrypted bytes from storage, then decrypts into an output buffer. `EncryptAndWriteBlob` encrypts index data, derives a blob ID with prefix and suffix, writes it to storage, logs metadata, and returns `blob.Metadata`. `NewEncryptionManager` constructs the manager.

Control flow: reads go through `indexBlobCache.GetOrLoad` before decryption; writes encrypt into a temporary gather buffer, call `blob.PutBlobAndGetMetadata`, and log latency and write size. Errors are wrapped but preserve root causes for storage/encryption failures.

State and persistence behavior: encrypted index blobs are durable repository objects named by encrypted content hash plus optional session suffix. The cache stores encrypted payloads, not decrypted index contents.

Dependencies: `blobcrypto`, cache, gather, content logging, blob storage, and timing helpers.

Risks and tests: corrupted encrypted data must fail decrypt, cache misses must propagate blob-not-found, and write/encrypt failures must not report metadata. `index_blob_encryption_test.go` covers successful round trip, corruption, missing blob, put failure, and encryption failure.
