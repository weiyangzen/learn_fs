# sources/storage-engines/pebble/internal/genericcache/shard.go

## Purpose
`shard.go` implements the cache’s per-shard CLOCK-Pro algorithm, concurrency control, initialization synchronization, eviction, and asynchronous release loop.

## Important APIs, Types, And Functions
`shard` holds hit/miss counters, capacity, locked node map and CLOCK hands, release channel/waitgroup, and init/release callbacks. Key methods include `Init`, `releaseLoop`, `UnrefValue`, `findOrCreateValue`, `addNode`, `evictNodes`, `runHandCold`, `runHandHot`, `runHandTest`, `Evict`, `EvictAll`, `forAllNodesLocked`, and `Close`.

## Control Flow
`findOrCreateValue` uses a read-lock fast path for initialized or initializing hits, waits with context cancellation if needed, and falls back to a write-lock miss path. New misses create cold nodes or resurrect test nodes as hot, create a `value` with two references, unlock, and call `initValueFn`. Failed initialization unlinks and clears the node. CLOCK hands demote hot entries, clear cold unreferenced entries into test ghosts, and prune excess test entries. Release runs asynchronously once refcount reaches zero, waiting for initialization first.

## State And Persistence Behavior
Shard state is in-memory. Live values are held by shard and caller references; ghost test nodes retain keys but no value. `Close` drains nodes, closes the release channel, and waits for all pending releases.

## Dependencies And Integration Points
It depends on `context`, `sync`, `atomic`, `errors`, and `invariants`. It backs all public `Cache` operations.

## Risks And Edge Cases
Outstanding references during `Evict` or `Close` panic. Initialization errors must close `initialized`; waiters rely on that channel. Context-canceled waiters receive synthetic initialized error values and unref the shared value. `EvictAll` requires no matching keys be inserted concurrently and checks that in invariant builds.

## Test Signals
`cache_test.go` directly stresses initialization, concurrent waiters, explicit eviction, close, and policy hit/miss behavior. Race testing is valuable because locks, atomics, and release goroutines interact closely.
