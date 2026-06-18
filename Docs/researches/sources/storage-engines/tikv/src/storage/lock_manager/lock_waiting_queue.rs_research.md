# sources/storage-engines/tikv/src/storage/lock_manager/lock_waiting_queue.rs

## Purpose

This file implements `LockWaitQueues`, the per-key waiting queue used by TiKV storage when `AcquirePessimisticLock` requests encounter an existing lock. It tracks blocked lock acquisition requests, orders them by transaction start timestamp, wakes them when the blocking lock is released, and supports the legacy retry behavior where non-resumable waiters are cancelled with `WriteConflict` after a delayed wake-up window. It also connects queue changes to lock-manager wait-for updates and Prometheus metrics.

The module-level comments are important design documentation. They distinguish legacy requests (`allow_lock_with_conflict == false`) from resumable requests (`allow_lock_with_conflict == true`) and explain why delayed notification exists: after a legacy waiter is woken and returns retry to the client, the key may remain unlocked and older waiters must not wait forever for a release event that may never happen.

## Important APIs, Types, and Functions

`LockWaitEntry` represents a single waiting pessimistic-lock request. It stores the target `Key`, a precomputed `lock_hash`, full `PessimisticLockParameters`, key-local flags (`should_not_exist`, `is_shared_lock`), its `LockWaitToken`, shared cancellation state, optional `legacy_wake_up_index`, and the key callback to finish the request. Its ordering reverses `start_ts` comparison so `KeyedPriorityQueue`, which is a max heap, pops the smallest start timestamp first.

`KeyLockWaitState` is the value stored per key in the dashmap. It contains the latest known `current_lock`, a `legacy_wake_up_index` counter, the keyed priority queue, the latest conflict timestamps used to construct `WriteConflict`, and optional delayed-notify state `(id, start_time, delay_duration)`.

`LockWaitQueueInner` holds the concurrent `DashMap<Key, KeyLockWaitState>`, internal delayed-notify id allocator, atomic entry count, and the generic `LockManager`. `LockWaitQueues<L>` wraps it in `Arc` so handles can be cloned into delayed futures.

`push_lock_wait` inserts a `LockWaitEntry` for its key, initializes per-key state when needed, records the current legacy wake index on first insertion, refreshes `current_lock`, increments `entries_count`, and updates `LOCK_WAIT_QUEUE_ENTRIES_GAUGE_VEC` plus `LOCK_WAIT_QUEUE_LENGTH_HISTOGRAM`.

`on_push_canceled_entry` handles the corner case where a request was cancelled while temporarily absent from the queue. If the stored external error is `KeyIsLocked`, it replaces the embedded lock info with the latest per-key `current_lock` when available, then invokes the waiting callback as cancelled.

`pop_for_waking_up` and `pop_for_waking_up_impl` remove the next waiter or a consecutive group of shared-lock waiters. Legacy waiters increment the per-key wake index and may schedule delayed notification if more entries remain. The method returns popped entries plus an optional `DelayedNotifyAllFuture` that the caller must execute.

`handle_delayed_wake_up`, `async_delayed_notify_all`, and `delayed_notify_all` implement the delayed legacy wake path. Existing delayed tasks are extended by atomically increasing the target delay. A new task sleeps through `GLOBAL_TIMER_HANDLE`, checks that its notify id still matches the key state, drains only entries whose recorded legacy index predates the latest wake-up, cancels legacy entries with `WriteConflict`, and stops at the first resumable entry, returning it to the caller for resumed execution.

`remove_by_token` removes a particular waiter from a key queue without calling the callback. The caller owns completion/cancellation after removal.

`update_lock_wait` accepts fresh `LockInfo` records, updates `current_lock` for matching keys, builds `UpdateWaitForEvent` entries for each queued waiter, and calls `lock_mgr.update_wait_for` so deadlock detection and wait-for diagnostics track the latest blocking lock.

`entry_count`, `is_empty`, and test-only assertion helpers expose queue state.

## Control Flow

The normal enqueue path starts when storage creates a `LockWaitEntry` for a lock conflict and calls `push_lock_wait`. The function checks cancellation state before insertion, gets or creates a per-key `KeyLockWaitState`, stamps legacy entries with the current wake index, pushes into the keyed priority queue by token, increments atomic and Prometheus counters, and records queue length.

When a lock release can wake waiters, callers use `pop_for_waking_up`. Under `DashMap::remove_if_mut`, the implementation updates conflict timestamps, pops the highest-priority entry, optionally keeps popping adjacent shared-lock entries, updates legacy wake state, schedules or extends delayed notification if legacy waiters were popped and the queue is still non-empty, decrements counts, and removes the key entry if the queue is empty.

The delayed notification flow is asynchronous but stateful. A queued future waits until elapsed time reaches the latest atomic delay value, allowing later legacy wakeups to extend the same task. On timeout, `delayed_notify_all` verifies the notify id to avoid acting on stale recreated key state, clears delayed state, drains only entries that existed before the wake event, cancels drained legacy entries with `PessimisticRetry` write conflicts, and returns one resumable entry if encountered.

Cancellation can happen outside the queue through `LockWaitContextSharedState`. If a waiter is still queued, external cancellation eventually removes it by token. If cancellation happens while a waiter is being re-pushed after temporary removal, `push_lock_wait` detects it and calls `on_push_canceled_entry`.

`update_lock_wait` is a side-channel refresh path. It does not reorder queues; it updates diagnostic/current-lock information and propagates revised wait-for edges to the lock manager.

## State and Persistence Behavior

All state is in memory. There is no durable persistence in this file. Queue state is held in a concurrent `DashMap`, each key state owns an in-memory priority queue, and counts are maintained in atomics plus Prometheus metrics. Delayed wake-up state is also in memory and keyed by an internal id so stale futures do not mutate newly recreated queues.

The logical state invariants are more important than persistence: `entries_count` should match total queued entries, `LOCK_WAIT_QUEUE_ENTRIES_GAUGE_VEC.waiters` and `.keys` should track waiters and non-empty key queues, and `legacy_wake_up_index` partitions old waiters from waiters that arrived after the wake event that scheduled delayed notification.

The callback in each `LockWaitEntry` is consumed exactly when a waiting request is cancelled by delayed notification or by the cancelled-on-push path. Pop and remove paths intentionally return entries without invoking callbacks so upper layers can resume, retry, or otherwise finish the request.

## Dependencies and Integration Points

The implementation depends on `dashmap` for concurrent key-state storage, `keyed_priority_queue` for token-addressable priority queues, `smallvec` for small batches of delayed cancellations, `sync_wrapper` for storing callback closures, `GLOBAL_TIMER_HANDLE` plus `Future01CompatExt` for sleeping delayed tasks, and TiKV transaction types such as `Key`, `TimeStamp`, `PessimisticLockParameters`, `StorageError`, `TxnError`, and `MvccError`.

The generic `LockManager` integration is used through `update_lock_wait` and through test mocks. `LockWaitToken`, `KeyLockWaitInfo`, `LockDigest`, and `UpdateWaitForEvent` come from the sibling lock-manager module. Metrics are imported from `storage::metrics` and updated on enqueue, pop, removal, and delayed drain.

Storage command execution must run returned `DelayedNotifyAllFuture` values. The queue itself does not own a runtime or thread pool, so missing future execution would leave legacy waiters blocked until another path wakes or cancels them.

## Risks and Edge Cases

The main correctness risk is count drift between the queue map, `entries_count`, and Prometheus gauges. The code decrements inside `remove_if_mut` and then adjusts metrics after lock release; any future changes to early returns or multi-entry shared pops must preserve those paths.

The delayed wake logic is subtle. It relies on `legacy_wake_up_index` comparisons, notify ids, and an atomically extendable delay. Off-by-one changes can either over-cancel new waiters, causing unnecessary retries, or under-cancel old waiters, causing indefinite waiting.

Shared-lock grouping wakes consecutive shared waiters only at the front of the queue. This assumes the priority ordering plus `is_shared_lock` semantics are sufficient; mixed shared/exclusive waiters require careful tests so exclusive waiters are not bypassed incorrectly.

Callback ownership is a risk because `key_cb` is an `Option` that is unwrapped in cancellation paths. Callers must only enqueue entries with callbacks and must avoid double-consuming a callback.

`on_push_canceled_entry` rewrites nested error lock info only for a specific `StorageError::Txn::Mvcc::KeyIsLocked` shape. New error variants or wrapper changes could make cancellation return stale lock info.

`async_delayed_notify_all` unwraps the timer result. Timer failures are presumably fatal/unexpected in TiKV, but this is still a panic edge.

## Test Signals

The file contains focused unit tests and benches. `test_simple_push_pop` validates basic enqueue, pop, key removal, and empty-state accounting. `test_popping_priority` verifies start-ts ordering and duplicate start timestamps. `test_removing_by_token` exercises targeted removal and idempotent missing-token removal. `test_dropping_cancelled_entries` validates external cancellation removing queued entries.

`test_delayed_notify_all` is the most important behavioral test. It covers delayed legacy wake-up, avoiding wake of entries added after the scheduling wake event, stopping at a resumable waiter, stale/mismatched notify ids, extending an existing delayed future, latest conflict timestamp propagation, and no-op behavior for missing keys.

`test_pop_shared_group` checks grouped popping of consecutive shared lock waits and transition to a later exclusive wait. Two benchmarks measure `update_lock_wait` overhead for an empty/mismatched update and a queue with 512 waiters.
