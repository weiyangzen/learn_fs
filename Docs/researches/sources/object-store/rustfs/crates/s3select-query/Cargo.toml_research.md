# sources/object-store/rustfs/crates/s3select-query/Cargo.toml

## Purpose
This manifest defines the `rustfs-s3select-query` crate, the DataFusion-backed S3 Select query engine implementation for RustFS.

## Important APIs, Types, And Functions
Package metadata identifies the crate, workspace versioning, Rust edition, license, docs URL, keywords, and categories. Dependencies include `rustfs-s3select-api`, `datafusion`, `async-trait`, `async-recursion`, `derive_builder`, `futures`, `parking_lot`, `s3s`, `snafu` with backtraces, `tokio`, and `tracing`. The `[lib]` section disables doctests.

## Control Flow
Cargo uses this file to compile the query engine and its test modules. Workspace dependencies keep versions aligned with the larger RustFS tree.

## State And Persistence Behavior
No runtime state exists in the manifest. Build-time state is derived from workspace dependency resolution.

## Dependencies And Integration Points
The crate depends on the API crate for contracts and on DataFusion for SQL planning/execution. `s3s` supplies Select request DTOs; `tokio` and `futures` support async execution.

## Risks And Edge Cases
Disabling doctests avoids documentation test failures but can hide stale examples. DataFusion version changes are high impact because parser, planner, table-provider, and physical-plan APIs are used directly.

## Test Signals
Cargo will include the unit and integration tests under `src/test` and inline module tests when this crate is tested.
