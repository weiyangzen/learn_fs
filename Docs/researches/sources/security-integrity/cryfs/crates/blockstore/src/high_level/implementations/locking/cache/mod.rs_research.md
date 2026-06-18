<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/mod.rs

## Purpose
Provides the public cache wrapper used by `LockingBlockStore`, including periodic pruning, test pruning hooks, block locking, flushing, and async-drop flushing.

## APIs, Flow, And State
`BlockCache<B>` owns a `BlockCacheImpl` and a `PeriodicTask` that prunes entries every 500 ms if they have been unlocked for at least 500 ms. `async_lock` acquires a cache entry and wires eviction to `_prune_blocks`. Test/testutils hooks `prune_unloaded_blocks` and `prune_all_blocks` force cache cleanup. `_prune_block` flushes dirty entries and deletes them. `async_drop_impl` stops the prune task and drains/flushed all remaining entries concurrently.

## Dependencies And Integration
Wraps `BlockCacheImpl`, `BlockCacheEntry`, `BlockCacheEntryGuard`, `PeriodicTask`, `futures::join`, and `cryfs_utils::stream::for_each_unordered`. It is the persistence bridge between high-level dirty block handles and the low-level base store.

## Risks And Test Signals
Comments identify potential deadlocks from arbitrary lock ordering and busy waiting for `Arc` references to disappear. Dirty data persistence relies on async-drop being called; intentional deletion must use discard/delete helpers. Generic high-level blockstore tests exercise normal cache behavior with and without forced flush, but several TODOs request more direct prune tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/mod.rs -->
