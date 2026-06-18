<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/manager_trait.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/manager_trait.rs

Purpose: `manager_trait.rs` defines the unified async trait that lets enabled and disabled lock managers share one public API. The trait is used by `GlobalLockManager` to hide whether locking is active at runtime.

Important APIs/types/functions: `LockManager` requires `Send + Sync` and uses `async_trait`. It declares single-lock acquisition, read/write convenience acquisition, batch acquisition, lock inspection, aggregated metrics, total active lock count, object-pool stats, adaptive and traditional cleanup, shutdown, and `is_disabled`.

Control flow: this file has no runtime control flow beyond dynamic/static dispatch through trait methods. Implementors in this module set are `FastObjectLockManager`, `DisabledLockManager` from the same module tree, and `GlobalLockManager` in `lib.rs`, which delegates calls to either enabled or disabled managers.

State and persistence behavior: no state is stored here. The trait shape defines what state implementors must expose: lock info, metrics, pool stats, cleanup, and disabled status. All implementations in this crate are in-memory.

Dependencies and integration points: depends on `FastLockGuard`, `AggregatedMetrics`, `BatchLockRequest`, `BatchLockResult`, `ObjectKey`, `ObjectLockInfo`, `ObjectLockRequest`, and `LockResult`. It is imported by `manager.rs`, `disabled_manager.rs`, `lib.rs`, and `local_lock.rs`. Because methods accept `impl Into<Arc<str>> + Send`, the trait is not object-safe; it is designed for concrete/generic dispatch, not `dyn LockManager`.

Risks: adding object-safety requirements later would require changing generic owner parameters. Implementors must preserve semantics for disabled managers, especially returning disabled guards and empty metrics rather than failing. Divergence between inherent methods and trait methods can cause recursion mistakes, but current implementations explicitly delegate to inherent methods.

Test signals: indirect coverage comes from every `GlobalLockManager` and `LocalLock` test. Disabled-manager-specific behavior is outside this assigned source set but is critical for this trait contract.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/manager_trait.rs -->
