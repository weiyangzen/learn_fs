# sources/storage-engines/tikv/components/resource_control/src/config.rs

`config.rs` defines dynamic resource-control configuration. `Config` is serde-deserializable, kebab-case, and derives `OnlineConfig`. It controls whether resource control is enabled, priority strategy, CPU thresholds for background and foreground throttling, compaction pressure thresholds, background write IO ceiling/floor, fair scheduling, read/write admission control, historical RU baseline window, burst percentage, and maximum delayed admission count. `enabled` and `historical_usage_window_mins` are marked non-online.

Defaults enable resource control with `Moderate` priority control, 60 percent background CPU throttle threshold, 70 percent foreground threshold, 70 percent compaction pressure threshold, 100 GB background write IO ceiling, 10 MB floor, fair scheduling and admission disabled, a 15 minute history window, 20 percent burst allowance, and 10,000 delayed admission slots.

`PriorityCtlStrategy` maps `Aggressive`, `Moderate`, and `Conservative` to resource utilization percentages 0.5, 0.7, and 0.9. It supports display and conversion to/from `online_config::ConfigValue::String`; invalid string values return errors while non-string values panic. `ResourceContrlCfgMgr` wraps `Arc<VersionTrack<Config>>` and applies online changes through `ConfigManager::dispatch`.

State is maintained in `VersionTrack`, not persisted here. Risks include the typo in `ResourceContrlCfgMgr`, panic on wrong `ConfigValue` type, and skipped online fields requiring restart. Tests are not local in this file, so validation is mostly by serde/online-config integration elsewhere.
