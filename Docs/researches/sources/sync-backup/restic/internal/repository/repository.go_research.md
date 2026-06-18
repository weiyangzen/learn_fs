
# sources/sync-backup/restic/internal/repository/repository.go

Purpose: central repository implementation for backend access, encryption, compression, pack upload, index loading, blob save/load, config/key integration, and streaming pack reads.

Key types are `Repository`, `internalRepository`, `Options`, `CompressionMode`, `blobSaverRepo`, `associatedBlobSet`, `byteReader`, and `packBlobIterator`. Important APIs include `New`, `UseCache`, `LoadUnpacked`, `LoadBlob`, `SaveUnpacked`, `WithBlobUploader`, `flush`, `LoadIndex`, `createIndexFromPacks`, `SearchKey`, `Init`, `List`, `ListPackHandles`, `saveBlob`, `SaveBlobAsync`, `LoadBlobsFromPack`, and `ZeroChunk`.

Control flow for saving blobs computes or accepts plaintext IDs, reserves pending index entries to suppress duplicates, compresses in repo v2, encrypts and verifies ciphertext, then queues into data/tree packer managers. `WithBlobUploader` coordinates async blob saving, pack uploader workers, final flush, and index flush. Load paths prefer cached packs, retry after cache eviction on failures, decrypt/decompress, and verify hashes. Multi-blob pack streaming coalesces nearby ranges, skips large gaps, detects overlaps, and falls back to `LoadBlob` for corrupted ranges when possible.

State and persistence include backend config/key/index/pack files, in-memory master index, cache wrapping, zstd encoder/decoder singletons, pending blob entries, temp pack files, and async goroutines. Risks include duplicate suppression correctness, context cancellation, compression compatibility with repo versions, cache invalidation, pack range math, and index/backend consistency. Extensive repository tests cover save/load, cache retry, incremental indexes, async saves, verification, streaming, and initialization safeguards.
