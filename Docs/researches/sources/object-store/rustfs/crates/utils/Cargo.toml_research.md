# sources/object-store/rustfs/crates/utils/Cargo.toml

Purpose: Cargo manifest for `rustfs-utils`, a feature-gated utility crate used by RustFS components.

Important APIs/config: Package metadata identifies utilities for hashing, compression, and network support. Dependencies are mostly workspace dependencies and optional behind features. Feature sets include `ip` default, `net`, `io`, `path`, `compress`, `string`, `crypto`, `hash`, `os`, `integration`, `http`, `obj`, and `full`.

Control flow/state: Build-time dependency selection only. Target-specific Windows dependency exposes filesystem APIs under `os`.

Integration points: `trusted-proxies` uses env/address utilities from this crate. Other RustFS crates can enable only needed utility surfaces to reduce dependency cost.

Risks and tests: Optional dependencies must stay aligned with source modules; enabling source files without matching features can break builds if module gating is absent elsewhere. Default is only `ip`, so consumers requiring env/crypto/hash/compress must request the proper feature set or rely on a broader workspace feature.
