# sources/object-store/garage/src/k2v-client/Cargo.toml

Purpose: This manifest defines the `k2v-client` crate, a Rust library and optional CLI for Garage's K2V protocol.

Important APIs and types: Package metadata sets name `k2v-client`, version `0.0.4`, AGPL license, repository, and readme. The library path is `lib.rs`; binary `k2v-cli` uses `bin/k2v-cli.rs` and requires feature `cli`. Feature `cli` enables `clap`, `tokio/fs`, `tokio/io-std`, `tracing-subscriber`, and `format_table`.

Control flow: Cargo uses this manifest to resolve workspace dependencies and feature-gated binary compilation. Without `cli`, only the library and its non-CLI dependencies are built.

State and persistence behavior: The manifest itself has no runtime state. It controls which dependencies and code paths are available, including filesystem/stdin support for the CLI feature.

Dependencies and integration points: Core dependencies include base64, sha2, hex, http, http-body-util, log, aws-sigv4, aws-sdk-config, percent-encoding, hyper/hyper-util/hyper-rustls, serde, serde_json, thiserror, and tokio. It inherits workspace lint settings.

Risks: The crate uses edition 2018 while the wider workspace may contain newer editions. CLI behavior is absent unless the feature is selected. Dependency versions are workspace-controlled, so API changes in shared dependencies can affect both library and CLI.

Test signals: The Garage integration tests under `tests/k2v_client` compile and exercise the library when the `k2v` feature is enabled; CLI-specific code has no direct test in this group.
