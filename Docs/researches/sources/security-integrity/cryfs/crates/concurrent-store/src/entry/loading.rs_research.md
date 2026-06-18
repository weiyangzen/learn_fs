<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loading.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loading.rs

Purpose: models an entry whose loader future is in progress and lets multiple callers await the same load.

Important APIs/types/functions: `EntryStateLoading<V,E>` wraps a shared loading-result future, monotonically increasing `num_waiters`, and an `ImmediateDropRequest`. `LoadingResult<E>` is `Loaded`, `NotFound`, or `Error(E)` and is cloneable for shared futures. `add_waiter` increments waiter count and returns an `EntryLoadingWaiter`.

Control flow: `ConcurrentStoreInner::make_loading_future` creates this state. Waiters await the shared future; on `Loaded`, the map has already transitioned to `Loaded`, and the waiter finalizes against the store. Immediate-drop requests can be registered while loading, then carried into `EntryStateLoaded`.

State and persistence: no persistence; tracks in-memory waiting tasks. Waiters are never decremented in loading state, only transferred to loaded-state unfulfilled waiter accounting.

Dependencies/integration: uses `futures::Shared`, `AsyncDropGuard`, `Event`, and `EntryLoadingWaiter`.

Risks/test signals: a top-level TODO in `store.rs` states cancellation is not safe; if a task waiting for loading is cancelled, counts can be wrong. Tests should target cancelled waiters and immediate-drop during loading.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loading.rs -->
