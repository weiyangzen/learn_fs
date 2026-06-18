<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/lib.rs -->
# sources/object-store/rustfs/crates/lock/src/lib.rs

Purpose: `lib.rs` is the crate root for `rustfs-lock`. It declares modules, re-exports the public API, defines version/policy constants, and provides the global lock manager singleton with runtime enabled/disabled selection.

Important APIs/types/functions: modules include `distributed_lock`, `local_lock`, `namespace`, `client`, `fast_lock`, `error`, and `types`. Public re-exports cover clients, guards, errors, fast-lock managers/types, namespace wrappers, and core lock/health structures. `GlobalLockManager` is an enum over `Enabled(Arc<FastObjectLockManager>)` and `Disabled(DisabledLockManager)`. `GlobalLockManager::new` reads lock enablement and acquire-timeout environment variables, clamps timeout, and constructs the appropriate manager. `get_global_lock_manager` returns the `OnceLock` singleton; `get_global_fast_lock_manager` is deprecated and panics when locks are disabled.

Control flow: when the singleton is first requested, environment variables are read. `RUSTFS_LOCK_ENABLED` is canonical and `RUSTFS_ENABLE_LOCKS` is a deprecated alias. If disabled, a `DisabledLockManager` is returned. If enabled, `RUSTFS_LOCK_ACQUIRE_TIMEOUT` is clamped to [1, max] seconds and installed into `LockConfig::default_acquire_timeout`, then a fast manager is created. The `LockManager` trait impl delegates every method to the active enum variant.

State and persistence behavior: global manager state is process-local in a `OnceLock<Arc<GlobalLockManager>>`; environment changes after initialization have no effect. No lock state persists across restarts. Version/build constants are compile-time strings.

Dependencies and integration points: `rustfs_utils` provides env parsing with aliases; `fast_lock` supplies manager/config/constants; `namespace` and `client` form the higher-level locking API. Downstream object-store code uses `NamespaceLockWrapper`, `GlobalLockManager`, and the re-exported request/response types.

Risks: creating the global manager can spawn a Tokio cleanup task through `FastObjectLockManager::with_config`, so initialization context must have a runtime. The configured `default_acquire_timeout` in `LockConfig` may not affect all request constructors, which use module constants unless the caller sets timeouts explicitly. OnceLock makes tests involving env changes order-dependent unless isolated. Deprecated `get_global_fast_lock_manager` panics in disabled mode.

Test signals: namespace tests create fresh `Arc<GlobalLockManager::new()>` instances heavily, exercising enabled mode and trait delegation. Disabled-mode env tests are not in the listed files and would be important for this facade.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/lib.rs -->
