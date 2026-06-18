# sources/storage-engines/tikv/components/tikv_alloc/Cargo.toml

## Purpose
This manifest defines the `tikv_alloc` crate, the workspace component responsible for installing and abstracting TiKV's global allocator. It exposes feature-controlled allocator backends and jemalloc profiling support.

## Important APIs, Types, and Control Flow
The primary feature is `jemalloc`, which pulls in `tikv-jemallocator`, `tikv-jemalloc-ctl`, and `tikv-jemalloc-sys`. `mem-profiling` enables jemallocator profiling support. Optional allocator alternatives are `mimalloc`, `snmalloc`, and `tcmalloc`, with tcmalloc built from bundled sources. Dependencies include `fxhash` for memory trace maps, `lazy_static` for jemalloc global maps, and `libc` for FFI.

## State, Dependencies, and Integration
The crate is unpublished and Rust 2021. It participates in workspace linting and explicitly allows the custom `cfg(fuzzing)` in `unexpected_cfgs`. Downstream binaries link to this crate to select the allocator at compile time. Feature combinations are resolved in `src/lib.rs` through cfg-selected `imp` modules.

## Risks and Test Signals
Risks include mutually enabled allocator features creating multiple `imp` modules on Unix, backend-specific platform limits, and profiling functions only working when both Cargo features and runtime jemalloc config are correct. The manifest's dev dependency on `tempfile` supports profiling dump tests.
