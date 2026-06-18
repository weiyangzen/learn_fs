# sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_guard.rs

Purpose: RAII-like guard that forces explicit asynchronous cleanup and panics if forgotten.

Important APIs/types/functions: `AsyncDropGuard<T>(Option<T>)`; `new`, `new_invalid`, `into_box`, `map_unsafe`, `unsafe_into_inner_dont_drop`, `is_dropped`, and `async_drop`. Implements `Drop`, `Deref`, and `DerefMut`.

Control flow: `async_drop` takes the value, calls `AsyncDrop::async_drop_impl`, and leaves `None` so `Drop` is quiet. If dropped while still `Some`, `safe_panic!` reports a forgotten async drop.

State/persistence: in-memory option tracks live vs dropped state. The wrapped value's own `Drop` runs after `async_drop_impl` because the taken value is dropped at the end of the async cleanup path.

Dependencies/integration: central to every async-drop utility. Uses `safe_panic!` to avoid double-panic aborts.

Risks: `map_unsafe` and `unsafe_into_inner_dont_drop` bypass cleanup guarantees and require careful callers. Forgotten cleanup panics at drop time, which may appear far from the bug.

Test signals: unit tests verify panic-on-forget, async cleanup, sync drop ordering, error propagation, and cleanup despite async-drop errors.
