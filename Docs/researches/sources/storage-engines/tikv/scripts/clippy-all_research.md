# sources/storage-engines/tikv/scripts/clippy-all

## Purpose
Wrapper that runs the common Clippy policy with broader target coverage and test-oriented features.

## Important Commands and Control Flow
The script re-enters via `make run` unless `MAKEFILE_RUN` is set, honors `SHELL_DEBUG`, then executes `./scripts/clippy --all-targets --features "testexport failpoints"`. Commented sections show older per-package and fuzz clippy strategies but are inactive.

## State, Dependencies, Integration
The wrapper persists no state beyond Cargo artifacts. It depends on `scripts/clippy`, make, Cargo, Clippy, and feature compatibility for `testexport` and `failpoints`.

## Risks and Test Signals
Feature composition depends on how the delegated script's `--features "${TIKV_ENABLE_FEATURES}"` interacts with wrapper-supplied feature arguments. A passing run means all covered targets satisfy the curated Clippy policy under the test/failpoint feature set.
