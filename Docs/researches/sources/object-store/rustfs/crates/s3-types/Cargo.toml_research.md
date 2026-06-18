<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/Cargo.toml -->
# sources/object-store/rustfs/crates/s3-types/Cargo.toml

## Purpose
Defines the `rustfs-s3-types` crate package metadata. The crate owns reusable S3 event type definitions for RustFS.

## Important APIs, types, and functions
The manifest names the crate `rustfs-s3-types`, inherits workspace package metadata and lints, describes the crate as S3 event type definitions, and disables library doctests.

## Control flow
Cargo reads this manifest to compile the event types in `src/event_name.rs` and expose them through `src/lib.rs`.

## State and persistence behavior
No runtime state exists. Package metadata controls workspace builds and crates.io/docs presentation if published.

## Dependencies and integration points
Depends on workspace `serde` and `serde_json` for event serialization/deserialization support. `rustfs-s3-ops` depends on this crate.

## Risks and edge cases
The crate relies on workspace-managed versions. Removing serde dependencies would break the custom serialize/deserialize implementations in `EventName`.

## Test signals
No manifest-local tests exist. `cargo test -p rustfs-s3-types` would validate the event parsing and serde tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/Cargo.toml -->
