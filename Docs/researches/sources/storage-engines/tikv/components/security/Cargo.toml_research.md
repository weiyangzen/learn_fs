## sources/storage-engines/tikv/components/security/Cargo.toml

Purpose: package manifest for the `security` component crate.

Important APIs/types/functions: declares package name `security`, edition 2021, Apache-2.0 license, non-publishable. Dependencies include collections, encryption, grpcio, log wrappers, online config, serde/serde_derive, slog, slog-global, and tikv_util; dev dependency is tempfile.

Control flow: no runtime control flow; it controls crate compilation and feature availability.

State/persistence: no direct state. The dependency graph enables TLS certificate loading, online config handling, and encryption config embedding in `SecurityConfig`.

Dependencies/integration: consumed by server and PD/grpc clients. `grpcio` is central for channel/server credential builders and peer auth checks; `online_config` enables runtime redaction config changes.

Risks: because versions are mostly workspace-managed, security behavior tracks workspace dependency updates. No crate features are declared here, so optional behavior must come from dependencies or config.

Test signals: `tempfile` supports file-based certificate/config tests in `src/lib.rs`.
