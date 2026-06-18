# sources/sync-backup/restic/internal/backend/cache/backend.go

Purpose: Provides a backend wrapper that transparently caches selected files locally while delegating storage operations to an underlying backend.

Important APIs and types: `cacheBackend` embeds `backend.Backend` and `*Cache`, tracks `inProgress` downloads, and logs cache-cleanup errors. Key methods are `newBackend`, `Remove`, `Save`, `Load`, `Stat`, `List`, `Unwrap`, `Warmup`, and `WarmupWait`. `autoCacheTypes` selects index files, snapshot files, and metadata pack files.

Control flow and state: `Save` stores cacheable files in the backend first, rewinds, then saves them in cache. `Load` waits for any existing download, tries cache load, falls back directly for non-cacheable types, otherwise downloads the complete file once through `cacheFile`, then serves the requested range from cache. `cacheFile` uses a handle-to-channel map so concurrent callers share one download. `List` records backend IDs and clears stale cache entries after successful listing.

Persistence and dependencies: Persistent state lives in `Cache` files. Runtime state includes `inProgress` synchronization and forgotten cache entries in `Cache`. Dependencies include `backend`, `io`, `sync`, and `debug`.

Integration points: `Cache.Wrap` returns this wrapper. It is commonly layered with retry and remote backends; `Unwrap` supports `backend.AsBackend`.

Risks and test signals: Risks include serving stale cached data unless callers use `Forget`, deadlocks if in-progress channels are not closed, cache poisoning after failed downloads, out-of-bounds range behavior, and cache pruning errors. `backend_test.go` covers normal load/save/remove/stat, concurrent load errors, range errors, forget circuit breaker, and automatic clearing.
