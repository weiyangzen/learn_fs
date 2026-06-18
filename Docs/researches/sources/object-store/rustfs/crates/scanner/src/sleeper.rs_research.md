# sources/object-store/rustfs/crates/scanner/src/sleeper.rs

## Purpose
Defines scanner throttling for RustFS data scans. It centralizes scanner speed presets, idle-mode enablement, runtime refresh from environment/configuration, proportional work-time backoff, fixed folder-level pacing, yield interval configuration, and metrics reporting for throttle configuration and actual sleeps.

## Important APIs, types, and functions
- `SCANNER_SLEEPER` is a global `LazyLock<DynamicSleeper>` initialized from `RUSTFS_SCANNER_SPEED` and `RUSTFS_SCANNER_IDLE_MODE`; it records throttle config at initialization.
- `SCANNER_IDLE_MODE` is an `AtomicBool` gate that lets runtime configuration skip all scanner sleeps when disabled.
- `DynamicSleeper` wraps shared `SleeperParams` containing a sleep factor and max sleep under `RwLock`s. Clones share the same mutable throttle parameters.
- `DynamicSleeper::sleep_folder()` sleeps for `MIN_SLEEP * factor`, capped by max sleep, for folder-level gaps.
- `DynamicSleeper::timer()` returns a `SleepTimer`; `SleepTimer::sleep()` computes `elapsed_work_time * factor`, clamps it to at least `MIN_SLEEP` and at most max sleep, then sleeps.
- `DynamicSleeper::update`, `refresh_from_env`, and `update_from_runtime_config` update throttle parameters and idle mode, then record metrics.
- `scanner_default_speed`, `set_scanner_default_speed`, `scanner_speed_from_env_or_default`, `scanner_env_config`, and speed-code helpers manage the default speed preset and env parsing.
- `scanner_yield_every_n_objects()` reads `RUSTFS_SCANNER_YIELD_EVERY_N_OBJECTS` with the RustFS default.

## Control flow
At startup, `SCANNER_SLEEPER` reads the configured scanner speed and idle mode, stores idle mode in the global atomic, builds a `DynamicSleeper` using the speed preset's `sleep_factor` and `max_sleep`, and records the throttle config including the current yield interval. Folder scanning calls `sleep_folder` before opening or processing a folder. Object scanning creates a timer before metadata work and calls `SleepTimer::sleep` after work or after handled object-size failures. Both sleep paths first check `SCANNER_IDLE_MODE`, then skip sleep when factor is zero or max sleep is zero.

Runtime reconfiguration can call `refresh_from_env` or `update_from_runtime_config`; both replace the shared factor/max-sleep values so all clones see new pacing. `update_from_runtime_config` also writes idle mode and records the supplied yield interval, making it the bridge from higher-level scanner runtime config into throttle metrics.

## State and persistence behavior
The file has no persistent storage. State is process-local: `SCANNER_DEFAULT_SPEED_PRESET` stores a default speed code, `SCANNER_IDLE_MODE` stores whether sleeping is enabled, and each `DynamicSleeper` stores shared `RwLock`-protected throttle parameters. Sleep durations are reported to `global_metrics().record_scanner_throttle_sleep`, and configuration is reported through `record_scanner_throttle_config`.

## Dependencies and integration points
It depends on `rustfs_config` for speed presets, default idle mode, default yield interval, and environment variable names; `rustfs_utils` for typed env reads; `rustfs_common::metrics::global_metrics`; Tokio time for async sleeps; and standard atomics/locks for low-overhead shared runtime state. `scanner_folder.rs` uses `DynamicSleeper` directly, while `scanner_io.rs` passes the global `SCANNER_SLEEPER` into disk folder scans.

## Risks and edge cases
Because `RwLock` poisoning is recovered through `into_inner`, a panic while updating parameters will not permanently block scans, but it may expose partially updated factor/max-sleep pairs if future edits split updates differently. `SCANNER_IDLE_MODE` is global rather than per-sleeper, so one runtime refresh changes sleep enablement for all scanner users. `SleepTimer::sleep` enforces a minimum 1 ms delay for any nonzero factor, even for very fast operations, while `sleep_folder` can be below or equal to that computed base only after factor multiplication and max-sleep capping. Tests that change environment and global defaults require serialization to avoid cross-test contamination.

## Test signals
Tests cover preset factors and max sleeps for fastest/default/slowest, `update` changing parameters, explicit runtime-config updates applying factor/max/idle mode, env refresh applying speed and idle mode, default-speed override when speed env is unset, fastest mode never sleeping, and idle-mode-off skipping sleep. The tests use `serial_test`, `temp_env`, and Tokio paused time for deterministic global/env behavior.
