# sources/test-tools/syzkaller/pkg/symbolizer/cache.go

## Purpose

`cache.go` contains support utilities for symbolization: a thread-safe per-PC cache and a string interner to reduce repeated allocation of function and file names.

## Important APIs, Types, And Functions

`Cache` stores a guarded map from `(bin, pc)` to frames/error. `Cache.Symbolize` checks the cache under an `RWMutex`, calls an `inner` symbolizer on miss, initializes the map if needed, stores both successful frames and errors, and returns the result. `Interner.Do` stores cloned strings in `sync.Map` and returns canonical copies.

## Control Flow, State, Dependencies, And Integration

Cache state persists in memory and is safe for normal concurrent map access. It does not coalesce concurrent cache misses, so two goroutines can symbolize the same key simultaneously before either stores. The interner uses `sync.Map`, but comments say it is not semantically thread-safe; production use in `addr2line` is single stream oriented. Integrates with symbolization consumers that need repeated PC lookup.

## Risks And Test Signals

Cached errors can make transient symbolizer failures sticky. Returned frame slices are not cloned, so callers could mutate cached data. `cache_test.go` verifies hits avoid repeated `inner` calls and that errors are cached per key.
