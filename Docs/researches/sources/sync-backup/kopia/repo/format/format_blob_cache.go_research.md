# sources/sync-backup/kopia/repo/format/format_blob_cache.go

## Purpose
Implements small caches for root repository format blobs, supporting null, in-memory, and on-disk modes.

## Important APIs, Types, And Functions
`DefaultRepositoryBlobCacheDuration` is 15 minutes. `blobCache` defines `Get`, `Put`, and `Remove`. Implementations are `nullCache`, `inMemoryCache`, and `onDiskCache`. Constructors are `NewDiskCache`, `NewMemoryBlobCache`, and `NewFormatBlobCache`.

## Control Flow
`nullCache` never returns stored data. `inMemoryCache` stores byte slices and modification times under a mutex. `onDiskCache` maps blob IDs to files under a cache directory, reads file contents and mtimes, writes atomically, creates the directory and cache marker on first write if needed, and removes selected files on invalidation. `NewFormatBlobCache` selects disk cache when `cacheDir` is non-empty, memory cache when valid duration is positive, else null cache.

## State And Persistence
Memory cache state is process-local maps. Disk cache state is files named after blob IDs in the cache directory.

## Dependencies And Integration Points
Depends on `atomicfile`, `cache`, `cachedir`, `clock`, and logging. `format.Manager` uses this cache to avoid frequent `kopia.repository` and `kopia.blobcfg` reads.

## Risks And Edge Cases
Disk cache trusts file names derived from blob IDs. Cached byte slices from memory are returned as stored, so callers should not mutate them. Cache validity is enforced by `Manager`, not by cache implementations themselves.

## Test Signals
`format_blob_cache_test.go` covers null, disk existing, disk missing-directory, and memory caches for get/put/overwrite/remove behavior and disk file cleanup.
