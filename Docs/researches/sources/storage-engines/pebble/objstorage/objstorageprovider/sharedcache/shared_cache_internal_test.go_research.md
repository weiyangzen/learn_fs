# sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_internal_test.go

Purpose: This file unit-tests the shared cache shard's intrusive list primitives: the LRU doubly linked circular list and free singly linked list.

Important tests: `TestSharedCacheLruList` initializes a shard with 100 block states, then inserts and unlinks block indexes while checking list order and backlink correctness. `TestSharedCacheFreeList` pushes and pops indexes, asserting LIFO order and empty-list state.

Control flow and state: Both tests construct only a `shard` with `mu.blocks`; no cache files, worker goroutines, or remote reads are involved. Local `expect` closures walk list pointers and compare against expected integer slices.

Dependencies and integration: These primitives are used by `shard.set` when allocating or evicting blocks and by `shard.get` when moving accessed blocks to the front. Correctness is essential because corrupt list state can break eviction, leak blocks, or panic under invariants.

Risks and test signals: These tests catch pointer update regressions in simple cases, including removing head, tail, and sole LRU entry. They do not cover concurrent access or interactions with `whereMap` and locks; those are partly covered by randomized shared cache tests and invariant consistency checks.
