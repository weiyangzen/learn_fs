<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-ops/Cargo.toml -->
# sources/object-store/rustfs/crates/s3-ops/Cargo.toml

## Purpose
Defines the `rustfs-s3-ops` crate package metadata. The crate is a small data-structure/library crate for S3 operation enums and event mapping.

## Important APIs, types, and functions
The manifest names the crate `rustfs-s3-ops`, uses workspace version, edition, license, repository, rust-version, and homepage settings, and describes the crate as "S3 operation enum and event mapping for RustFS." It declares keywords/categories and disables doctests for the library target.

## Control flow
Cargo uses this file to resolve the crate and its single dependency before compiling `src/lib.rs`.

## State and persistence behavior
No runtime state exists. The manifest participates in workspace dependency resolution and package publication metadata.

## Dependencies and integration points
The only crate dependency is `rustfs-s3-types` from the workspace, which supplies `EventName`. Lints are inherited from the workspace.

## Risks and edge cases
Because the crate is intentionally narrow, adding operation mappings that need serialization or parsing would require updating dependencies and possibly enabling doctests. The manifest relies on workspace keys, so it cannot be built standalone without the workspace context.

## Test signals
No manifest-specific tests exist. `cargo test -p rustfs-s3-ops` would compile this manifest and run the mapping tests in `src/lib.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-ops/Cargo.toml -->
