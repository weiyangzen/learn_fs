## sources/user-network-fs/gcsfuse/internal/gcsx/multi_range_downloader_wrapper_test.go

Purpose: comprehensive tests for `MultiRangeDownloaderWrapper` read behavior, downloader creation/recreation, refcounting, and LRU cache lifecycle.

Important APIs and fixtures: `mrdWrapperTest`, `mrdWrapperCacheTest`, mock bucket, fake multi-range downloaders with sleeps/errors, generated object data, and cache capacity variants.

Control flow and behavior covered: parallel refcount increments/decrements, invalid decrement, successful reads, MRD creation errors, short reads, cancellation with interrupts enabled versus disabled, EOF passthrough, non-EOF error wrapping, constructor validation, `SetMinObject`, ensure behavior for missing fields, reusable existing MRD, unusable existing MRD recreation, force recreation, file-clobbered conversion, cache add/remove, cache eviction on overflow, deleted-if-reopened behavior, concurrent add/remove, disabled cache, eviction/repool races, and multiple evictions.

State/persistence signals: tests inspect refcount, `Wrapped`, cached handle reuse, LRU membership, cache size, and whether MRDs remain open or are closed after eviction. They validate that cached wrappers are removed on reopen and that inactive evicted wrappers close safely.

Dependencies/integration: uses storage mock bucket, fake MRDs, LRU cache, config with `IgnoreInterrupts`, `testify/suite`, and request matching.

Risks/test signals: strong local concurrency and lifecycle coverage. Real network callback timing and production tracing are not validated, but fake downloader sleep/error modes exercise the key asynchronous paths.
