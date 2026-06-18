<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/waiter.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/waiter.rs

Purpose: RAII handle for a caller registered as waiting on an entry load.

Important APIs/types/functions: `EntryLoadingWaiter<K,E>` owns `EntryLoadingWaiterInner { key, loading_result }`. It is marked `#[must_use]` and intentionally non-cloneable. `wait_until_loaded` awaits the shared `LoadingResult` and returns `Option<AsyncDropGuard<LoadedEntryGuard<...>>>`.

Control flow: on `Loaded`, the waiter calls `ConcurrentStoreInner::_finalize_waiter`, which decrements loaded-state unfulfilled waiter count and grants a loaded guard. On `NotFound` or `Error`, the loading state has already been removed, so no decrement is required.

State and persistence: no persistence. Its main state behavior is guaranteeing one waiter token is redeemed exactly once.

Dependencies/integration: uses `safe_panic!` on `Drop` if the waiter is discarded without awaiting, because that leaks waiter accounting. Integrated by `EntryStateLoading`, `LoadingOrLoaded`, and `Inserting`.

Risks/test signals: cancellation/drop before awaiting is explicitly unsafe and converted to a safe panic. Tests should exercise waiter misuse and successful finalization.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/waiter.rs -->
