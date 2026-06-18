# File Research: sources/virtualization/virtiofsd/rustfmt.toml

## Scope

Rust formatting configuration.

## Settings

- `imports_granularity = "Module"` groups imports at module granularity.
- `edition = "2018"` matches the crate manifest.

## Role

Supports the CI `cargo fmt --check` job and keeps import formatting stable across contributors.
