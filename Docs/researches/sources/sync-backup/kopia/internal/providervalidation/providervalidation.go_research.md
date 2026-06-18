# sources/sync-backup/kopia/internal/providervalidation/providervalidation.go

Purpose: validates a blob storage provider against Kopia assumptions for capacity reporting, missing-blob errors, conditional writes, listing, partial reads, metadata, clock drift, and concurrent access.

Important APIs/types/functions: `Options`, `DefaultOptions`, `ValidateProvider`, `equivalentBlobStorageConnections`, `openEquivalentStorageConnections`, `concurrencyTest`, worker methods, `cleanupAllBlobs`, and `verifyBlobCount`.

Control flow: unless `KOPIA_SKIP_PROVIDER_VALIDATION` is set, validation opens multiple equivalent storage connections, creates a unique temp prefix, checks capacity semantics, verifies empty/missing/list behavior, writes a large blob, probes `DoNotRecreate`, validates full and partial reads and metadata timestamp drift, then runs concurrent put/get/metadata workers until a deadline.

State and persistence behavior: temporary blobs are written to the target storage and removed with deferred cleanup. Concurrency state tracks generated blob IDs, seeds, and write completion under a mutex.

Dependencies and integration points: used during repository/storage setup; integrates `blob.Storage`, `gather`, logging wrappers, fake clock, and UUID temp prefixes.

Risks and test signals: the list worker is a TODO, random lengths can be zero and generated ID needs at least 16 bytes of data, and validation can be expensive. Tests should use map storage and short durations to verify basic pass/fail behavior.
