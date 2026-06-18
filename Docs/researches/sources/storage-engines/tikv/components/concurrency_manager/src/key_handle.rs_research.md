# sources/storage-engines/tikv/components/concurrency_manager/src/key_handle.rs

Purpose: represents a per-key entry in the in-memory lock table and provides the RAII guard that serializes mutation of the lock for that key.

Important APIs and types: `KeyHandle`, `KeyHandleGuard`, `KeyHandle::new`, `KeyHandle::lock`, `with_lock`, unsafe `set_table`, `KeyHandleGuard::key`, and `KeyHandleGuard::with_lock`.

Control flow: `KeyHandle::lock` awaits an async mutex and transmutes its guard to `'static` so it can be stored together with an `Arc<KeyHandle>` in `KeyHandleGuard`. The field order ensures the mutex guard drops before the handle `Arc`. `KeyHandleGuard::drop` clears the stored `Lock`, making memory locks live only while the write path holds the guard. `KeyHandle::drop` removes its key from the parent `LockTable`.

State and persistence: in-memory `lock_store: Mutex<Option<Lock>>`; no disk persistence. `table` is an `UnsafeCell<Option<LockTable>>` set once after insertion so drop can remove the map entry.

Dependencies and integration: used by `LockTable` and exposed by `ConcurrencyManager`. Depends on Tokio async mutex for per-key serialization and parking_lot mutex for lock payload reads/writes.

Risks: relies on unsafe lifetime transmute and field-drop ordering; changing struct layout can break safety. `unsafe impl Sync` depends on disciplined access to `UnsafeCell`. Guard drop always clears locks, so callers must keep guards alive until storage write completion.

Test signals: tests verify mutual exclusion across concurrent tasks and weak-reference cleanup behavior after handles and guards drop.
