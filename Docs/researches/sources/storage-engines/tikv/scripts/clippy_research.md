# sources/storage-engines/tikv/scripts/clippy

## Purpose
Runs TiKV's curated Clippy policy for the workspace under the Makefile environment. It centralizes which lints are allowed, warned, or denied.

## Important Settings and Control Flow
The script re-enters via `make run` unless `MAKEFILE_RUN` is set and supports `SHELL_DEBUG`. It builds a `CLIPPY_LINTS` array that allows known noisy lints, warns on `dbg_macro` and `todo`, denies policy lints such as `upper_case_acronyms`, `disallowed_methods`, `rust-2018-idioms`, and denies several async-quality lints. It runs `cargo clippy --workspace`, excludes fuzz crates, uses `--no-default-features --features "${TIKV_ENABLE_FEATURES}"`, forwards user args, and appends lints after `--`.

## State, Dependencies, Integration
No custom state is persisted, though Cargo target artifacts may be written. Dependencies are bash, make, Cargo, Clippy, the pinned Rust toolchain, and `TIKV_ENABLE_FEATURES` from Makefile setup. `scripts/clippy-all` delegates to it.

## Risks and Test Signals
Lint names and behavior depend on the nightly toolchain. Under `set -u`, the Makefile environment must define `TIKV_ENABLE_FEATURES`. Passing clippy is the main signal; deliberate `dbg!`, `todo!`, or denied async patterns should fail.
