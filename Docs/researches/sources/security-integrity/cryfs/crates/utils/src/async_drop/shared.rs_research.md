# sources/security-integrity/cryfs/crates/utils/src/async_drop/shared.rs

Purpose: async-drop-aware equivalent of `futures::future::Shared`, allowing a future that returns `AsyncDropGuard<O>` to be cloned and awaited by multiple consumers.

Important APIs/types/functions: `AsyncDropShared<O,Fut>` stores an `AsyncDropArc<Inner<O,Fut>>` plus a waker key. `Inner` holds `UnsafeCell<FutureOrOutput<O,Fut>>` and a `Notifier`. State constants are `IDLE`, `POLLING`, `COMPLETE`, and `POISONED`. Public APIs include `new`, `new_ready`, `peek`, `strong_count`, `ptr_hash`, `ptr_eq`, and associated `clone`.

Control flow: polling checks completion fast path, records the caller waker, atomically claims polling, polls the inner future with notifier waker, stores output as `AsyncDropArc` on readiness, marks complete, wakes waiters, and returns a cloned output guard. Async drop removes registered wakers and async-drops the shared inner only when the last reference releases it.

State/persistence: all state is in memory: atomic state, slab of wakers, and either future or output. If dropped before completion, `Inner::async_drop_impl` awaits the future to obtain and cleanup any async-drop output.

Dependencies/integration: depends on futures task APIs, `slab`, `UnsafeCell`, atomics, mutexes, and async-drop wrappers. Used where multiple tasks need a shared result with deterministic async cleanup.

Risks: this is concurrency-critical unsafe code. Correctness depends on atomic state transitions guarding `UnsafeCell` access. Panics during poll poison the future. Awaiting an uncompleted future during cleanup can run arbitrary async work during drop.

Test signals: extensive tokio tests cover result/future drop ordering, clone polling, shared output, peek, strong counts, pointer equality/hash, unpolled cleanup, clone after completion, repeated poll, and debug.
