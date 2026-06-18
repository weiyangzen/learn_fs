# sources/storage-engines/tikv/components/cdc/src/watchdog.rs

## Purpose
`watchdog.rs` monitors a CDC EventFeed connection for stalled flushing under high memory pressure and explicitly aborts both receive and send tasks when the connection remains idle beyond configured thresholds.

## Important APIs, Types, and Functions
- `Config` holds check interval, idle deregister threshold, and memory-quota abort ratio; failpoints can override thresholds.
- `FlushActivity` shares the last successful flush `Instant` through `Arc<AtomicCell<Instant>>`.
- `WatchdogHandle` returns activity plus receive/send abort receivers and a `ForwardExitGuard`.
- `wait_for_abort` resolves only on explicit abort; dropped senders intentionally park forever.
- `Watchdog::spawn` and `spawn_with_activity` create abort channels, forward-exit signal, and spawn `run` on the worker pool.
- `check_and_maybe_abort` compares idle duration and memory quota usage, then aborts idempotently.

## Control Flow
The watchdog runs a timer interval via `GLOBAL_TIMER_HANDLE`. Each tick logs when the connection has been idle longer than one check interval, and aborts only if idle time exceeds `idle_deregister_threshold` and `MemoryQuota::used_ratio` is at or above the configured threshold. Dropping `ForwardExitGuard` wakes the watchdog and stops polling for normal send-task exit.

## State and Persistence Behavior
All state is per-connection and in-memory: last flush timestamp, abort senders, forward-exit receiver, peer string, connection id, and memory-quota reference. No persistent state is written.

## Dependencies and Integration Points
`service.rs` holds the returned `ForwardExitGuard` in the send task, passes `FlushActivity` into channel forwarding, and races send/receive futures against `wait_for_abort`. The watchdog uses TiKV worker pools, global timers, failpoints, and `MemoryQuota`.

## Risks and Edge Cases
Abort requires both idle duration and memory pressure, preventing cancellation of quiet but healthy streams. `wait_for_abort` intentionally hangs on sender drop, so misuse could leak a pending future. `memory_quota_abort_threshold` currently uses the same failpoint name as `idle_deregister_threshold`, which may be surprising for test control.

## Test Signals
Unit tests verify watchdog cancellation of both send and receive under quota pressure, idempotent abort sender behavior, and `wait_for_abort` not completing when sender side is simply dropped.
