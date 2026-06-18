## sources/user-network-fs/gcsfuse/internal/gcsx/multi_range_downloader_wrapper.go

Purpose: wraps a single `gcs.MultiRangeDownloader` with lazy creation, read helper logic, refcounting, optional LRU caching, handle reuse, and eviction cleanup.

Important APIs/types/functions: `NewMultiRangeDownloaderWrapper`, `readResult`, `MultiRangeDownloaderWrapper`, `SetMinObject`, `wrapperKey`, `GetMinObject`, `GetRefCount`, `IncrementRefCount`, `DecrementRefCount`, `CloseMRDForEviction`, `ensureMultiRangeDownloader`, `Read`, `closeLocked`, and `Size`.

Control flow: construction requires non-nil object. Refcount increment removes an inactive wrapper from cache. Decrement inserts into cache at zero and closes evicted wrappers outside the current lock. `ensureMultiRangeDownloader` handles nil/unusable/forced recreation by temporarily upgrading from read lock to write lock, using existing or cached handles unless force recreation is requested, and mapping `NotFoundError` to `FileClobberedError`. `Read` creates/reuses MRD, caps end offset to buffer length, issues `Add`, waits for callback or context depending on `IgnoreInterrupts`, wraps non-EOF errors, and captures metrics.

State/persistence behavior: stores object/bucket/config, wrapped downloader, cached read handle, refcount, and LRU cache pointer. No local data persistence; remote read handle is preserved on close for future recreation.

Dependencies/integration: GCS MRD APIs, LRU cache, config, tracing propagation, monitor metrics, logger, and file-clobbered error type. It supports client-side multi-range reader flows distinct from pooled `MrdInstance`.

Risks/test signals: the callback channel is closed via a mutex to avoid sends after cancellation, but complexity is high. Refcount misuse returns errors. Cache eviction race protection checks refcount and cache membership. Tests cover parallel refcounts, reads, cancellation modes, EOF/error wrapping, recreation, file clobber, cache reuse/eviction/races, and disabled cache behavior.
