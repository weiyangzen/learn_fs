# sources/object-store/minio/cmd/metacache-manager.go

## Purpose

`metacache-manager.go` coordinates local bucket metacaches for a peer. It lazily creates per-bucket managers, periodically cleans caches, preserves recently deleted cache entries in a trash map, and exposes update/state-check helpers used by peer listing RPCs.

## Important APIs, Control Flow, And State

`localMetacacheMgr` is the process-local manager with `buckets` and `trash` maps. `metacacheManager` protects those maps with a mutex and starts background maintenance once through `init`. `initManager` waits for the object layer to become available, then ticks once per minute until `GlobalContext` closes. Each tick runs `cleanup` on live bucket caches and deletes trashed metacaches whose `lastUpdate` exceeds `metacacheMaxRunningAge`.

`updateCacheEntry` returns a trashed entry unchanged if the ID is in trash, otherwise delegates to the bucket metacache or returns `errVolumeNotFound`. `getBucket` ensures maintenance is started, returns a cached bucket if present, or creates a new bucket metacache with cleanup enabled and stores it. `deleteBucketCache` removes a bucket from the manager, deletes old cache data immediately, and moves recently updated caches into `trash` as `scanStateError` with `"Bucket deleted"`. `deleteAll` deletes and removes all buckets. `listPathOptions.checkMetacacheState` asks a peer for a listing, treats missing/none as `errFileNotFound`, marks stale running/success states as timeout errors on the peer, and reports cached async errors.

State is in memory plus on-disk cache cleanup via bucket metacache operations.

## Risks And Test Signals

Risks include background goroutine lifetime, lock ordering while bucket cleanup may be expensive, stale trash entries masking new updates by ID, and timeout heuristics marking a slow listing as failed. No direct tests in this subset cover the manager; behavior is exercised through listing and peer metacache paths.
