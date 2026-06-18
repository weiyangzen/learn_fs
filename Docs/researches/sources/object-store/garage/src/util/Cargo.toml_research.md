<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/Cargo.toml -->
# sources/object-store/garage/src/util/Cargo.toml

## Purpose
Cargo manifest for the `garage_util` crate, the shared utility layer used by Garage crates for configuration, CRDTs, serialization, errors, metrics, background workers, persistence, time, and version metadata.

## Important APIs, types, and functions
The manifest declares `lib.rs`, workspace dependencies on `garage_db` and `garage_net`, serialization/hash/time/async/HTTP/OpenTelemetry crates, build dependency `rustc_version`, and features `k2v` and optional `arbitrary` support.

## Control flow
Cargo uses the build script to inject `RUSTC_VERSION`; crate modules are exposed by `lib.rs`. Feature selection controls whether arbitrary generators for CRDT fuzzing are compiled.

## State and persistence behavior
No runtime state, but dependency and feature choices define which persistence, migration, and test/fuzz helpers are available to the compiled utility crate.

## Dependencies and integration points
This manifest is consumed by most Garage workspace crates. Version skew in `serde`, `rmp-serde`, `tokio`, `hyper`, and OpenTelemetry can affect public utility APIs across the repository.

## Risks and test signals
Optional `arbitrary` must stay synchronized with CRDT modules that gate `Arbitrary` impls. Build/test signals are workspace `cargo check`, feature builds with `--features arbitrary`, and utility crate unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/Cargo.toml -->
