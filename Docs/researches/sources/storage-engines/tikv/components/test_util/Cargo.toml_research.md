# Research: sources/storage-engines/tikv/components/test_util/Cargo.toml

## sources/storage-engines/tikv/components/test_util/Cargo.toml

Purpose: manifest for the shared `test_util` crate. It is a private Apache-2.0 Rust 2021 package of general testing helpers for TiKV components.

Dependencies cover the helper scope: `backtrace` for CI warmup and leak diagnostics, `chrono`/`slog`/`slog-global`/`time` for test logging, `fail` for failpoint test runners, `grpcio` and `security` for TLS fixtures, `encryption_export`/`kvproto` for encryption helpers, `rand`/`rand_isaac` for data generation, `tempfile`, `tikv_util`, collections, and log redaction wrappers.

Control flow is Cargo-level; source modules provide setup, logging, cert loading, encryption key managers, retry macros, and custom test framework runners. State and persistence are source-managed through temp dirs, env vars, log files, cert files, and failpoint thread locals.

Risks include tight coupling to nightly test framework internals, workspace crate APIs, and generated cert paths. Test signals are broad downstream usage plus benches in `kv_generator` and custom runner integration with Rust's unstable `test` crate.
