# sources/user-network-fs/blobfuse2/component/entry_cache/entry_cache.go

## Purpose

`entry_cache.go` implements a read-only directory listing cache for `StreamDir` results. It stores paged directory entries keyed by path and continuation token, with TLRU expiration.

## Important APIs, Types, and Functions

`EntryCache` embeds `internal.BaseComponent` and holds `cacheTimeout`, `pathLocks`, `pathLRU`, and `pathMap`. `pathCacheItem` stores children and next token. Public component methods include `Name`, `SetName`, `SetNextComponent`, `Start`, `Stop`, `Configure`, and `StreamDir`; internal helpers include `pathEvict`, `NewEntryCacheComponent`, and package `init`.

## Control Flow

`Configure` requires global `read-only` to be true, loads `entry_cache.timeout-sec`, constructs a TLRU with capacity 1000 and the configured timeout, and initializes path locks. `Start` starts the TLRU worker, and `Stop` stops it. `StreamDir` builds a key as `name##token`, locks that key, returns cached children if present, otherwise calls `NextComponent().StreamDir`, stores non-empty successful results, and adds the key to the TLRU. `pathEvict` locks the same key and deletes the map entry when TLRU expires it.

## State and Persistence Behavior

Cached entries live in `sync.Map`; expiration state lives in the external `tlru.TLRU`. Per-key locks prevent duplicate fetch/store/evict races for the same path token. No filesystem persistence is used.

## Dependencies and Integration Points

The component depends on Blobfuse `common.LockMap`, `config`, `log`, `internal`, and `github.com/vibhansa-msft/tlru`. It sits in the component pipeline above storage components and only intercepts `StreamDir`.

## Risks and Edge Cases

It only caches non-empty successful listings, so empty directories and errors are never cached. Cache invalidation is purely timeout-based and requires read-only mode, so using it in mutable mounts is rejected. Key construction with `##` is simple but assumes path/token combinations cannot collide semantically.

## Test Signals

`entry_cache_test.go` verifies read-only configuration through loopback, non-caching of empty/error listings, cache hits that hide newly created files until expiration, and TLRU eviction.
