
# sources/user-network-fs/nfs-ganesha/src/SAL/state_async.c

## Purpose

`state_async.c` manages SAL asynchronous execution for state operations, especially blocked NLM/NFS lock callbacks, lock cancellation, and periodic blocked-lock polling. It wraps fridgethr worker pools so state code can schedule operations outside request threads while preserving the necessary export/op context.

## Important APIs, types, and functions

- Global fridges: `state_async_fridge` handles one-off async work; `state_poll_fridge` is a looper for blocked lock polling.
- `state_async_schedule()` schedules a generic `state_async_queue_t` callback through `state_async_func_caller()`.
- `state_block_schedule()` schedules `process_blocked_lock_upcall()` for a blocked lock.
- `state_block_cancel_schedule()` schedules `state_cancel_blocked()`.
- `test_blocking_lock_eligibility_schedule()` schedules `state_test()` plus optional grant callback and updates last poll time.
- `state_async_init()` creates both fridges and starts `blocked_lock_polling`.
- `state_async_shutdown()` stops both fridges with a 120-second timeout and cancels on timeout.

## Control flow

For blocked lock grant and eligibility callbacks, the worker retrieves the saved export from the lock entry, checks `export_ready()`, obtains an export ref, initializes a root request op context, locks the file state with `STATELOCK_lock()`, and invokes the lock processing function. It then unlocks, decrements the lock entry reference, and releases op context.

Cancellation follows a similar export-context setup and calls `state_cancel_blocked()` without taking the state lock in this wrapper. The generic async scheduler simply invokes the function pointer stored in `state_async_queue_t`.

Initialization creates a deferred one-thread async queue and a one-thread looper whose delay comes from `nfs_param.core_param.blocked_lock_poller_interval`.

## State and persistence behavior

The module maintains no persistent state. It holds process-global thread-pool pointers and manipulates references on lock entries and exports. Polling updates `sbd_v4.snbd_last_poll_time` for blocked lock data.

## Dependencies and integration points

It depends on fridgethr, export manager functions, op-context helpers, state lock APIs, lock testing/cancellation helpers, `blocked_lock_polling`, and `nfs_param`. It is initialized/shutdown with SAL state subsystem lifecycle and used by lock conflict paths to notify or poll blocked clients.

## Risks and edge cases

- `state_blocked_lock_cancel()` logs critical and returns without decrementing the lock-entry reference if the export is not ready, which can leak a reference unless upstream prevents this state.
- `state_async_init()` does not tear down `state_async_fridge` if `state_poll_fridge` init or polling submit fails.
- Single-threaded queues serialize all state async work; long callbacks can delay lock notifications.
- Workers rely on saved export pointers remaining valid enough for `export_ready()`/ref acquisition.
- Shutdown returns error if either fridge stop times out or fails; callers must tolerate partial cancellation.

## Test signals

Tests should cover successful scheduling, fridgethr submit failure paths, export-not-ready behavior, reference balance for lock entries, op context setup/release, blocked lock grant after `state_test()`, cancellation, polling interval initialization, and shutdown timeout/cancel paths.
