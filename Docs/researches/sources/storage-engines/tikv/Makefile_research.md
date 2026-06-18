# sources/storage-engines/tikv/Makefile

## Purpose
The TiKV Makefile wraps Cargo and project scripts for development, testing, static analysis, Docker images, release binaries, and distribution artifacts while injecting TiKV-specific feature and environment policy.

## Important APIs, types, and functions
Major variables include `ENABLE_FEATURES`, `TIKV_FRAME_POINTER`, allocator selectors, `ROCKSDB_SYS_PORTABLE`, `ROCKSDB_SYS_SSE`, `FAIL_POINT`, test-engine selectors, Docker image variables, build metadata exports, `CARGO_TARGET_DIR`, and `DIST_CONFIG`. Important targets include `build`, `release`, `dist_release`, `build_dist_release`, `test`, `test_with_nextest`, `format`, `clippy`, `audit`, `ctl`, `docker`, `docker_test`, `docker_shell`, `error-code`, and `x-build-dist`.

## Control flow
The Makefile computes default features based on OS/architecture and environment. Frame pointers are enabled by default and cause Rust standard library rebuild with nightly `-Z build-std`. Allocator features default to jemalloc, with Linux memory profiling. FIPS switches Dockerfile/tag and enables `gcp_v2/fips`; otherwise `openssl-vendored` is enabled. Build targets call Cargo directly or route distribution builds through `scripts/run-cargo.sh`. Clippy target chains project validation scripts before `scripts/clippy-all`.

## State and persistence behavior
Targets write Cargo target artifacts, `bin/`, `dist/`, Docker images/tags, generated `etc/error_code.toml`, cargo-sort installations, Rustup components/overrides, and possibly compressed/debug-optimized binaries via `dwz`/`objcopy`.

## Dependencies and integration points
It integrates Cargo, Rustup, project scripts, Docker, Python, Linux binary tools, cargo-audit, cargo-sort, cargo-udeps, and platform toolchains. It is the central entry point for CI and developer workflows.

## Risks and edge cases
Default frame-pointer behavior uses nightly-only build-std and can surprise local builds. Feature composition depends on environment variables and platform probes. Some recursive `make` calls do not pass `$(MAKE)`. Docker/release targets assume Linux tools for validation/compression. `cargo search cargo-audit` in `pre-audit` uses network and may be slow or flaky.

## Test signals
`make build`, `make release`, `make dist_release`, `make clippy`, `make test`, `make test_with_nextest`, `make ctl`, and Docker targets are direct signals. Build logs should show expected `TIKV_ENABLE_FEATURES`, frame-pointer flags, allocator selection, and generated binaries.
