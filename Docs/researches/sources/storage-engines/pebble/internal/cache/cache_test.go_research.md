# sources/storage-engines/pebble/internal/cache/cache_test.go

## Purpose
This file tests Pebble's sharded block cache through the public `Cache` and `Handle` APIs. It validates CLOCK-Pro behavior against reference data, file/handle namespacing, explicit deletion and file eviction, reservation accounting, zero-sized cache behavior, concurrent replacement of existing keys, and lookup benchmark behavior.

## Important APIs, Types, And Functions
`TestCache` replays `testdata/cache` and compares expected hit/miss decisions. `setTestValue` allocates `Value`s, copies bytes, inserts with `Handle.Set`, and releases the caller ref. Other tests exercise `Peek`, `Get`, `Delete`, `EvictFile`, `NewHandle`, `Reserve`, `Size`, and `Unref`. `BenchmarkCacheGet` fills a large cache and runs parallel randomized `Get`s across levels and categories.

## Control Flow
Tests create one-shard or multi-shard caches, install small values, then force eviction or namespace separation. `TestCachePeek` first warms half the entries through `Get`, peeks the other half, inserts more data, and expects the `Get`-touched entries to survive. `TestReserve` shrinks effective capacity with a release callback, checks evictions, releases the reservation, and checks future insertions.

## State And Persistence Behavior
The tests cover in-memory cache state only. They assert size counters, per-handle key namespaces, and that caller references are released after cache insertion. No persistent files are written except the static reference trace read from `testdata/cache`.

## Dependencies And Integration Points
The suite uses `base.DiskFileNum`, `base.Level`, cache `Category` metrics categories, `require`, and Go concurrency primitives. It indirectly validates `clockpro.go`, `entry.go`, `value.go`, and reference-counting implementations.

## Risks And Edge Cases
Key risks are reference leaks, accidental access-bit updates from `Peek`, deletion of missing keys, eviction across handles, reservation double-release, zero target size, and races replacing an existing key. The stress test is intentionally narrow: it targets concurrent `Set` on existing entries, not all concurrent eviction/read paths.

## Test Signals
Strong signals are exact hit/miss trace conformance, expected `Size()` values after mutation, preserved h2 data after h1 file eviction, a panic string for double reservation release, and no race/panic during repeated concurrent replacement.
