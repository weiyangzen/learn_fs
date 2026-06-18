# sources/storage-engines/tikv/src/storage/lock_manager/lock_wait_context.rs

## Purpose

This module holds shared state and callbacks for a lock-waiting `AcquirePessimisticLock` request. It guarantees that the request's storage callback is invoked at most once while coordinating wakeup, cancellation, timeout/deadlock errors, and the race where a resumed request re-enters lock waiting.

## Important APIs, Types, And Functions

`PessimisticLockKeyCallback` is called when a blocked key finishes or is canceled before enqueueing. `CancellationCallback` is called by lock-manager timeout/deadlock handling. `LockWaitContextInner` stores the final `StorageCallback`. `LockWaitContextSharedState` stores optional inner callback state, `LockWaitToken`, blocked key, atomic cancellation flag, and one-shot channels for passing an external cancellation error across the resume/enqueue race. `LockWaitContext<L>` wraps shared state, `LockWaitQueues<L>`, and `allow_lock_with_conflict`.

Public methods include `new`, `get_shared_states`, `get_callback_for_first_write_batch`, `get_callback_for_blocked_key`, and `get_callback_for_cancellation`. Internal `finish_request` performs the single completion path.

## Control Flow

When a request first waits, a context is created with a token and callback. The first-write-batch callback is currently a no-op boolean callback that unwraps success. The blocked-key callback calls `finish_request` as `Executed` unless the queue reports cancellation before enqueueing. The cancellation callback calls `finish_request` as `Canceled`.

For executed completions, `finish_request` tells the lock manager to remove the wait token. For cancellations, it sets `is_canceled`, attempts to remove the entry from `LockWaitQueues`, and if the entry is absent assumes the request has been popped and resumed; in that race it stores the cancellation error through `external_error_tx` and returns without taking the final callback. When a later enqueue sees `is_canceled`, it can consume `get_external_error` and finish as canceled before enqueueing. Normal completion takes `ctx_inner` exactly once and either fails the whole request when `allow_lock_with_conflict` is false or returns a one-element pessimistic-lock result when conflicts are allowed.

## State And Persistence Behavior

State is in-memory only. The core persistence property is callback ownership: `ctx_inner: Mutex<Option<...>>` is taken once to prevent duplicate RPC responses. The cancellation flag uses release/acquire ordering. The external error channel is one-shot and consumed in the rare cancellation/resume race.

## Dependencies And Integration Points

The module integrates storage callbacks and process results, pessimistic lock result types, lock manager token allocation/removal, `LockWaitQueues`, transaction keys, and `SharedError`. It is used by scheduler/lock-manager paths that queue, wake, or cancel pessimistic-lock waiters.

## Risks And Edge Cases

The most important edge case is documented in the file: a waiter can be popped for wakeup, encounter the lock again, and race with timeout cancellation. The atomic canceled flag plus external error handoff prevents the waiter from being re-enqueued forever. `finish_request` uses `unwrap` on expected ownership and conversion invariants, so misuse can panic. Double-calling a callback after completion is expected to do nothing only in paths that return early before taking consumed state.

## Test Signals

Tests create mock lock wait contexts, verify first-write-batch callback does not finish the request, verify blocked-key errors complete and drop the response channel, verify late cancellation after completion does not produce a second response, and verify cancellation removes a queued lock-wait entry and returns the expected lock error.
