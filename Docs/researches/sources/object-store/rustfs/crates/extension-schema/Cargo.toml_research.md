# sources/object-store/rustfs/crates/extension-schema/Cargo.toml

Purpose: crate manifest for `rustfs-extension-schema`, the shared RustFS extension contract/schema package.

Important declarations: package metadata inherits workspace version, edition, license, repository, rust-version, and homepage. It disables doctests for the library. Runtime dependencies are intentionally minimal: `serde` for stable wire/schema serialization and `thiserror` for typed validation errors. `serde_json` is dev-only for JSON shape tests. Lints are workspace-governed.

State and persistence: no runtime state, but the manifest controls published crate identity, dependency surface, and documentation/test behavior.

Dependencies and integration: this crate is a small boundary contract for extension systems. The manifest keeps it independent of object-store internals, which helps plugins, ops diagnostics, and S3 hook contracts share schemas without pulling storage dependencies.

Risks: disabling doctests can hide stale documentation examples. Any workspace dependency feature changes to `serde` or `thiserror` affect this crate. The manifest has no feature gates, so future optional contract families would need careful dependency discipline.

Test signals: `serde_json` dev dependency supports the stable JSON serialization tests in `src/lib.rs`.
