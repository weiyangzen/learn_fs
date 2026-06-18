# sources/user-network-fs/rclone/backend/cache/cache_internal_test.go

## Purpose
This is the cache backend's internal integration test harness. It exercises cache behavior against either a configured remote, a cache remote wrapped by crypt, or an auto-created local remote. The tests focus on object discovery, stale metadata, wrapped-remote changes, chunk caching, directory notification, and helper behavior used by upload tests.

## Important APIs, Types, And Control Flow
`TestMain` parses `-remote-internal` and `-upload-dir-internal`, creates a global `runInstance`, and runs the package tests. The `run` helper owns temp upload paths, cache DB/chunk paths, crypt state, and backend-type detection. `newCacheFs` builds the configured cache filesystem, optionally synthesizes a local wrapped remote, configures crypt credentials when needed, opens the shared `cache.Persistent`, purges temp uploads, instantiates `cache.NewFs`, and registers cleanup. Helper methods write, update, list, read ranges, move, copy, remove, wait for background upload events, retry eventually consistent checks, and unwrap `*cache.Fs`.

## State And Persistence
The tests mutate real rclone config entries for synthesized local remotes, temporary upload directories, cache DB files under `config.GetCacheDir()/cache-backend`, persistent chunk files, and possibly VFS cache paths. They rely on cleanup through `operations.Purge`, `StopBackgroundRunners`, temp-file closure/removal, and `debug.FreeOSMemory`. Crypt fixtures include deterministic encrypted-name mappings and encrypted payload byte strings so tests can validate wrapped crypt behavior.

## Dependencies And Integration Points
The file integrates `backend/cache`, `backend/crypt`, `backend/local`, optional drive import, `fs/config`, `operations`, `fstest`, `object.NewStaticObjectInfo`, and `vfscommon`. It is intentionally built with `!plan9 && !js && !race`, reflecting timing and background-worker sensitivity. Several tests skip or retry when the wrapped remote is external or crypt-backed.

## Risks And Test Signals
The tests cover stale cache invalidation, cache read correctness across chunk boundaries, double updates, direct wrapped-FS mutation visibility, change notifications creating missing parent buckets, cache-write chunk timestamps, chunk-total-size cleanup preserving recent chunks, expired listings, and bug 2117 nested directory listings. Risks include long sleeps, global mutable `runInstance`, real config mutation, external remote eventual consistency, crypt fixture drift, and race-build exclusion.
