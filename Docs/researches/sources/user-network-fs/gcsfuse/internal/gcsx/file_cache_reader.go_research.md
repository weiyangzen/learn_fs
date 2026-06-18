## sources/user-network-fs/gcsfuse/internal/gcsx/file_cache_reader.go

Purpose: implements `FileCacheReader`, a first-layer `Reader` that attempts to satisfy GCS object reads from the local file cache and signals `FallbackToAnotherReader` when GCS should be used.

Important APIs/types/functions: `NewFileCacheReader`, `ReaderName`, `tryReadingFromFileCache`, `ReadAt`, `captureFileCacheMetrics`, `Destroy`, and `CheckInvariants`. State includes the target `MinObject`, `Bucket`, optional `file.CacheHandler`, `cacheFileForRangeRead`, a mutex-protected `file.CacheHandle`, metrics/tracing handles, and FUSE handle ID.

Control flow: `ReadAt` immediately returns EOF for offsets at or beyond object size, then calls `tryReadingFromFileCache`. Cache reads return success when there is a cache hit, a full buffer, or a partial read exactly at object EOF. Otherwise it returns `FallbackToAnotherReader`. `tryReadingFromFileCache` lazily creates a cache handle, handles expected cache misses and exclusions as non-errors, reads through the handle, resets invalid handles, and wraps unexpected cache errors.

State/persistence behavior: it maintains an open cache handle across reads and closes/nils it on invalidation or destroy. The cache handler may start or reuse local download jobs; a read can be write-through where data is fetched from GCS and served from local cache with `cacheHit=false`.

Dependencies/integration: integrates with cache handler/job/lru utilities, metrics, tracing, logger, UUID request logging, and FUSE handle IDs. It relies on cache utility sentinel errors to distinguish fallback from fatal cache failures.

Risks/test signals: concurrency safety depends on correct lock handoff around handle creation and reads. Request offsets below zero are not explicitly rejected here and rely on lower cache layers. Tests cover disabled cache, file-size exclusion, EOF, cache hits/misses, invalid jobs/handles, deleted files, unfinalized objects, destroy races, and concurrent reads.
