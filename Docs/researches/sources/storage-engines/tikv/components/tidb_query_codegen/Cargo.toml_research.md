# sources/storage-engines/tikv/components/tidb_query_codegen/Cargo.toml

Purpose: declares `tidb_query_codegen`, a non-published Rust 2021 procedural macro crate used by TiDB query components.

Important APIs and control flow: marks the library as `proc-macro = true`. Dependencies include `darling` for derive/attribute parsing, `syn` with full AST support, `quote` and `proc-macro2` for generated tokens, and `heck` for identifier case conversion.

State and persistence behavior: no runtime state; build-time macro crate configuration only.

Dependencies and integration: consumed by aggregate and expression crates through `#[derive(AggrFunction)]` and `#[rpn_fn]`. Workspace-managed dependencies reduce version drift for shared crates.

Risks and test signals: uses nightly-only features in source, so compiler/toolchain compatibility matters. Macro expansion failures surface at compile time in downstream crates.
