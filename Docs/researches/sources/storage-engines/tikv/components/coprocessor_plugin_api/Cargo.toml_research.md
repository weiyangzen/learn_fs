# sources/storage-engines/tikv/components/coprocessor_plugin_api/Cargo.toml

Purpose: manifest for the `coprocessor_plugin_api` crate, which defines the ABI-facing traits and helper macros for custom TiKV coprocessor plugins.

Important APIs and types: package metadata, runtime dependencies `async-trait` and `atomic`, build dependency `rustc_version`.

Control flow: no runtime control flow. Build-time behavior comes from `build.rs`, which injects API version, target triple, and rustc version for plugin compatibility checks.

State and persistence: none directly.

Dependencies and integration: `async-trait` supports async storage trait methods without requiring `Send`; `atomic` stores allocator function pointers. The crate is unpublished and intended for workspace/internal plugin loading.

Risks: ABI compatibility is sensitive to dependency versions and Rust compiler behavior, especially because exported functions return Rust structs and trait-object pointers across dynamic library boundaries. The manifest’s version is used as `API_VERSION`.

Test signals: build script and allocator unit tests are the main direct validation paths.
