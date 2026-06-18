# sources/storage-engines/pebble/internal/genericcache/cache.go

## Purpose
`cache.go` provides the public API for a generic sharded CLOCK-Pro cache with reference-counted values initialized on demand and released on eviction.

## Important APIs, Types, And Functions
`Cache[K,V,InitOpts]` owns shards. `Key` requires comparability and `Shard(numShards) int`. `InitValueFn` initializes a value and receives its `ValueRef`; `ReleaseValueFn` releases a value. `New`, `Init`, `Close`, `FindOrCreate`, `Evict`, `EvictAll`, and `Metrics` are the public methods. `ValueRef` exposes `Value` and `Unref`. `Metrics` reports size, count, hits, and misses.

## Control Flow
`Init` divides capacity across shards and starts each shard’s release loop. `FindOrCreate` routes by key shard, asks the shard for a value, converts initialization errors into returned errors, and returns a reference that callers must unref. `Evict` and `EvictAll` delegate to shards. `Close` closes every shard and requires no outstanding references.

## State And Persistence Behavior
The cache is fully in-memory. Values persist until evicted and no references remain. Metrics are approximate byte accounting based on `unsafe.Sizeof` for metadata and stored `value[V]` objects; caller-owned pointees are not included.

## Dependencies And Integration Points
It depends on `context`, `unsafe`, `errors`, and `invariants`. Integration points are internal Pebble components needing typed caches without duplicating CLOCK-Pro logic.

## Risks And Edge Cases
The caller must always call `Unref`; leaks prevent release. `Evict`, `EvictAll`, and `Close` panic if references remain. `Key.Shard` must return a valid shard index or the cache will panic. Initialization may run concurrently for the same key if eviction races with creation.

## Test Signals
`cache_test.go` covers basic creation, CLOCK-Pro hit/miss behavior, eviction release, outstanding-reference panics, initialization errors, and context cancellation while waiting on another initializer.
