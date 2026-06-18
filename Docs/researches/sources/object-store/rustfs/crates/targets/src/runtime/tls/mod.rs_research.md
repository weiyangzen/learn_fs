## sources/object-store/rustfs/crates/targets/src/runtime/tls/mod.rs

Purpose: is the public module boundary for target TLS hot reload support. It organizes adapter, config, coordinator, fingerprint, metrics, state, trait, and validation helpers and re-exports the main types.

Important APIs/types/functions: re-exports `TlsReloadAdapter`, `TargetTlsReloadCoordinator`, fingerprint types and builder, `init_target_tls_metrics`, runtime state/status types, `ReloadableTargetTls`, and `validate_tls_material`.

Control flow and state: none. The file establishes import ergonomics and crate-facing API shape.

Dependencies and integration points: target implementations can depend on `runtime::tls::*` instead of individual submodules. It bridges target-specific code with shared `rustfs_tls_runtime` config and certificate parsing helpers.

Risks: because it re-exports broad internals, later module refactors can become public API changes. The raw identifier module `r#trait` avoids reserved keyword conflict but may be mildly awkward for direct imports.

Test signals: no local tests; coverage is distributed across submodules.
