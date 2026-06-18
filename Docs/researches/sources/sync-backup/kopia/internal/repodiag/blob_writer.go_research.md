# sources/sync-backup/kopia/internal/repodiag/blob_writer.go

Purpose: asynchronously encrypts and writes diagnostic blobs.

Important APIs/types/functions: `BlobWriter`, `EncryptAndWriteBlobAsync`, `Wait`, and `NewWriter`.

Control flow: `EncryptAndWriteBlobAsync` starts an errgroup task that encrypts gathered bytes through a crypter, writes them to blob storage under a prefix-derived ID, logs progress, and invokes a close callback. `Wait` joins all pending writes.

State and persistence behavior: diagnostic data is persisted as encrypted blobs in the target storage; pending goroutines are tracked by `errgroup`.

Dependencies and integration points: used by diagnostic log manager; depends on `blob.Storage`, `blobcrypto.Crypter`, `gather`, and logging.

Risks and test signals: callers must call `Wait` to surface asynchronous errors, and close callbacks must always run. Tests should validate encryption, blob IDs, callback invocation, and write error propagation.
