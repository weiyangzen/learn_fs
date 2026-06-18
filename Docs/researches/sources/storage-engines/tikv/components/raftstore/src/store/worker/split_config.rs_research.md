# sources/storage-engines/tikv/components/raftstore/src/store/worker/split_config.rs

Purpose: this file defines online configuration for load-based region splitting. It centralizes QPS, byte, sampling, balance, contained-range, and CPU overload thresholds used by the auto split controller and read-stat collectors.

Important APIs and types:
- Constants define defaults for detect times, sample count/threshold, QPS and byte thresholds, large-region thresholds, split scores, and CPU overload ratios.
- `get_sample_num()` reads the global `SPLIT_CONFIG` `VersionTrack` if installed, otherwise returns `DEFAULT_SAMPLE_NUM`.
- `SplitConfig` is `Serialize`, `Deserialize`, `PartialEq`, and `OnlineConfig`; fields use kebab-case names. Some deprecated fields are skipped for online config and serialization.
- `SplitConfigManager` wraps `Arc<VersionTrack<SplitConfig>>`, installs it into the global `SPLIT_CONFIG`, implements `ConfigManager`, and dereferences to the underlying `VersionTrack`.

Control flow:
- `SplitConfig::validate` rejects split scores outside `[0,1]`, `sample_num >= qps_threshold`, and CPU ratios outside `[0,1]`.
- `qps_threshold`, `byte_threshold`, and `region_cpu_overload_threshold_ratio` resolve optional values to defaults.
- `optimize_for` fills unset thresholds based on region size. Regions at or above 4096 MiB use higher QPS/byte thresholds and the big-region CPU ratio.
- `SplitConfigManager::dispatch` clones the incoming change, updates the tracked config using generated `OnlineConfig::update`, and logs the accepted change.

State and persistence behavior:
- Configuration is held in memory by `VersionTrack`. Runtime consumers use trackers or `get_sample_num`.
- There is no direct persistence in this file; it participates in TiKV's broader online config infrastructure.
- The global `SPLIT_CONFIG` is a process-wide pointer used by `ReadStats::default` to pick current sample size.

Dependencies and integration points:
- Used by `split_controller.rs` for split decisions and CPU collector registration changes.
- Used by `ReadStats::default` through `get_sample_num`.
- Managed through `online_config::ConfigManager` and re-exported by raftstore worker/store modules.

Risks and edge cases:
- `sample_num` must be lower than QPS threshold; invalid online changes should be rejected before they can make sampling logic ineffective.
- The global config pointer means tests and multiple managers can affect `get_sample_num` process-wide.
- `optimize_for` only fills unset optional fields; explicit user values are preserved even for very large regions.

Test signals:
- `test_static_var_after_config_change` verifies default sample count, manager installation into the static config, online update dispatch, and `get_sample_num` reflecting the updated tracked config.
