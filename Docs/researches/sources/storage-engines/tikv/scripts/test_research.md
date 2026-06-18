# sources/storage-engines/tikv/scripts/test

## Purpose
Runs TiKV workspace tests under the common Makefile environment, centralizing feature handling, Docker-specific behavior, library paths, logging, backtraces, and workspace exclusions.

## Important Variables and Control Flow
The script re-enters through `make run` unless `MAKEFILE_RUN` is set and honors `SHELL_DEBUG`. It defaults `CUSTOM_TEST_COMMAND` to `test`, sets empty defaults for `DYLD_LIBRARY_PATH`, `LOCAL_DIR`, `TIKV_ENABLE_FEATURES`, and `EXTRA_CARGO_ARGS`, appends `docker_test` inside Docker, exports `DYLD_LIBRARY_PATH`, `LOG_LEVEL=DEBUG`, and `RUST_BACKTRACE=full`, then runs `cargo $CUSTOM_TEST_COMMAND --workspace` excluding fuzz crates and enabling `${TIKV_ENABLE_FEATURES}`.

## State, Dependencies, Integration
The script persists no state beyond Cargo/test artifacts. Dependencies are bash, make, Cargo, the Makefile `run` target, feature naming, and workspace package layout. `scripts/test-all` builds on it.

## Risks and Test Signals
Empty or incompatible feature strings can change Cargo behavior. macOS library path behavior depends on `LOCAL_DIR`; Docker detection relies on `/.dockerenv`. Signals include successful `./scripts/test --no-run`, Docker runs that include `docker_test`, and correct exit status propagation from Cargo.
