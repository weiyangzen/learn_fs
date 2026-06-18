# sources/storage-engines/tikv/src/storage/txn/tracker.rs

## Purpose
`tracker.rs` implements `TlsFutureTracker`, a `tracker::FutureTrack` adapter that measures scheduler future active poll time and suspended-between-polls time. It exists because scheduler callbacks may be invoked inside future polling, and TiKV wants request trackers to contain accurate timing before callbacks hand details back to the gRPC layer.

## Important APIs, types, and functions
`PollState` records whether timing has been collected, a poll began at an `Instant`, or a poll finished at an `Instant`. `State` stores the tracker token, command kind tag, command ID, current poll state, accumulated future process nanoseconds, and accumulated suspend nanoseconds. `CURRENT_STATE` is TLS holding the state for the currently polled future.

`TlsFutureTracker::new` creates a tracker in `Finished(now)` state so the wait before the first poll is counted as suspend time. `TlsFutureTracker::collect_to_tracker` reads the TLS current state, folds any active poll duration into accumulated process time, adds accumulated process/suspend nanoseconds to the provided global tracker, resets the accumulators, and marks the state as `Collected` to avoid double counting before the poll finish hook.

`State::on_poll_begin` accounts suspend time from the previous finish to the new begin. `State::on_poll_finish` accounts active process time and writes it into the request tracker. The `FutureTrack` implementation moves state between the wrapper and TLS on poll begin/finish and uses `GLOBAL_TRACKERS.with_tracker` to update the global tracker by token.

## Control flow
Scheduler futures are wrapped with `tracker::track(future, TlsFutureTracker::new(...))`. On every poll begin, the wrapper takes its state, accounts any suspend interval, sets state to `Began(now)`, and installs it into TLS. Code inside the future can call `TlsFutureTracker::collect_to_tracker` just before a callback, which updates request metrics while the future is still polling. On poll finish, the TLS state is removed, process time is collected if it was not already collected, state is set to `Finished(now)`, and moved back into the wrapper for the next poll.

## State and persistence behavior
This module maintains only in-memory timing state. It updates `tracker.metrics.future_process_nanos` and `tracker.metrics.future_suspend_nanos`, which later feed request execution details. It does not interact with storage persistence.

## Dependencies and integration points
The implementation depends on `tikv_util::time::Instant`, the external `tracker` crate's `FutureTrack`, `GLOBAL_TRACKERS`, and `TrackerToken`, plus storage `CommandKind` for debugging messages. `TxnScheduler` uses it around futures submitted to `SchedPool` and calls `collect_to_tracker` before early responses, normal completions, and error completions.

## Risks and edge cases
The state machine intentionally panics on impossible poll ordering, missing TLS state, double TLS installation, or missing wrapper state. This catches nested or incorrectly tracked futures but makes misuse fail hard. `collect_to_tracker` expects to be called only while a tracked future is polling and TLS state is present. If the global tracker has already been removed, the poll-finish path simply cannot update it, but direct collection into a provided standalone tracker still works when TLS state exists.

The `Collected` state prevents double counting when collection happens inside a poll before the poll finish hook. Future suspend time includes wall-clock time before the first poll and between polls; process time includes wall-clock time spent inside polls and can include blocking work done during a poll.

## Test signals
`test_tracker` wraps a oneshot future, forces two polls with sleeps, calls `collect_to_tracker` inside the second poll, and asserts suspend time covers the waiting/sleep interval while process time covers only the intended in-poll work. `test_no_tracker` removes the global tracker before completion, verifies collection does not depend on the token being live for standalone tracker use, and asserts TLS state is cleared after completion.
