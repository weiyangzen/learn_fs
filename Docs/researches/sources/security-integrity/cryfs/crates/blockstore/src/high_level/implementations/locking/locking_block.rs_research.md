<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_block.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_block.rs

## Purpose
Defines `LockingBlock`, the loaded high-level block handle returned by `LockingBlockStore`.

## APIs, Flow, And State
`LockingBlock<B>` owns a `BlockCacheEntryGuard<B>`, so holding the block also holds the per-block cache lock. The `Block` implementation returns the guarded `BlockId`, data reference, mutable data reference, and async resize. Mutable data access and resize delegate to `BlockCacheEntry`, marking entries dirty.

## Dependencies And Integration
Used as `LockingBlockStore::Block`. It depends on `BlockCacheEntryGuard`, the high-level `Block` trait, and low-level `LLBlockStore` bounds.

## Risks And Test Signals
Methods assume a loaded block always has a cache value and panic if the guarded entry is `None`. This invariant depends on store load/create/remove control flow. Debug output includes ID and cache entry state for diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_block.rs -->
