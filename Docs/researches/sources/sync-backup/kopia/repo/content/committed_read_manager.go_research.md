# sources/sync-backup/kopia/repo/content/committed_read_manager.go

Purpose: builds and manages the shared read side of Kopia content storage: committed index loading, content and metadata caches, index blob managers, local pack-index recovery, decryption/decompression, epoch support, and repository diagnostics.

Important APIs/types/functions: `SharedManager`, `IndexBlobReader`, constants for cache sweep ages and index refresh, `LoadIndexBlob`, `IndexReaderV0`, `IndexReaderV1`, `readPackFileLocalIndex`, `loadPackIndexesLocked`, `indexBlobManager`, `decryptContentAndVerify`, `IndexBlobs`, cache construction helpers, `setupCachesAndIndexManagers`, `EpochManager`, `CloseShared`, `shouldRefreshIndexes`, `PrepareUpgradeToIndexBlobManagerV1`, and `NewSharedManager`.

Control flow: construction clones/defaults options, initializes caches and V0/V1 index managers, then loads active pack indexes under `indexesLock`. Index loading chooses V0 or V1 manager based on mutable epoch parameters, retries on missing blobs with cache flush and backoff, fetches missing encrypted index blobs into the committed index cache, swaps active indexes, sets refresh deadline, and warns on too many index blobs. Content reads decrypt using content ID-derived IV, verify format encryption, and decompress when `CompressionHeaderID` is set.

State and persistence behavior: owns persistent caches under `CachingOptions.CacheDirectory` for contents, metadata, list/own-writes backing stores, and index blobs; committed index state is memory plus optional disk `.sndx` cache. It tracks refresh deadline, statistics, metrics, and diagnostic loggers. Close releases index/cache resources, flushes epoch manager, and syncs logs.

Dependencies/integration: central integration point for blob storage, filesystem cache storage, sharded cache layout, listcache, ownwrites, persistent cache protection, indexblob managers, epoch manager, format/encryption/hashing, compression registry, repodiag logging, and content stats/metrics.

Risks and edge cases: cache setup order is important because index blob managers depend on wrapped cached storage. Local pack-index recovery first reads only the postamble tail and falls back to full blob. Permissive cache loading skips bad index blobs. V1 epoch setup passes a callback that calls `sm.indexBlobManagerV1`, so initialization order must remain valid. Closing assumes all cache/index manager fields were initialized.

Test signals: content formatter and broader content-manager tests exercise end-to-end write/read, encryption/decompression, flushing, and cache paths; index cache tests cover committed index cache pieces. Direct tests should cover refresh retry behavior, V0/V1 selection, local-index recovery fallback, and close ordering.
