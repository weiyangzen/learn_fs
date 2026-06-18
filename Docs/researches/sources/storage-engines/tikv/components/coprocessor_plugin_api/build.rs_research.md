# sources/storage-engines/tikv/components/coprocessor_plugin_api/build.rs

Purpose: emits compile-time environment variables used by plugin build information.

Important APIs and types: single `main` function that prints `cargo:rustc-env=API_VERSION`, `TARGET`, and `RUSTC_VERSION`.

Control flow: Cargo executes the build script before compiling the crate. It reads `CARGO_PKG_VERSION` through `env!`, reads `TARGET` from the environment, asks `rustc_version::version_meta()` for the short compiler version, and writes the values for use by `BuildInfo::get`.

State and persistence: no repo state. It affects compiler environment for the current build.

Dependencies and integration: integrates with `util::BuildInfo`, plugin loading compatibility checks, Cargo build-script protocol, and the `rustc_version` crate.

Risks: `std::env::var("TARGET").unwrap()` and `version_meta().unwrap()` panic if Cargo/rustc metadata is unavailable, which is acceptable under normal Cargo builds but brittle in unusual build systems.

Test signals: successful crate build validates the script. There are no direct unit tests.
