<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/mod.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/mod.rs

Purpose: `mod.rs` is the module root and public facade for the fast object lock system. It documents the architecture and re-exports the main manager, guard, trait, and types.

Important APIs/types/functions: public modules are `disabled_manager`, `guard`, `manager`, `manager_trait`, `metrics`, `object_pool`, `optimized_notify`, `shard`, `state`, and `types`; test module `tests` is compiled under `cfg(test)`. Re-exports include `DisabledLockManager`, `FastLockGuard`, `FastObjectLockManager`, `LockManager`, and all `types::*`. Constants define default shard count, lock TTL, acquire timeout, max acquire timeout, and cleanup interval.

Control flow: this file has no runtime flow. Its constants influence `LockConfig::default`, `GlobalLockManager` environment clamping, and namespace convenience APIs.

State and persistence behavior: no state is stored. Constants are compile-time defaults; runtime state lives in manager/shard/state modules.

Dependencies and integration points: this facade is consumed by `lib.rs` for public exports and global manager setup; `local_lock.rs` imports lock types and the trait; external crates use `rustfs_lock::FastObjectLockManager`, `ObjectKey`, `BatchLockRequest`, and related exports through this module.

Risks: the default constants are policy-sensitive. `DEFAULT_SHARD_COUNT` must stay power-of-two because `FastObjectLockManager::with_config` asserts that. Increasing acquire/cleanup timeouts changes namespace-lock latency and cleanup memory retention. The private `DEFAULT_RUSTFS_*` constants are used by env parsing in `lib.rs`.

Test signals: module-level tests in `fast_lock/tests.rs` exercise the exported facade rather than private modules only. Build coverage is important because re-export changes affect downstream crates.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/mod.rs -->
