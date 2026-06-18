# sources/storage-engines/tikv/components/in_memory_engine/src/config.rs

## Purpose

Defines the online configuration contract for the in-memory engine and validates derived memory thresholds, timing intervals, and default capacity sizing against block-cache and region-size inputs.

## Important APIs, Types, And Functions

`InMemoryEngineConfig` is a `Serialize`, `Deserialize`, `OnlineConfig` struct using kebab-case field names. Its fields include `enable`, optional `capacity`, optional `evict_threshold`, optional `stop_load_threshold`, `gc_run_interval`, `load_evict_interval`, `mvcc_amplification_threshold`, skipped `cross_check_interval`, and hidden skipped `expected_region_size`. `Default` disables IME with a three-minute GC interval, five-minute load/evict interval, MVCC amplification threshold 10, and no capacity thresholds. `validate` mutates the config in place, computing defaults and rejecting invalid combinations. Accessors `capacity`, `evict_threshold`, and `stop_load_threshold` return `usize` values with zero for unset fields. `config_for_test` provides a fully enabled small test profile. `InMemoryEngineConfigManager` wraps `Arc<VersionTrack<InMemoryEngineConfig>>` and applies `ConfigChange` through online config updates.

## Control Flow

Validation returns immediately when `enable` is false. For enabled configs without manual capacity, it derives capacity as twice 10% of block-cache capacity, disables IME if that value is too small or not larger than region split size, clamps it to 5 GiB, stores it, and subtracts half from block-cache capacity. It then derives `evict_threshold` as capacity minus the smaller of 10% capacity or ten seconds of estimated write throughput, unless supplied; supplied values must be below capacity. It derives `stop_load_threshold` below the eviction threshold, bounded by either 15% of capacity or two region sizes plus reserved write throughput, unless supplied; supplied values must not exceed eviction threshold. It finally enforces GC interval in `[10s, 600s]` and load/evict interval at least 120s.

## State And Persistence Behavior

Config is process state tracked through `VersionTrack`, with changes applied online by `InMemoryEngineConfigManager::dispatch`. It does not persist data directly, but its values control when background workers load, evict, GC, and stop admitting new regions. The validation step can mutate external block-cache capacity, so startup configuration has cross-component memory side effects.

## Dependencies And Integration Points

Uses `online_config` for dynamic updates, `tikv_util::config::{ReadableDuration, ReadableSize, VersionTrack}`, raftstore split-size defaults, and serde. `RegionCacheMemoryEngine::with_region_info_provider`, `MemoryController`, `BgWorkManager::start_tick`, `BackgroundRunner`, `RegionStatsManager`, and tests all read from the shared `VersionTrack`.

## Risks

Misconfigured thresholds can disable IME, trigger constant eviction, or allow loads to exceed memory budget. Manual capacity is not capped by `MAX_CAPACITY` and does not reduce block-cache capacity, by design, so operator-supplied values carry more risk. Validation uses `unwrap` after earlier initialization checks; new fields or call-order changes should preserve those invariants. The skipped `cross_check_interval` is test-only and should not be enabled in production. Online updates bypass this file's startup `validate` path unless the broader config system enforces equivalent validation.

## Test Signals

`test_validate` verifies disabled defaults, valid manual settings, GC interval bounds, derived threshold deltas for 1 GiB and 5 GiB capacities, smaller region split effects, auto-disable for insufficient derived capacity, manual override behavior, block-cache reduction for derived capacity, max derived capacity clamp, and no block-cache reduction for manual over-max capacity.
