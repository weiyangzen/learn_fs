<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/version.rs -->
# sources/object-store/garage/src/util/version.rs

## Purpose
Global runtime accessors for Garage version, optional feature list, and embedded Rust compiler version.

## Important APIs, types, and functions
Uses `ArcSwapOption` statics `VERSION` and `FEATURES`. Functions are `garage_version`, `garage_features`, `init_version`, `init_features`, and `rust_version`.

## Control flow
Startup calls init functions to store static references. Accessors load the swapped Arcs and return static data; `rust_version` reads the build-script environment variable.

## State and persistence behavior
State is process-global and in-memory. It feeds metrics/build info and diagnostics, not persistent application data.

## Dependencies and integration points
Depends on `arc-swap`, `lazy_static`, and the `RUSTC_VERSION` build env from `build.rs`.

## Risks and test signals
`garage_version` unwraps and will panic before initialization. Tests should initialize values before access and verify feature optionality.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/version.rs -->
