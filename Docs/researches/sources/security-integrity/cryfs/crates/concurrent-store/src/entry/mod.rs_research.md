<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/mod.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/mod.rs

Purpose: central module for the per-key state machine used by `ConcurrentStoreInner`.

Important APIs/types/functions: `EntryState<V,E>` has `Loading(EntryStateLoading)`, `Loaded(EntryStateLoaded)`, and `Dropping(EntryStateDropping)` variants. The module re-exports loading, loaded, dropping, immediate-drop, and waiter types used by `store.rs`.

Control flow: all transitions are driven from `store.rs`: absent to loading, loading to loaded or absent, loaded to dropping, dropping to absent. The enum keeps those transitions explicit and type checked.

State and persistence: this module defines in-memory state only. Persistence effects are deferred to value `AsyncDrop` or immediate-drop callbacks.

Dependencies/integration: depends on `cryfs_utils::async_drop::AsyncDrop` to constrain stored values. It is private to the crate but its subtypes are visible within crate modules.

Risks/test signals: the module has no tests of its own; correctness depends on store-level transition tests. Any new state variant must update all exhaustive matches in `store.rs`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/mod.rs -->
