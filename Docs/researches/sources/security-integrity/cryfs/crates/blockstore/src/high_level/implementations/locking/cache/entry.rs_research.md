<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/entry.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/entry.rs

## Purpose
Defines the cache entry value stored for each locked/cached block and the state enums used to track dirtiness and base-store presence.

## APIs, Flow, And State
`CacheEntryState` is `Dirty` or `Clean`; `BlockBaseStoreState` records whether the block exists in the base store. `BlockCacheEntry<B>` holds the base store guard, dirty flag, `Data`, and base-store state. `data_mut` and `resize` mark the entry dirty. `_flush_to_base_store` writes dirty data to the base store, marks it clean, updates base-store state, and returns a `FlushResult`. `discard` marks dirty data clean so intentional deletion can drop it without panic.

## Dependencies And Integration
Entries are owned by `BlockCacheImpl` and exposed through `BlockCacheEntryGuard` and `LockingBlock`. They call low-level `store` on the base store and use `safe_panic!` in `Drop`.

## Risks And Test Signals
Dropping a dirty entry panics, which is an important safety net but makes correct flush/discard paths critical. `_flush_to_base_store` does not update `BlockCacheImpl`'s counter by itself; callers must use `flush_entry` unless the cache is already being destroyed.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/entry.rs -->
