<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/Cargo.toml -->
# sources/object-store/rustfs/crates/credentials/Cargo.toml

## Purpose
Declares the `rustfs-credentials` crate metadata, dependencies, and workspace lint inheritance.

## Important APIs, types, and functions
The package describes credential management utilities for authentication/authorization. Dependencies include `base64-simd`, `hmac`, `rand`, `serde`, `serde_json`, `sha2`, and `time` with serde/parsing/formatting/macros features.

## Control flow
Cargo uses this manifest to compile the credentials crate and expose its library with workspace edition/version/license/rust-version settings.

## State and persistence behavior
No runtime state. Dependency and feature choices affect binary composition and serialization/parsing support.

## Dependencies and integration points
Integrates with the workspace dependency versions and crates that import credential generation, global credentials, RPC secret, and serde helpers.

## Risks and edge cases
Security behavior depends on cryptographic dependency versions. The manifest has no feature gates, so all listed dependencies are always included.

## Test signals
Build, cargo metadata, and crate tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/Cargo.toml -->
