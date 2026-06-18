<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/object_pool.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/object_pool.rs

Purpose: `object_pool.rs` implements a small lock-state pool to reduce allocation churn for `ObjectLockState` entries removed by cleanup.

Important APIs/types/functions: `ObjectStatePool` wraps a lock-free `crossbeam_queue::SegQueue<Box<ObjectLockState>>` and `PoolStats` atomic counters. `acquire` pops a state, resets it, and records a hit or creates a new state and records a miss. `release` pushes states back while the pool length is below 1000 and records releases. `stats` and `hit_rate` expose pool health. An extension impl on `ObjectLockState` adds `reset_for_reuse`.

Control flow: cleanup in `LockShard::cleanup_expired_batch` attempts `Arc::try_unwrap` on idle lock states; if successful it boxes and returns them to this pool. Future acquisitions take states from the pool, resetting atomics, owners, shared owners, priority, and optimized notification before reuse.

State and persistence behavior: pool state is process-local and bounded by a soft `pool.len() < 1000` check. The queue length check is approximate under concurrency. Reset explicitly clears owner/priority fields and creates a new `OptimizedNotify`; traditional `Notify` fields are not reset directly because the entire `ObjectLockState` value came from an unwrapped object.

Dependencies and integration points: depends on `ObjectLockState`, `AtomicLockState`, `OptimizedNotify`, `LockPriority`, `crossbeam_queue`, and parking_lot locks inside the state. `LockShard` owns one pool per shard and exposes stats through manager APIs.

Risks: pooling is safe only for states no longer referenced by any lock holder or waiter. The shard only recycles after `Arc::try_unwrap`, which protects against outstanding `Arc`s, but future code must maintain that invariant. `pool.len()` on `SegQueue` can be expensive or approximate under load. Reset changes `optimized_notify` but not every field by name, so new fields added to `ObjectLockState` must be added to `reset_for_reuse`.

Test signals: unit tests check hit/miss/release accounting and owner reset. Cleanup-path tests should confirm recycled states do not retain owners, waiting counters, priority, or notifications across keys.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/object_pool.rs -->
