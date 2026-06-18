# sources/storage-engines/tikv/components/tikv_util/src/future.rs

## Purpose
Provides small futures utilities for bridging callbacks to futures, buffering streams, polling futures directly from wakeups, applying timeouts without a Tokio runtime, and periodically running async checks.

## Important APIs, Types, And Functions
`paired_future_callback` returns a boxed one-shot callback and a `futures::channel::oneshot::Receiver`. `paired_must_called_future_callback` wraps the sender in `callback::must_call` so a fallback value is produced if the callback is dropped uncalled.

`create_stream_with_buffer` returns an mpsc receiver stream plus a driver future that forwards items from a remote stream into the bounded buffer. `poll_future_notify` installs a custom `ArcWake` implementation that immediately polls the boxed future on the thread invoking `wake`.

`try_poll` synchronously polls once and returns `Some` only for immediately ready futures. `block_on_timeout` blocks the current thread until a future or global timer delay completes. `async_timeout` is async and uses a fast path that avoids creating a timer if the wrapped future completes immediately. `RescheduleChecker` runs a future builder after a configured TiKV duration has elapsed.

## Control Flow
The callback helpers send through oneshot channels and log a warning if the receiver was dropped. Stream buffering maps each stream item into `Ok` and forwards into the mpsc sender, logging send failures.

The `PollAtWake` state machine uses `IDLE`, `POLLING`, and `NOTIFIED` in an `AtomicU8`. A poller wins `IDLE -> POLLING`, polls the future, and tries to return to `IDLE`; wakeups during polling switch `POLLING -> NOTIFIED`, causing the polling thread to loop and poll again before releasing. When the future returns ready, the stored future is taken and later wakeups are ignored.

`block_on_timeout` selects between the fused future and a global timer delay. `async_timeout` first uses `select_biased!` against `ready(())`; if the future is pending, it creates a timer and selects between completion and timeout. `RescheduleChecker::check` compares elapsed coarse time with the configured interval, awaits the built future, and resets its start time.

## State And Persistence
State is in-memory: one-shot channels, mpsc buffers, the `UnsafeCell<Option<BoxFuture>>` inside `PollAtWake`, atomic poll state, and `RescheduleChecker`'s last-run instant. There is no persistence.

## Dependencies And Integration
Depends on `futures`, `futures_util::compat`, TiKV `GLOBAL_TIMER_HANDLE`, `callback::must_call`, and TiKV time wrappers. It is useful in yatp/future-pool contexts where Tokio runtime assumptions are undesirable.

## Risks
`PollAtWake` relies on unsafe `UnsafeCell` sharing and careful atomic transitions; incorrect future `Send` assumptions or unexpected reentrant wake patterns would be high risk. `block_on_timeout` blocks the current thread and should not be used where blocking harms scheduler progress. `async_timeout` returns a boxed dynamic error for timeout and does not cancel external side effects of the wrapped future beyond dropping it. The lazy timer fast path intentionally polls the future once immediately, so future implementations must tolerate normal poll semantics.

## Test Signals
Tests verify in-place wake repolling counts, `try_poll` ready/pending behavior, successful timeout completion, timeout error messages, immediate completion fast path, propagation of `Result` outputs, and the lazy timer behavior for fast and slow futures.
