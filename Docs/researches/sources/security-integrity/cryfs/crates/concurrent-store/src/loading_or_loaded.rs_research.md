<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/loading_or_loaded.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/loading_or_loaded.rs

Purpose: must-use result object for "get if present or wait for load" operations.

Important APIs/types/functions: `LoadingOrLoaded<K,V,E>` wraps `NotFound`, `Loading { waiter, store }`, or `Loaded(LoadedEntryGuard)`. `wait_until_loaded` normalizes all cases into `Result<Option<LoadedEntryGuard>, E>`.

Control flow: store methods create this wrapper for already loaded entries, existing loading futures, newly started loads, or not-found states. Awaiting it either returns immediately or redeems an `EntryLoadingWaiter`.

State and persistence: no persistent state. It temporarily owns store/waiter references so accounting can be completed correctly.

Dependencies/integration: uses `AsyncDropArc`, `AsyncDropGuard`, `safe_panic!`, and `with_async_drop_2_infallible!`. It integrates with `ConcurrentStore::get_loaded_or_insert_loading`, `get_if_loading_or_loaded`, and `all_loading_or_loaded`.

Risks/test signals: `Drop` safe-panics if not awaited, with a typo in the message (`wait_for_loaded` vs `wait_until_loaded`). Cancellation before wait completion remains part of the broader store cancellation-safety risk.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/loading_or_loaded.rs -->
