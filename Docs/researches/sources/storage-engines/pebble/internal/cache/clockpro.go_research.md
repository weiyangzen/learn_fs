# sources/storage-engines/pebble/internal/cache/clockpro.go

## Purpose
This file implements the per-shard CLOCK-Pro block cache algorithm. It stores blocks by `(handleID, fileNum, offset)`, keeps per-file linked lists for efficient whole-file eviction, maintains hot/cold/test lists with three clock hands, accounts cache hits/misses by level and category, and integrates read-miss de-duplication through `readShard`.

## Important APIs, Types, And Functions
`key` identifies cache blocks and computes shard indexes with Fibonacci hashing. `shard` owns counters, maps, hands, sizes, counts, reservation state, and a `readShard`. Public shard methods include `init`, `get`, `getWithReadEntry`, `set`, `delete`, `evictFile`, `Free`, `Reserve`, `Size`, and `targetSize`. Internal mutation helpers include `metaAdd`, `metaDel`, `metaCheck`, `metaEvict`, `evict`, `runHandCold`, `runHandHot`, and `runHandTest`.

## Control Flow
Reads acquire the shard read lock, find an entry in `blocks`, acquire its `Value`, and mark it referenced unless `peekOnly` is true. Misses increment counters and optionally obtain a `readEntry`. `set` either inserts a new cold entry, replaces a resident hot/cold entry, or promotes a test entry to hot while increasing `coldTarget`. Eviction runs `runHandCold` until resident hot+cold bytes fit the target, with hot and test hands adjusting classification and `coldTarget`.

## State And Persistence Behavior
All state is volatile. Resident values are reference counted and manually allocated elsewhere. `blocks` maps block keys to entries; `files` maps file keys to circular file-link lists; `entries` is only present when Go allocation needs GC visibility. `sizeHot`, `sizeCold`, `sizeTest` and count mirrors are correctness-critical and checked by invariant code.

## Dependencies And Integration Points
The shard is used by `Cache` and `Handle` in `cache.go`, `read_shard.go` for miss coordination, `entry.go` for linked-list nodes, `value.go` for reference-counted buffers, `block_map.go` for Swiss-map storage, and `metrics.go` for counter aggregation.

## Risks And Edge Cases
Important risks are corrupted circular lists, stale hands pointing at freed entries, negative size/count accounting, oversized entries, reservations exceeding maximum size, nil values in test entries, and expensive file eviction under a shard lock. `evictFileRun` deliberately evicts only a few entries per mutex acquisition to reduce latency. The TODO on cold-entry replacement notes an algorithmic ambiguity.

## Test Signals
`cache_test.go` checks behavior externally, `clockpro_test.go` covers `Reserve`/`coldTarget`, and invariant builds use `metaCheck` to find entries remaining in maps or lists after deletion. Hit/miss metrics are indirectly exercised by `Get`/`Peek`.
