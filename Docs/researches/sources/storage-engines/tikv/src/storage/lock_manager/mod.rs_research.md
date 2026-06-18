# sources/storage-engines/tikv/src/storage/lock_manager/mod.rs

## Purpose

This module defines the storage lock-manager interface used by TiKV transactions that wait for pessimistic locks. It provides common types for describing lock wait relationships, a timeout encoding helper, diagnostic context carried into wait tracking, and the `LockManager` trait implemented by real server-side deadlock/waiter managers. It also exports the `lock_wait_context` and `lock_waiting_queue` submodules.

The file is the boundary between storage code that encounters locks and the server lock-manager subsystem that tracks wait-for relationships, timeouts, cancellation, deadlock handling, and diagnostic dumps.

## Important APIs, Types, and Functions

`LockDigest` is a compact identity for a blocking lock: its transaction timestamp plus a key hash.

`DiagnosticContext` carries diagnostic metadata for lock waits: the key of interest, TiDB resource group tag or SQL digest-style tag, and a `TrackerToken`. Its custom `Debug` implementation logs key-like fields through `log_wrappers::Value::key`, avoiding raw sensitive key output.

`WaitTimeout` models lock wait timeout policy. `Default` means use the caller-provided ceiling, while `Millis(u64)` is capped by `into_duration_with_ceiling`. `from_encoded` maps protobuf-style timeout integers into `Option<WaitTimeout>`: zero means default, positive means explicit milliseconds, and negative means no wait (`None`).

`KeyLockWaitInfo` describes the lock a request is waiting for. It includes the waiting key, `LockDigest`, full protobuf `LockInfo`, and whether the request is allowed to lock despite conflict.

`LockWaitToken` uniquely identifies a waiting request. The token wraps `Option<u64>`, allowing invalid/no-token states; `is_valid` checks for `Some`.

`UpdateWaitForEvent` carries updates for an existing wait-for edge: token, waiting transaction start timestamp, first-lock flag, and new `KeyLockWaitInfo`.

`LockManager` is the key trait. Implementors must allocate tokens, register wait-for relationships through `wait_for`, update them through `update_wait_for`, remove waiters, expose a cheap `has_waiter` hint, and dump wait-for entries through `waiter_manager::Callback`.

`MockLockManager` is a test implementation backed by `Arc<AtomicU64>` token allocation and an `Arc<parking_lot::Mutex<HashMap<LockWaitToken, (KeyLockWaitInfo, CancellationCallback)>>>`. It can simulate timeout for all waiters or a single waiter by invoking stored cancellation callbacks with `KeyIsLocked` errors.

## Control Flow

The typical flow begins with storage code calling `allocate_token`, then creating lock wait context and queue state tied to that token. When a transaction must wait on a lock, storage calls `wait_for` with region metadata, transaction start timestamp, `KeyLockWaitInfo`, first-lock status, timeout policy, cancellation callback, and diagnostics. The real implementation records the dependency for timeout/deadlock handling.

If the underlying blocking lock information changes while the request is still waiting, storage or `LockWaitQueues` calls `update_wait_for` with `UpdateWaitForEvent` records. If the waiter no longer needs tracking, `remove_lock_wait` removes it. Monitoring or diagnostics can call `dump_wait_for_entries`.

The mock follows the same broad contract but stores only `wait_info` and cancellation callbacks. `simulate_timeout_all` drains the map and cancels every waiter. `simulate_timeout` removes and cancels one token.

## State and Persistence Behavior

This file defines in-memory interfaces and test state only. There is no durable persistence. `DiagnosticContext` and wait-info structs are passed by value into runtime managers. `MockLockManager` persists waiters only for the lifetime of the test object.

The important state contract is token identity. `LockWaitToken` must be allocated before wait registration so related storage structures and cancellation callbacks can reference the same waiter. Mock token allocation uses relaxed atomics, which is enough for uniqueness in tests because the token value has no synchronization semantics.

## Dependencies and Integration Points

The module depends on `kvproto` lock and region metadata, TiKV `txn_types::{Key, TimeStamp}`, `tracker::TrackerToken`, `collections::{HashMap, HashSet}`, and `parking_lot::Mutex` for the mock. It imports server lock-manager callback types from `crate::server::lock_manager::waiter_manager`.

It re-exports `CancellationCallback` from `lock_wait_context`, making cancellation callback type usage available to other storage modules. It declares `lock_wait_context` and `lock_waiting_queue`, whose code uses the trait and types here.

Error integration in the mock uses `StorageError`, `TxnError`, and `MvccErrorInner::KeyIsLocked` to emulate timeout/deadlock cancellation paths expected by storage callers.

## Risks and Edge Cases

Timeout decoding is compact but semantically loaded: negative encoded values return `None`, meaning no wait rather than an immediate timeout. Callers must preserve that distinction.

`LockWaitToken(None)` is representable. Code using tokens must either validate with `is_valid` or be designed to tolerate invalid tokens.

The default `has_waiter` returns `true`, favoring correctness over optimization. Real implementations should override it if they want to avoid unnecessary wake-up calculations.

`DiagnosticContext::Debug` intentionally redacts key-like fields. Future changes should avoid accidentally logging raw keys or resource tags.

The mock `remove_lock_wait` is a no-op, unlike a real lock manager. Tests that rely on exact removal semantics need either a richer mock or direct map inspection.

## Test Signals

There are no direct `#[test]` functions in this file. Its test signal is the `MockLockManager`, which supports unit tests in `lock_waiting_queue.rs` and other storage modules. The mock exposes `simulate_timeout_all`, `simulate_timeout`, and `get_all_tokens` to validate cancellation behavior and token registration.
