<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/Cargo.toml -->
# sources/object-store/rustfs/crates/s3select-api/Cargo.toml

## Purpose
Defines the `rustfs-s3select-api` crate package metadata and dependencies for RustFS S3 Select query support.

## Important APIs, types, and functions
The manifest names the crate, inherits workspace package metadata, sets documentation URL, describes S3 Select support, and disables library doctests. Dependencies include query execution, async streaming, object-store integration, S3 protocol types, error handling, and runtime utilities.

## Control flow
Cargo resolves the declared workspace dependencies and compiles modules exported by `src/lib.rs`: `object_store`, `query`, and `server`.

## State and persistence behavior
No runtime state is defined. Dependency selection determines which backends and query engines are available to the S3 Select implementation.

## Dependencies and integration points
Key dependencies include `datafusion`, `object_store`, `rustfs-ecstore`, `s3s`, `tokio`, `tokio-util`, `futures`, `bytes`, `http`, `snafu`, `parking_lot`, `tracing`, `transform-stream`, and `url`. These tie S3 Select SQL parsing/execution to RustFS object data and server streaming.

## Risks and edge cases
This crate has a broad dependency surface. DataFusion version changes can affect error variants, SQL behavior, and planner output. The manifest relies on workspace versions and cannot be evaluated independently from the workspace.

## Test signals
No manifest-local tests exist. `cargo test -p rustfs-s3select-api` would compile this dependency set and run tests in the crate modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/Cargo.toml -->
