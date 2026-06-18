<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/build.rs -->
# sources/object-store/garage/src/util/build.rs

## Purpose
Cargo build script for `garage_util`; records the Rust compiler version used for the build.

## Important APIs, types, and functions
`main` calls `rustc_version::version` and emits `cargo:rustc-env=RUSTC_VERSION=...`.

## Control flow
Cargo runs the script before compiling the crate. The emitted environment variable is later read by `version.rs` through `env!`.

## State and persistence behavior
No persistent application state. The build output embeds compiler version metadata into the binary.

## Dependencies and integration points
Integrates Cargo build-script protocol, `rustc_version`, and Garage build info metrics/version reporting.

## Risks and test signals
`unwrap` means build fails if rustc version cannot be queried. Build success and `garage_util::version::rust_version()` returning a non-empty string are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/build.rs -->
