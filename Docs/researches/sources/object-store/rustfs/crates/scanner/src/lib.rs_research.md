# sources/object-store/rustfs/crates/scanner/src/lib.rs

## Purpose

`lib.rs` is the scanner crate root. It declares scanner submodules, exposes the public API surface used by other RustFS crates, and tracks coarse scanner activity with an atomic work-unit counter.

## Important APIs, Types, and Functions

- Module declarations:
  - Public modules: `data_usage_define`, `error`, `runtime_config`, `scanner`, `scanner_budget`, `scanner_folder`, `scanner_io`, and `sleeper`.
- Re-exports:
  - All public items from `data_usage_define`.
  - `ScannerError`.
  - Runtime config entry points: `apply_scanner_runtime_config`, `scanner_runtime_config_status`, and `validate_scanner_runtime_config`.
  - `rustfs_common::last_minute`.
  - `scanner::init_data_scanner`.
  - `DynamicSleeper`, `SCANNER_IDLE_MODE`, and `SCANNER_SLEEPER`.
- Activity tracking:
  - `current_scanner_activity() -> u64` reads `SCANNER_ACTIVE_WORK_UNITS`.
  - `ScannerActivityGuard::new()` increments the counter.
  - `Drop for ScannerActivityGuard` decrements with saturating behavior through `fetch_update`.

## Control Flow

Other crates initialize background scanner work through the re-exported `init_data_scanner`. Runtime configuration is validated/applied through re-exported functions from `runtime_config.rs`. Internal scanner tasks create `ScannerActivityGuard` values around active work; when guards drop, the global counter is decremented. This gives observers a simple measure of active scanner work without coupling to individual task implementations.

## State and Persistence Behavior

The only crate-root state is `SCANNER_ACTIVE_WORK_UNITS: AtomicU64`. It is process-local, relaxed-ordering telemetry and is not persisted. Persistence of scanner cycles, background heal state, and data-usage snapshots is delegated to `scanner.rs` and `data_usage_define.rs`.

## Dependencies and Integration Points

- Provides the public namespace for scanner consumers, including integration tests that import `rustfs_scanner::scanner::init_data_scanner`.
- Integrates with `runtime_config`, `sleeper`, and data-usage definitions by re-exporting their stable entry points.
- `ScannerActivityGuard` is used in `scanner.rs` around scan cycles and backend data-usage saving.

## Risks and Edge Cases

- `ScannerActivityGuard` is crate-private, so external consumers can observe but not mark scanner work. That keeps the counter scoped but means all internal work sites must remember to use the guard.
- Relaxed atomic ordering is suitable for approximate telemetry but not for synchronization decisions.
- The crate has `unreachable_pub` warnings enabled; exported module contents should be intentional because public module declarations can expose more than the curated re-export list.

## Test Signals

There are no direct tests in `lib.rs`. Activity behavior is indirectly covered when scanner tests run guarded operations, but there is no explicit test asserting `current_scanner_activity` increments/decrements.
