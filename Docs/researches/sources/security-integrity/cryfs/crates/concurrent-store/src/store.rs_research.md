<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/store.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/store.rs

Purpose: implements `ConcurrentStore`, a per-key async cache that coalesces concurrent loads, returns shared loaded guards, and asynchronously drops or immediately removes entries when access ends.

Important APIs/types/functions: public methods include `new`, `clone_ref`, `try_insert_loading`, `try_insert_loaded`, `get_loaded_or_insert_loading`, `get_if_loading_or_loaded`, `all_loading_or_loaded`, `is_fully_absent`, test-only `is_empty`, and `request_immediate_drop`. Internal helpers create loading/drop futures, execute immediate drops, remove dropping entries, finalize waiters, and implement `AsyncDrop`.

Control flow: the store map is a `Mutex<HashMap<K, EntryState<V,E>>>`. Absent keys start a loading future; concurrent callers get waiters. Loading futures update the map to `Loaded` or remove entries on not-found/error. Loaded guards call `unload`; when no references or unfulfilled waiters remain, the state becomes `Dropping`, a shared drop future runs outside the lock, and the map entry is removed. Requests during dropping await the shared future and retry. Immediate-drop requests block new access, wait for existing readers, then run a user callback with exclusive access.

State and persistence: all coordination state is in memory. Persistence is delegated to `V::async_drop` or the immediate-drop callback. Store drop panics if loading or loaded entries remain, but waits for dropping futures.

Dependencies/integration: relies on `AsyncDropArc`, `AsyncDropGuard`, `Event`, boxed/shared futures, `for_each_unordered`, `tokio::oneshot`, and `lockable::Never`.

Risks/test signals: a file-level TODO states cancellation is not safe because waiter counts can become wrong. Several async-drop paths use `unwrap()`. Direct tests are absent in this crate, so downstream tests should cover races, immediate drop, failed loads, and store shutdown invariants.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/store.rs -->
