<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/guard.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/guard.rs

Purpose: loaded-entry guard that keeps an entry alive while a caller uses it and unloads it when released.

Important APIs/types/functions: `LoadedEntryGuard<K,V,E>` stores the owning store, key, and `AsyncDropArc<V>` guard. Public `key`, `value`, and `request_immediate_drop` expose access and keyed deletion. Its `AsyncDrop` impl removes its value guard and calls `ConcurrentStoreInner::unload`.

Control flow: store methods return this guard wrapped in `AsyncDropGuard`. Dropping a guard decreases the value reference count, then `_drop_if_no_references` may transition the map to `Dropping`.

State and persistence: in-memory RAII. Persistence effects occur through `V::async_drop` or immediate-drop callbacks initiated from the guard.

Dependencies/integration: uses `AsyncDrop`, `AsyncDropArc`, `AsyncDropGuard`, `RequestImmediateDropResult`, and `lockable::Never`.

Risks/test signals: implementation uses `unwrap()` on async-drop results with TODOs. Misordered or missing `async_drop` by consumers may leave entries loaded until store drop panics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/guard.rs -->
