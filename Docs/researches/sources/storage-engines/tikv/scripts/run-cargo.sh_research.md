# sources/storage-engines/tikv/scripts/run-cargo.sh

## Purpose
Runs Cargo with environment-driven experimental build options for Makefile `x-` targets. It manages temporary Cargo config, feature selection, release/debug mode, Rust flags, package selection, and optional frame-pointer builds.

## Important Variables and Control Flow
`X_CARGO_CMD` is required. Optional inputs include `X_CARGO_FEATURES`, `X_CARGO_RELEASE`, `X_CARGO_CONFIG_FILE`, `X_RUSTFLAGS`, `X_DEBUG`, `X_PACKAGE`, `X_CARGO_ARGS`, `TIKV_FRAME_POINTER`, `TIKV_BUILD_RUSTC_TARGET`, and `X_CARGO_TARGET_DIR`. The script removes existing `.cargo/config`, assembles cargo args with `--no-default-features`, copies a temporary config if requested, exports custom flags/debug profile variables, builds package args, adds nightly `-Z build-std` options for frame pointers, runs cargo with tracing, captures the exit code, cleans `.cargo/config`, removes empty `.cargo`, and exits with the original cargo status.

## State, Dependencies, Integration
It deliberately mutates `.cargo/config` during a run and writes normal Cargo artifacts. It may install `rust-src` for frame-pointer builds. Dependencies are bash, Cargo, rustup, nightly Cargo for `-Z` flags, and Makefile callers that set `X_` variables.

## Risks and Test Signals
Pre-existing `.cargo/config` is removed rather than preserved, so repo-local config must be disposable. String-based argument assembly is sensitive to spaces. Frame-pointer builds require valid target/out-dir variables. Test with minimal checks, temporary config files, cargo failures, and frame-pointer paths to ensure cleanup and exit-code preservation.
