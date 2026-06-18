# sources/storage-engines/tikv/components/tikv_util/src/mpsc/mod.rs

## Purpose
Wraps `crossbeam_channel` to add explicit sender-side close detection and a loose bounded sender variant for high-throughput paths that can tolerate approximate capacity enforcement.

## Important APIs, Types, and Functions
- Public submodules: `future` and `priority_queue`.
- `Sender<T>` wraps `crossbeam::Sender<T>` with shared `State { sender_cnt, connected }`.
- `Receiver<T>` wraps `crossbeam::Receiver<T>`.
- `unbounded`, `bounded`, and `loose_bounded` constructors mirror channel styles.
- `LooseBoundedSender<T>` supports `try_send`, `force_send`, `close_sender`, and connection checks.

## Control Flow
Cloning a sender increments `sender_cnt`; dropping decrements it and closes the sender side when the last sender is dropped. `Sender::send` and `try_send` check `connected` before delegating to crossbeam. Dropping the receiver stores `connected=false`, causing future sends to return disconnected. `LooseBoundedSender::try_send` only checks `len() < limit` every `CHECK_INTERVAL` attempts, using a failpoint to override the interval in tests.

## State and Persistence Behavior
State is process-local channel state. The close flag is separate from crossbeam's own disconnection and allows sender-side early rejection after explicit close or receiver drop.

## Dependencies and Integration Points
Depends on `crossbeam::channel`, atomics, `fail` failpoints, and local async/priority channel submodules. It is a common utility for internal worker queues.

## Risks
Closing a sender does not wake a receiver blocked on `recv`; comments note this is a deliberate performance tradeoff. Loose bounding can temporarily exceed the configured limit and uses `len()` as an approximate concurrent signal. `sender_cnt` uses `AtomicIsize`; misuse outside clone/drop invariants would be unsafe logically.

## Test Signals
Tests cover bounded/unbounded send/receive/disconnect/timeouts, explicit close behavior, zero-capacity blocking, loose-bound overflow, force sends, failpoint-driven capacity checks, and receiver drop handling.
