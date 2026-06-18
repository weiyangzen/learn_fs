<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/cache_impl.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/cache_impl.rs

## Purpose
Implements the internal lockable LRU cache used by `LockingBlockStore` to serialize per-block operations, buffer dirty data, and prune/flush cached blocks.

## APIs, Flow, And State
`BlockCacheImpl<B>` owns an optional `Arc<LockableLruCache<BlockId, BlockCacheEntry<B>>>` and an eventually consistent `AtomicU64` count of blocks present only in cache. `async_lock` acquires an owned lock with a soft entry limit of 10,240 and invokes an async eviction callback. `set_entry`, `set_or_overwrite_entry_even_if_dirty`, delete helpers, and `flush_entry` maintain dirty/base-store state and the not-yet-in-base counter. `into_entries_unordered` waits until all other cache references are gone, then consumes the LRU entries.

## Dependencies And Integration
Built on the `lockable` crate, Tokio yielding, `Arc`, atomics, and `BlockCacheEntry`. `BlockCache` wraps it with periodic pruning and async-drop orchestration; `LockingBlockStore` uses it as both cache and per-ID mutex table.

## Risks And Test Signals
The file contains deliberate assertions to catch counter underflow, deleting unset entries, setting over existing entries, and dirty drop mistakes. Busy-wait loops on `Arc::strong_count` can deadlock if a current task holds a guard while waiting on drop. The counter is explicitly eventually consistent during concurrent mutations, so exact counts are reliable only at quiescent points.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/cache_impl.rs -->
