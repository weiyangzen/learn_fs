# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_pool.rs

Purpose: allocates, releases, and optionally reserves typed handles with generation counters.

Important APIs: `HandlePool::new`, `acquire`, `acquire_specific`, `try_acquire_specific`, `release`, `undo_acquire`, and `lookup`.

Control flow and state: it tracks `in_use_handles: HashMap<Handle, u64>`, `released_handles: Vec<HandleWithGeneration<Handle>>`, and `next_handle`. `acquire` prefers recycled handles, otherwise returns `next_handle` and advances it. `try_acquire_specific` can jump forward, releasing skipped handles into the free list. `release` increments generation; `undo_acquire` returns a handle without incrementing generation for failed transactional inserts.

Dependencies and integration: generic over `HandleTrait`. Used by `HandleMap` and `HandleForest`, making it foundational for file handles and inode numbers.

Risks and tests: several invariant violations panic: releasing unused handles, exhausting handle range, generation overflow. Released handles are LIFO, which is fine but may make reuse patterns surprising. TODO calls for tests.
