<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/optimized_notify.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/optimized_notify.rs

Purpose: `optimized_notify.rs` provides a pooled notification mechanism for lock waiters, reducing per-object allocation and limiting broad wakeups under contention.

Important APIs/types/functions: `NOTIFY_POOL` is a lazily initialized vector of 128 shared `tokio::sync::Notify` instances. `OptimizedNotify` stores reader and writer waiter counters plus an index into that pool. Public methods are `new`, `notify_readers`, `notify_writer`, `wait_for_read`, `wait_for_write`, and `has_waiters`.

Control flow: construction selects a pool index from current time nanoseconds. Wait methods increment the corresponding counter, await `notified()` on the selected pooled `Notify`, then decrement the counter. Notify methods check counters and call either `notify_waiters` for readers or `notify_one` for writers.

State and persistence behavior: waiter counters and pool index are atomic in-memory state. Pool entries are global process state shared by many object locks; a notification can wake waiters from unrelated object states that landed on the same pool index. Correctness depends on callers retrying actual lock acquisition after wakeup, which `LockShard::acquire_lock_slow_path` does.

Dependencies and integration points: used by `ObjectLockState` release paths and slow-path waits in `LockShard`. It complements but does not use the traditional `read_notify` and `write_notify` fields still present on `ObjectLockState`.

Risks: `wait_for_read` and `wait_for_write` do not use a cancellation guard internally; if the waiting future is aborted while inside the method, the decrement after `.await` will not run. `LockShard` separately increments/decrements atomic waiting counters with `WaiterCounterGuard`, but these `OptimizedNotify` counters can still leak on cancellation and make `has_waiters`/notify decisions noisy. Pooled notifications can cause spurious wakes, which is acceptable only because lock acquisition is retried. Time-based pool index selection is simple and may cluster under bursty creation.

Test signals: unit tests cover basic read and writer notification completion. Shard cancellation tests cover the separate atomic waiting counters, not the `OptimizedNotify` counters; a targeted cancellation test for `reader_waiters`/`writer_waiters` would be useful.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/optimized_notify.rs -->
