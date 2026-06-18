# sources/storage-engines/tikv/.github/workflows/tikv-clippy-darwin.yml

## Purpose
This GitHub Actions workflow runs TiKV's clippy checks on macOS Intel and Apple Silicon pull requests.

## Important APIs, types, and functions
The workflow is named `Clippy (Darwin)`. It triggers on pull requests to `master` and `feature/**`, ignoring documentation/image and selected metadata-only changes. It defines `CMAKE_VERSION=3.28.0` and `GO_VERSION=1.25.7`, uses `actions/checkout@v4`, `actions/cache@v4`, and `dtolnay/rust-toolchain@stable` with `nightly-2025-02-28` plus rustfmt, clippy, rust-src, and rust-analyzer.

## Control flow
The job matrix runs on `macos-15-intel` for amd64 and `macos-15` for arm64. Steps install architecture-specific Go, install universal CMake under `/usr/local`, set Rust nightly components, cache Cargo registry/git/target by `Cargo.lock`, then run `make clippy`.

## State and persistence behavior
State is CI workspace files and cache entries. The job modifies `/usr/local/go`, installs CMake symlinks, and writes environment/GitHub path variables for later steps.

## Dependencies and integration points
It depends on GitHub-hosted macOS runners, network access to Go and CMake release artifacts, Rustup, Cargo, and TiKV's Makefile/scripts clippy pipeline.

## Risks and edge cases
Manual installation of Go and CMake can break if download URLs or runner permissions change. Cache includes `target/`, which can be large or stale across toolchain changes. The workflow is pull-request path-filtered, so ignored-file-only changes skip clippy.

## Test signals
Successful matrix completion, correct `go version` and `cmake --version`, Rust nightly availability, cache restore/save behavior, and `make clippy` success are the main signals.
