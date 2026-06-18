<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/capacity_manager.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/capacity_manager.rs

## Purpose
Implements the hybrid capacity cache used by RustFS capacity reporting. It combines scheduled full scans, write-triggered refreshes, per-disk dirty tracking, and singleflight refresh coordination so capacity queries can avoid repeatedly walking every data directory.

## Important APIs, Types, and Functions
Key configuration helpers expose environment-driven durations and limits such as `get_scheduled_update_interval`, `get_write_trigger_delay`, `get_max_files_threshold`, symlink settings, and dynamic timeout bounds. `CachedCapacityConfig` caches env reads in production and refreshes them in tests. `CachedCapacity`, `CapacityUpdate`, `DiskCapacityUpdate`, and `DataSource` are the core payloads. `HybridStrategyConfig` controls scheduled and write-triggered behavior. `HybridCapacityManager` owns the async cache, write-frequency buckets, dirty disk set, per-disk cache, cache-completeness flag, and `RefreshState`. Public entry points include `get_capacity_manager`, `create_isolated_manager`, `start_background_task`, `update_capacity`, `record_write_operation_with_scope_token`, `needs_fast_update`, `refresh_or_join`, and `spawn_refresh_if_needed`.

## Control Flow
Writes update a rolling 60-second bucket array and may consume a `Uuid` scope token from `capacity_scope`. `needs_fast_update` checks cache freshness, write frequency, and debounce delay. Refreshes are deduplicated: joiners subscribe to a `watch` channel while holding the mutex, while the leader runs the supplied future, catches panics, updates the cache on success, emits metrics, then publishes the result. Background work starts two Tokio tasks, one for scheduled refresh attempts and one for runtime summaries.

## State and Persistence
All state is in memory: an optional global singleton, `RwLock`-protected capacity cache, dirty disk set, per-disk cache, and write buckets. Disk cache completeness is only set after a full per-disk update covers the expected disk count. Dirty disks are cleared after successful scoped updates. No on-disk persistence exists, so restart resets capacity state.

## Dependencies and Integration
Integrates with `scan::refresh_capacity_with_scope`, `capacity_scope` scope registries, `rustfs_config` env constants, `rustfs_utils` env parsing, and `rustfs_io_metrics::capacity_metrics`. It is meant to be called by admin/object-store paths that need cached used-capacity values and by write paths that can propagate dirty disk scope tokens.

## Risks
Production env config is cached once, so runtime env changes are ignored outside tests. Full and scoped refresh correctness depends on stable `(endpoint, drive_path)` keys. If a full scan has partial errors, per-disk cache replacement is suppressed, preventing unsafe subset refresh but also delaying incremental optimization. The global singleton can make tests or embedded runtimes order-sensitive unless isolated managers are used.

## Test Signals
Tests cover env defaults and overrides, cache updates, write frequency windows, future-bucket filtering, fast-update debounce, disabled write triggers, concurrent access, singleflight joiners, background spawn deduplication, dirty scope token handling, global dirty scope draining, per-disk subset total recomputation, and config defaults.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/capacity_manager.rs -->
