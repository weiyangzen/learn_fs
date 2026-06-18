## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/Cargo.toml

Purpose: Rust crate manifest for the external Rust workload sample. It builds a `cdylib` named `rust-workload` so the FoundationDB C workload loader can load it as a dynamic library.

Important settings: package version is `0.1.0`, edition is 2021, library crate type is `cdylib`, and `bindgen 0.72.1` is a build dependency. The manifest has no runtime dependencies, keeping the example focused on generated FFI bindings and local wrapper code.

Control flow and build integration: Cargo invokes `build.rs` before compiling, which generates Rust bindings from `foundationdb/CWorkload.h` into `OUT_DIR`. The Rust source then includes those generated bindings.

State and persistence: no runtime state is defined here; its persistence significance is in producing a dynamic artifact compatible with the simulation workload loader.

Dependencies and integration points: integrates Cargo with FoundationDB's C workload header. The `cdylib` output must match the test configuration in `test_file.toml`, which refers to `libraryName = 'rust_workload'`.

Risks: `bindgen` output is sensitive to header layout, include paths, clang availability, and platform naming conventions for dynamic libraries.

Test signals: successful cargo build signals that the C workload ABI can be bound from Rust for this sample.
