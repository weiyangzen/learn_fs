<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/guard.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/guard.rs

## Purpose
Wraps the `lockable` owned guard for a cached block entry and exposes a narrow API to the locking blockstore.

## APIs, Flow, And State
`BlockCacheEntryGuard<B>` holds the owned guard from `LockableLruCache`. It exposes `key`, immutable/mutable `value`, and `insert`, preserving lock ownership for the guarded block ID. Debug prints the underlying guard.

## Dependencies And Integration
Used by `LockingBlock` and `LockingBlockStore` to keep a block locked while it is loaded or being removed. It abstracts the exact lockable guard type from most of the high-level implementation.

## Risks And Test Signals
Correctness depends on guard lifetime: dropping it releases the per-block lock and may allow cache pruning/removal. Tests around removal and cache flushing indirectly validate that locks survive long enough for operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/guard.rs -->
