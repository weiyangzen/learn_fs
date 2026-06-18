# sources/object-store/rustfs/crates/scanner/src/error.rs

## Purpose

`error.rs` defines the scanner crate's shared error enum. It keeps scanner-specific failures independent from lower-level object-store errors while still allowing standard IO and JSON serialization failures to flow through with `From` conversions.

## Important APIs, Types, and Functions

- `ScannerError` is `#[non_exhaustive]`, `Debug`, and `thiserror::Error`.
- Variants:
  - `Config(String)` for configuration failures.
  - `Io(std::io::Error)` via `#[from]`.
  - `Serialization(serde_json::Error)` via `#[from]`.
  - `Other(String)` for miscellaneous scanner failures.
  - `PartialCache(Box<DataUsageCache>)` for a scan that stopped after producing usable partial data.

## Control Flow

The enum is consumed by scanner routines that return `Result<_, ScannerError>`. `scanner.rs` uses it for the `run_data_scanner` return type, while `scanner_folder.rs` uses `Other`, `Io`, and `PartialCache` during directory traversal and budget/cancellation handling. `PartialCache` is a control-flow-bearing error: callers can inspect the boxed cache and preserve progress instead of treating the scan as a complete failure.

## State and Persistence Behavior

The only state carried directly by this file is the `DataUsageCache` boxed inside `PartialCache`. That cache may include resume markers and checkpoint metadata defined in `data_usage_define.rs`. Persistence is handled by the receiving scanner/cache code, not by the error type.

## Dependencies and Integration Points

- Depends on `thiserror` for display/error implementations.
- Depends on `serde_json` and `std::io` through conversion variants.
- Depends on `crate::data_usage_define::DataUsageCache` for partial scan propagation.
- Re-exported by `lib.rs` as `rustfs_scanner::ScannerError`.

## Risks and Edge Cases

- `Other(String)` is flexible but unstructured; callers cannot reliably match specific scanner failure causes unless a dedicated variant exists.
- `PartialCache` as an error can be mishandled by generic error logging paths, losing useful partial progress unless callers explicitly match it.
- Because the enum is non-exhaustive, downstream crates must include wildcard matches. That is good for forward compatibility but limits exhaustive handling outside the crate.

## Test Signals

This file has no direct unit tests. Behavior is indirectly exercised by `scanner_folder.rs` tests that expect `ScannerError::PartialCache` when budgets interrupt directory scanning, and by scanner paths that convert IO/serialization failures.
