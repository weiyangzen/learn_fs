# sources/storage-engines/raft-engine/Makefile

## Purpose
Provides standard developer and CI entry points for formatting, linting, testing, coverage matrix execution, cleanup, and building the control binary.

## Important APIs, Types, And Functions
Targets are `all`, `clean`, `format`, `clippy`, `test`, `test_matrix`, and `ctl`. Important variables are `EXTRA_CARGO_ARGS`, `WITH_STABLE_TOOLCHAIN`, `WITH_NIGHTLY_FEATURES`, `TOOLCHAIN_ARGS`, `BIN_PATH`, `CARGO_TARGET_DIR`, and exported `RUST_LOG=info`.

## Control Flow
The Makefile detects whether nightly features should be enabled from `WITH_STABLE_TOOLCHAIN` and current rustc version. Stable forced mode uses `+stable` and disables nightly feature groups. Nightly-capable mode runs clippy and tests with `nightly_group` and failpoints, while stable mode uses failpoints only. `test_matrix` requires nightly feature mode and runs additional default/failpoints/std_fs combinations.

## State And Persistence Behavior
The file only affects local build artifacts: `target/`, `bin/`, coverage inputs through test execution, and compiled `raft-engine-ctl`. It does not mutate engine data except temporary test directories created by tests.

## Dependencies And Integration Points
CI calls this Makefile directly. Cargo feature flags from `Cargo.toml`, failpoints tests, clippy lint configuration, and the `ctl` workspace package all integrate here.

## Risks And Edge Cases
Toolchain auto-detection can surprise users with nightly-only features if their default toolchain is nightly. `test_matrix` hard-errors under stable mode. The clippy whitelist only allows `bool_assert_comparison`, so new lints may break CI after toolchain updates.

## Test Signals
Successful `make all`, `make test`, `make test_matrix`, and `make ctl` are the primary signals. CI uses these targets as authoritative validation.
