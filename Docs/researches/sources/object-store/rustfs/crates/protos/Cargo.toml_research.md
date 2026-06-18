# sources/object-store/rustfs/crates/protos/Cargo.toml

## Purpose

This manifest defines the `rustfs-protos` crate, whose description says it provides gRPC and FlatBuffers protocol interfaces for communication between RustFS components. It also declares a `gproto` binary at `src/main.rs`, likely used for protocol generation or inspection.

## Important APIs, types, and functions

- Package metadata uses workspace-managed `version`, `edition`, `license`, `repository`, `rust-version`, and `homepage`.
- `documentation` points to the docs.rs page for `rustfs-protos`.
- The crate opts into workspace lints with `[lints] workspace = true`.
- `[[bin]] name = "gproto"` maps to `src/main.rs`.
- `[lib] doctest = false` disables doctests for the library, which is common for generated protocol crates.
- Dependencies include internal crates `rustfs-common`, `rustfs-io-metrics`, `rustfs-config`, `rustfs-tls-runtime`, and `rustfs-utils`.
- Protocol/generation dependencies include `flatbuffers`, `prost`, `tonic`, `tonic-prost`, and `tonic-prost-build`.
- `tonic` enables `transport`, `tls-native-roots`, and `tls-aws-lc`; `tokio` enables only `sync`.

## Control flow

The manifest does not contain runtime control flow. Build-time behavior is determined by Cargo: it compiles the library, includes the `gproto` binary, links generated FlatBuffers and Prost/Tonic modules, and applies workspace dependency versions and lint settings.

## State and persistence behavior

There is no runtime state in the manifest. Persistent build behavior comes from Cargo metadata and workspace dependency resolution. The choice to include code-generation/build crates as normal dependencies means downstream builds may compile generation support even when only consuming generated modules.

## Dependencies and integration points

This crate sits between protocol schema files (`models.fbs`, `node.proto`), generated Rust modules under `src/generated`, and RustFS components needing typed gRPC or FlatBuffers messages. TLS-enabled `tonic` settings indicate that generated gRPC clients/servers can use secure transport with native roots and AWS-LC TLS support. Internal RustFS dependencies suggest protocol messages are not isolated DTOs only; the crate may also provide service wiring, metrics, config, TLS runtime integration, or utility support.

## Risks and edge cases

- Generated modules often produce clippy warnings; the source modules suppress those locally, but workspace lints can still affect hand-written code.
- Disabling doctests prevents generated examples from breaking builds but also reduces documentation verification.
- `tonic-prost-build` as a regular dependency can increase compile surface if it is only needed by the binary or build tooling.
- TLS feature selection couples protocol transport behavior to native roots and AWS-LC availability.
- Consumers must be aware that generated sources should not be manually edited.

## Test signals

The manifest itself has no tests. Useful validation signals are `cargo check -p rustfs-protos`, `cargo test -p rustfs-protos`, and any regeneration command through `gproto` that confirms generated gRPC and FlatBuffers outputs remain compatible with `prost`, `tonic`, and `flatbuffers`.
