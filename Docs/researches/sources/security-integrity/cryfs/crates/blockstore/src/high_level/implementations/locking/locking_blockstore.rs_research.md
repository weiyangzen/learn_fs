<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_blockstore.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_blockstore.rs

## Purpose
Implements the primary high-level blockstore wrapper that adds per-block locking, write-back caching, random-ID creation, and high-level `Block` handles over a low-level store.

## APIs, Flow, And State
`LockingBlockStore<B>` owns an optional `Arc<AsyncDropGuard<B>>` base store plus a `BlockCache`. `load` locks the ID, loads from base store if absent from cache, inserts a clean cache entry, and returns `LockingBlock`. `try_create` locks the ID, rejects cache/base-store existence, and inserts a dirty entry marked absent from base store. `overwrite` sets or replaces a dirty cache entry, checking base existence only when needed. `_remove` removes cached data and optionally removes from base store depending on known base-store state. `num_blocks` combines base count with dirty cache-only blocks; `all_blocks` merges cache keys with base-store stream while filtering duplicates. `create` loops random IDs until `try_create` succeeds.

## Dependencies And Integration
Bridges high-level `BlockStore` to low-level `LLBlockStore`. It relies on `BlockCache`, `BlockBaseStoreState`, `CacheEntryState`, `futures` stream combinators, `HashSet`, and `RemoveResult`/`TryCreateResult`.

## Risks And Test Signals
Persistence depends on flushing dirty cache entries through explicit `flush_block`, pruning, clear-cache hooks, or async drop. Comments flag dangerous lock lifetime in `_remove`, possible inefficiency from double existence checks on create/flush, uncertain `all_blocks` semantics for locked entries, and exception-safety around drop failures. Tests cover generic high-level semantics, create passthrough, random ID retry, remove-before-flush avoiding base removal, remove-after-flush actually removing, error propagation, and overhead forwarding.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_blockstore.rs -->
