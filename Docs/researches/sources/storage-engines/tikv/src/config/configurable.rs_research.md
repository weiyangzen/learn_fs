# `sources/storage-engines/tikv/src/config/configurable.rs` Research

## Purpose

This file defines TiKV's small runtime-configuration adapter for RocksDB-backed engines. It turns higher-level online config updates into concrete `engine_traits` option mutations on either a single `RocksEngine` or a `TabletRegistry<RocksEngine>` that owns many cached tablet engines.

The abstraction lets config managers use one `ConfigurableDb` surface for legacy single RocksDB deployments and partitioned/tablet deployments. Most methods are thin wrappers over RocksDB DB/CF option APIs; the registry implementation adds fan-out, first-live-tablet updates for shared resources, and aggregated error logging.

## Important APIs, Types, and Functions

- `ConfigRes = Result<(), Box<dyn Error>>` is the shared dynamic-config result type. It deliberately erases concrete engine errors so callers in the online config layer can return boxed failures.
- `ConfigurableDb` is the central trait. It supports generic DB options, CF options, rate limiter bytes/sec, auto-tuned rate limiter mode, DB and CF write buffer flush limits, oldest-first flush behavior, shared block cache capacity, and RocksDB high-priority background thread count.
- `impl ConfigurableDb for RocksEngine` is the direct implementation. It delegates to `DbOptionsExt`, `CfOptionsExt`, `DbOptions`, and `CfOptions` from `engine_traits`.
- `loop_registry` iterates `TabletRegistry<RocksEngine>::for_each_opened_tablet`, applies a caller closure to each `CachedTablet<RocksEngine>`, records the last error, and logs up to three sampled tablet path failures.
- `impl ConfigurableDb for TabletRegistry<RocksEngine>` adapts every trait method to `loop_registry`, using `cache.latest()` to mutate only the latest opened tablet engine.

The direct `RocksEngine` methods have a few important details:

- `set_db_config` and `set_cf_config` pass string option pairs to RocksDB via `set_db_options` and `set_options_cf`.
- `set_rate_limiter_auto_tuned` mutates DB options, then reads `get_rate_limiter_auto_tuned` back and returns an `IoError` status if the observed state does not match the requested value.
- `set_shared_block_cache_capacity` retrieves `CF_DEFAULT` options and calls `set_block_cache_capacity`; it currently uses `unwrap()` on `get_options_cf(CF_DEFAULT)`.
- `set_high_priority_background_threads` requires `n > 0`, reads the RocksDB environment, and only lowers the thread count when `allow_reduce` is true.

## Control Flow

For a single `RocksEngine`, the flow is synchronous and direct:

1. The config manager invokes a `ConfigurableDb` method.
2. The method fetches DB or CF option handles where needed.
3. The engine trait call applies the live RocksDB option.
4. Engine errors are boxed and returned to the caller.

For a `TabletRegistry<RocksEngine>`, control runs through `loop_registry`:

1. The registry walks opened tablets with `for_each_opened_tablet`.
2. The closure receives each mutable cached tablet and usually calls `cache.latest()`.
3. If no latest engine is open, the closure returns `Ok(true)` to continue scanning.
4. On success, the closure returns a boolean that controls whether iteration continues.
5. On error, `loop_registry` increments an error count, stores the last error in `res`, samples up to three tablet ids and paths, and continues scanning.
6. After iteration, it logs aggregate errors and returns the last error if any occurred.

The registry methods intentionally differ by resource type:

- `set_db_config` and `set_cf_config` return `Ok(true)` after each successful latest-tablet update, so they attempt to update every opened tablet.
- Rate limiter, flush-size, flush-oldest-first, shared block cache, and high-priority thread updates return `Ok(false)` after the first live tablet. These settings are backed by shared process-level or shared RocksDB resources in this deployment mode, so one live engine handle is sufficient.

## State and Persistence Behavior

This file mutates in-memory/live RocksDB state. It does not persist config files, checkpoints, manifests, or metadata directly. Persistence of online configuration changes belongs to the higher-level `ConfigController` path; this adapter only applies the already-dispatched update to engine handles.

State affected at runtime includes:

- RocksDB DB option strings accepted by `set_db_options`.
- RocksDB CF option strings accepted by `set_options_cf`.
- Rate limiter throughput and auto-tuned mode.
- Write buffer manager flush limits at DB or CF level.
- Flush ordering policy.
- Shared block cache capacity.
- RocksDB environment high-priority background thread count.

`loop_registry` itself only keeps transient counters and sampled error text. It does not remember which tablets succeeded, and it returns the last observed error rather than a structured per-tablet result.

## Dependencies

The file depends on:

- `engine_rocks::RocksEngine` as the concrete RocksDB engine implementation.
- `engine_traits::{DbOptionsExt, CfOptionsExt, DbOptions, CfOptions}` for the option handle APIs.
- `engine_traits::{TabletRegistry, CachedTablet}` for tablet-mode iteration.
- `engine_traits::CF_DEFAULT` for shared block-cache updates through the default column family handle.
- `engine_traits::Status` and `Code::IoError` for the manual rate-limiter verification failure.
- TiKV logging macros for aggregated registry errors.
- `std::io::Write` to build sampled error text in a `Vec<u8>`.

## Integration Points

`src/config/mod.rs` re-exports `ConfigRes`, `ConfigurableDb`, and `loop_registry`, then uses `ConfigurableDb` in `DbConfigManger<D>`. The DB config manager maps online config keys such as RocksDB CF changes, rate-limiter settings, write-buffer limits, background jobs, subcompactions, and remaining DB option changes into this trait.

`src/storage/config_manager.rs` uses the same trait from `StorageConfigManger`. Notable calls are `set_shared_block_cache_capacity` for `storage.block-cache.capacity` and `set_cf_config(..., disable_write_stall)` for storage flow-control enable/disable across all CFs.

Server setup registers these managers with either a `RocksEngine` or `TabletRegistry<RocksEngine>` depending on the deployment path. The server shutdown path in `components/server/src/server2.rs` also calls `loop_registry` directly to raise high-priority background threads before flushing tablets, tolerating errors with a warning because the operation only affects shutdown speed.

The option methods ultimately rely on implementations in `components/engine_rocks/src/db_options.rs` and `components/engine_rocks/src/cf_options.rs`, while the trait contracts live under `components/engine_traits/src`.

## Risks and Edge Cases

- `set_shared_block_cache_capacity` uses `unwrap()` for `CF_DEFAULT` options. If the default CF handle is unavailable or the engine backend changes behavior, a dynamic storage config update can panic instead of returning `ConfigRes`.
- `loop_registry` returns only the last error while logging samples. Callers cannot distinguish partial success from total failure programmatically.
- Registry methods that stop at the first live tablet assume the underlying setting is shared. If a future option is per-tablet but copied into one of these first-live patterns, later tablets will be skipped.
- Registry methods silently skip cached tablets with no `latest()` engine. That is appropriate for open-tablet-only mutation, but an update may not affect tablets opened later unless their options are initialized from the already-updated source config.
- `set_high_priority_background_threads` asserts positive input. Bad validation upstream becomes a panic rather than a recoverable online-config error.
- The direct rate-limiter auto-tune check verifies the option handle's observed state, but only after the engine backend reports success; backend implementations with stale option snapshots would cause false failures.
- The storage flow-control path currently unwraps CF config updates in its loop, so errors from this adapter can panic there even though most config-manager paths propagate errors.

## Test Signals

Relevant tests are mostly in `sources/storage-engines/tikv/src/config/mod.rs`:

- `test_change_rate_limiter_auto_tuned` creates a live engine, updates `rocksdb.rate_limiter_auto_tuned`, and asserts `get_rate_limiter_auto_tuned()` changes accordingly.
- `test_change_shared_block_cache` verifies that shared block cache size cannot be changed through a RocksDB CF config key, then updates `storage.block-cache.capacity` and asserts the default CF block cache capacity changed.
- `test_flow_control` toggles `storage.flow-control.enable` and asserts `disable_write_stall` follows the expected value on the default CF while the flow controller enabled state changes.
- Broader config-manager tests exercise dynamic CF option changes through `DbConfigManger`, including calls that eventually pass through `set_cf_config`.

There does not appear to be a narrow unit test for `loop_registry` error aggregation or the first-live-tablet stopping behavior. Changes to registry fan-out semantics should add tablet-mode tests because the behavior is easy to regress without affecting single-engine tests.
