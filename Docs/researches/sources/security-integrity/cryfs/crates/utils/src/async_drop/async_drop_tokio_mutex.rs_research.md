# sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_tokio_mutex.rs

Purpose: wraps an `AsyncDropGuard<T>` in `tokio::sync::Mutex` for async interior mutability with proper cleanup.

Important APIs/types/functions: `AsyncDropTokioMutex<T> { v: Option<Mutex<AsyncDropGuard<T>>> }`; `new`, `lock`, and `into_inner`. Implements `AsyncDrop` by taking the mutex, extracting the inner guard, and async-dropping it.

Control flow: users lock to access/mutate the inner value. During async drop, no lock is awaited because ownership of the mutex is consumed.

State/persistence: in-memory mutex state only. `Option` marks destructed state.

Dependencies/integration: used where async-drop values need shared mutable access inside async tasks. Depends on tokio mutex and async-drop primitives.

Risks: if another task holds a lock when outer cleanup is attempted through shared ownership patterns, higher-level code must avoid races. `into_inner` transfers cleanup responsibility.

Test signals: unit tests cover new/lock, mutation, into-inner, and inner cleanup.
