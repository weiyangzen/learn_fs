<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/inserting.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/inserting.rs

Purpose: must-use handle returned by `try_insert_loading` for a caller inserting a newly loaded entry.

Important APIs/types/functions: `Inserting<K,V,E>` owns store access and an `EntryLoadingWaiter`. `wait_until_inserted` awaits the load and returns a `LoadedEntryGuard`, asserting the insert loader cannot return `None`.

Control flow: `try_insert_loading` installs a loading state with a loader wrapped to return `Some(entry)` and returns `Inserting`. The caller must drive `wait_until_inserted`, which drives the underlying shared future and finalizes waiter accounting.

State and persistence: no persistence; holds in-memory insertion state until redeemed.

Dependencies/integration: uses `with_async_drop_2_infallible!` to keep the store guard alive while awaiting. `Drop` calls `safe_panic!` if the handle is discarded without waiting.

Risks/test signals: if callers ignore this `#[must_use]` type at runtime, the store can leak loading/waiter state. The invariant that insertion loaders never return `None` is enforced by `expect`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/inserting.rs -->
