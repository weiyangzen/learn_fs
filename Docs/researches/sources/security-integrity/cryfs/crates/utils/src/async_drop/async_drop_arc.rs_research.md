# sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_arc.rs

Purpose: shared-ownership wrapper for `AsyncDropGuard<T>` that async-drops the inner value only when the last reference is dropped.

Important APIs/types/functions: `AsyncDropArc<T>` stores `Option<Arc<AsyncDropGuard<T>>>`. `new`, associated `clone`, `strong_count`, `into_inner`, `as_ptr`, and `ptr_eq` expose Arc-like behavior while retaining async-drop discipline. `Deref`/`Borrow` expose `T`.

Control flow: `async_drop_impl` takes the Arc. If `Arc::into_inner` succeeds, it calls the inner guard's `async_drop`; otherwise it returns `Ok(())` because another reference remains.

State/persistence: in-memory reference-counted ownership only. `Option` is used to mark destruction and panic on use after drop.

Dependencies/integration: depends on futures `BoxFuture`, `AsyncDrop`, `AsyncDropGuard`, `Arc`, `Deref`, and `Borrow`. Used by mock filesystem sharing and `AsyncDropShared`.

Risks: cloning is an associated function, not `Clone`, so callers must learn the custom API. `into_inner` bypasses async drop and transfers responsibility. Access after async drop panics.

Test signals: unit tests cover creation, cloning, strong count, into-inner single/multiple references, last-reference cleanup, and deref.
