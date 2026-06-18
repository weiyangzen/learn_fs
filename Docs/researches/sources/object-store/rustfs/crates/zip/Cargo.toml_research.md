# sources/object-store/rustfs/crates/zip/Cargo.toml

## Purpose
Defines the `rustfs-zip` crate package metadata, dependencies, benchmark target, and Linux-specific dependency feature extension.

## Important APIs, Types, And Functions
Package metadata uses workspace edition/license/repository/rust-version/version/homepage, documents the crate as ZIP handling for RustFS, and disables doctests for the library. The `zip_benchmark` Criterion bench is registered with `harness = false`. Runtime dependencies are `async-compression` with Tokio and bzip2/gzip/zlib/zstd/xz features, `tokio` with fs/io-util/macros, `tokio-stream`, `astral-tokio-tar`, `thiserror`, and `zip`. Dev dependencies are `criterion` with HTML reports and `tempfile`. On Linux, Tokio also enables `io-uring`.

## Control Flow And State
No runtime control flow. Cargo feature resolution controls available compression formats and Linux async IO behavior.

## Dependencies And Integration Points
This manifest ties the zip crate to the workspace dependency versions and lint policy. The benchmark file in `benches/zip_benchmark.rs` depends on the bench declaration and dev dependencies here.

## Risks And Test Signals
Linux target-specific Tokio feature unification can affect behavior or dependency graph only on Linux. Broad compression feature enablement increases build surface. Benchmark presence is the main performance signal; tests are in other crate sources not part of this work item.
