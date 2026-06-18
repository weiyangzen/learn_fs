# sources/storage-engines/tikv/components/tikv_util/src/lru.rs

## Purpose
Implements a generic LRU cache with pluggable size accounting and eviction policy, optimized around a hash map plus intrusive linked recency trace.

## Important APIs, Types, And Functions
Internal `Record<K>` nodes hold prev/next pointers and a key. `ValueEntry<K, V>` stores a value and pointer to its recency record. `Trace<K>` owns head/tail sentinel nodes, a sampling tick, and methods for create, promote, maybe-promote, delete, tail reuse, clear, remove-tail, and tail lookup.

`SizePolicy<K, V>` abstracts cache size accounting; `CountTracker` counts entries. `GetTailEntry` lets eviction policies inspect the least-recent entry lazily. `EvictPolicy<K, V>` decides whether to evict; `EvictOnFull` evicts when current size exceeds capacity.

`LruCache<K, V, T, E>` exposes constructors, `size`, `clear`, `capacity`, `internal_allocated_capacity`, `insert`, `insert_if_not_exist`, `remove`, `get`, `get_no_promote`, `contains_key`, `get_mut`, `iter`, `len`, `is_empty`, and `resize`.

## Control Flow
The trace list is newest at the head and oldest at the tail. Insertion of a new key either creates a new record or, if the eviction policy says the post-insert size should evict, reuses the tail record for the new key and removes the old key from the map. Existing-key insertions optionally replace the value and promote the record. After insertion, `evict_until_fit` repeatedly removes tail entries until the policy accepts the current size or the map is empty.

`get` and `get_mut` call `maybe_promote`, which promotes only when `tick & sample_mask == 0`, allowing sampled recency updates. `get_no_promote` and `contains_key` avoid recency mutation. `resize` clamps zero to one, evicts oldest entries when shrinking, and shrinks the map allocation after removals.

## State And Persistence
All state is in-memory: the map, linked-list nodes allocated with `Box::leak`, size policy counters, capacity, eviction policy, and sampling tick. `Drop` calls `clear`, and `Trace::drop` frees sentinel nodes.

## Dependencies And Integration
Depends on TiKV `collections::{HashMap, HashMapEntry}`, `std::ptr`, `NonNull`, and `MaybeUninit`. It integrates with caches that need custom size policies or eviction behavior, such as transaction-status style caches referenced by comments.

## Risks
The trace is unsafe and manually manages allocation, key initialization, pointer links, and drops. Any map/list divergence would cause memory unsafety or panics. `sample_mask` changes LRU precision; nonzero masks deliberately skip many promotions. Oversized entries can cause the cache to evict everything because `SizePolicy` cannot precompute a candidate's size before insertion. The cache is `Send` when its components are `Send`, but it is not internally synchronized.

## Test Signals
Tests cover insertion replacement and eviction order, query promotion, zero-capacity clamping, removal, resize shrink/grow behavior, sampled promotion, clear/reuse, custom size tracking, oversized value handling, no-promote lookup behavior, and insert-if-absent semantics.
