# sources/object-store/rustfs/crates/object-capacity/Cargo.toml

## Purpose
Package manifest for the RustFS object-capacity crate, which provides capacity scan and refresh core functionality.

## Important APIs, types, and functions
- Package metadata uses workspace version, edition, license, repository, rust version, and homepage.
- Library doctests are disabled.
- Criterion benchmark `capacity_scan` is configured with `harness = false`.
- Dependencies include RustFS config/constants, I/O metrics, utilities, futures, tokio sync/time, tracing, uuid, and walkdir.
- Dev dependencies include criterion, serial_test, temp-env, tempfile, and tokio test-util.

## Control flow
Cargo uses this manifest to compile the library and opt-in benchmark target. There is no application control flow.

## State and persistence behavior
No runtime state. Dependency choices indicate the crate scans filesystem paths, emits metrics/logs, and uses async coordination.

## Dependencies and integration points
The crate integrates with workspace RustFS config and metrics crates and uses `walkdir` for filesystem traversal. The benchmark in `benches/capacity_scan.rs` depends on the bench target declared here.

## Risks and edge cases
Workspace dependency versions/features control behavior; enabling only tokio `sync` and `time` in normal dependencies means code needing filesystem or runtime features must get them elsewhere or under dev features. `harness = false` is required for Criterion benchmarks.

## Test signals
Manifest-level signal is successful cargo metadata/build/bench discovery. No direct tests are defined in this file.
