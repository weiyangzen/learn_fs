# sources/object-store/rustfs/crates/scanner/src/runtime_config.rs

## Purpose

`runtime_config.rs` resolves, validates, applies, and reports scanner runtime configuration. It merges defaults, persisted server config, scanner compatibility config, environment variables, and deployment-specific default overrides into a single `ScannerRuntimeConfig`. It also updates the global scanner sleeper so pacing changes take effect in scanner loops.

## Important APIs, Types, and Functions

- `ScannerRuntimeConfigSource` identifies where a value came from: `Env`, `Config`, `ScannerCompatConfig`, or `Default`.
- `ScannerRuntimeConfig` stores resolved scanner settings: speed, delay, max wait, idle mode, startup delay, cycle interval, bitrot cycle, cycle budget, cache save timeout, scan concurrency, yield cadence, and alert thresholds.
- `ScannerRuntimeConfigError::InvalidValue` reports invalid persisted config with key, value, and reason.
- `ScannerRuntimeConfigValue<T>` and `ScannerRuntimeConfigStatus` expose status with both value and source for each setting.
- Global state:
  - `SCANNER_DEFAULT_CYCLE_SECS: AtomicU64` stores optional deployment-specific default cycle override.
  - `SCANNER_RUNTIME_CONFIG: LazyLock<RwLock<ScannerRuntimeConfig>>` stores the current resolved config.
- Public/crate APIs:
  - `set_scanner_default_cycle_secs`.
  - `lookup_scanner_runtime_config`.
  - `validate_scanner_runtime_config`.
  - `apply_scanner_runtime_config`.
  - `refresh_scanner_runtime_config_from_global`.
  - `current_scanner_runtime_config`.
  - `scanner_runtime_config_status`.
  - Accessors such as `scanner_cycle_interval`, `scanner_start_delay`, `scanner_bitrot_cycle`, `scanner_cache_save_timeout`, concurrency getters, and alert threshold getters.

## Control Flow

Validation first rejects non-default scanner or heal config targets, then validates persisted values independent of environment overrides. This prevents an invalid saved config from being hidden by a valid environment variable.

Resolution follows a consistent precedence pattern. Environment variables win first; persisted scanner config is next; compatibility locations such as scanner bitrot config may be used where supported; defaults and speed-derived values fill the rest. Cycle interval resolution is more nuanced: explicit `RUSTFS_SCANNER_CYCLE` wins, then persisted scanner cycle, then explicit start delay, then deployment default cycle override, then the selected speed preset's cycle interval.

Budget settings interpret zero counts as disabled. Cache save timeout is clamped to at least one second. Bitrot cycle parsing supports immediate deep scan (`0`, `true`, `on`, `yes`), disabled periodic deep scan (`false`, `off`, `no`, `disabled`), or a seconds value.

`apply_scanner_runtime_config` validates persisted config, resolves values, updates `SCANNER_SLEEPER` with delay/max-wait/idle/yield settings, and stores the resolved config behind the RwLock. `refresh_scanner_runtime_config_from_global` repeats that process from the global server config at scanner cycle boundaries.

## State and Persistence Behavior

This module does not persist config itself; it reads `rustfs_config::server_config` values and process environment. The resolved config is cached process-locally in `SCANNER_RUNTIME_CONFIG`. Runtime refreshes can alter sleeper behavior without restarting the scanner. `scanner_runtime_config_status` serializes both values and source tags for observability.

The default cycle override is process-global and is used by `scanner.rs` to apply single-disk defaults. It is stored as an atomic seconds value where zero means no override.

## Dependencies and Integration Points

- Pulls config keys, defaults, and `ScannerSpeed` from `rustfs_config`.
- Updates `sleeper::SCANNER_SLEEPER`, so pacing decisions in scanner traversal observe resolved runtime config.
- Consumes `ScannerCycleBudgetConfig` from `scanner_budget.rs`.
- Used by `scanner.rs` for cycle interval, bitrot cycle, start delay, scan budget, and cache save timeout.
- Used by `data_usage_define.rs` for cache-save timeout.
- Emits structured parse warnings through `tracing`.

## Risks and Edge Cases

- Environment parsing is intentionally more forgiving for some env values than persisted config parsing. For example invalid env delay falls back to the speed-derived delay but still reports source as env; operators need logs/status to notice the fallback.
- `SCANNER_RUNTIME_CONFIG` write failures are silently ignored in `apply_resolved_runtime_config` if the RwLock is poisoned/unavailable; callers receive `Ok` after sleeper update even if cached status is not updated.
- The default cycle override is global mutable process state. Tests use serial execution around environment/default mutations; production code must avoid racing updates except during startup/default configuration.
- Persisted config target validation only allows default targets. Adding per-target scanner config would require explicit design changes here.
- Scanner compatibility config for bitrot is lower precedence than heal config, but still reported distinctly as `scanner_compat_config`; consumers should not assume all config-sourced values are from the same subsystem.

## Test Signals

Tests cover env-over-config precedence, persisted value validation despite env overrides, heal bitrot precedence over scanner compatibility config, source reporting, invalid speed/delay/target rejection, bounded delay parsing, env fallback for excessive delay, cache timeout status, pacing override status, and subsecond max-wait reporting. The tests use `serial_test` and `temp_env`, which signals the global environment/config state is intentionally mutable and must be isolated.
