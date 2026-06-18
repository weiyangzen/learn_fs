# sources/object-store/rustfs/crates/protocols/src/webdav/mod.rs

Declares the WebDAV protocol module boundary.

Important API surface is limited to module exports: `config`, `driver`, and `server`. There are no local functions or types.

There is no local control flow, state, or persistence. Compile-time module inclusion is controlled by the parent crate feature gate for WebDAV.

Integration is through `lib.rs`, which exposes WebDAV modules and re-exports server/config types when the `webdav` feature is enabled.

Risks are limited to feature/module wiring. Missing re-exports here may require callers to import nested paths, but the module is intentionally thin.

There are no direct tests. Compilation with the `webdav` feature verifies module wiring.
