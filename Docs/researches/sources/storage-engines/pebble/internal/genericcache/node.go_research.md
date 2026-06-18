# sources/storage-engines/pebble/internal/genericcache/node.go

## Purpose
`node.go` defines the internal linked-list node and value holder used by the generic CLOCK-Pro cache.

## Important APIs, Types, And Functions
`node[K,V]` stores a key, optional `*value[V]`, intrusive `next`/`prev` links, `status`, and an atomic `referenced` bit. `nodeStatus` has `test`, `cold`, and `hot` states with a `String` method. `next`, `prev`, `link`, and `unlink` manage circular list links. `value[V]` stores initialized value/error, an `initialized` channel, and an atomic refcount.

## Control Flow
Nodes move among test/cold/hot states under shard locks. `link` inserts a node before a sentinel/current node; `unlink` removes it and self-links it. Values are published by closing `initialized`, allowing concurrent waiters and the release loop to synchronize.

## State And Persistence Behavior
All state is in-memory. Test nodes may retain keys without values as CLOCK-Pro ghost entries. Values remain alive while their refcount is nonzero and are released when evicted and unreferenced.

## Dependencies And Integration Points
This file is consumed by `shard.go` and measured by `cache.go` metrics. It depends only on `sync/atomic`.

## Risks And Edge Cases
Intrusive circular-list manipulation assumes callers maintain non-nil links and shard locking. A node’s `value` can be nil for test entries, so callers must distinguish cache ghosts from live objects. The `initialized` channel is essential; release before initialization would otherwise race.

## Test Signals
Node behavior is tested indirectly through cache policy, eviction, release, and error/cancellation tests.
