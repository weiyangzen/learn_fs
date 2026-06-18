# sources/storage-engines/tikv/components/tidb_query_codegen/src/lib.rs

Purpose: exports procedural macros for TiDB query components: `AggrFunction` derive and `rpn_fn` attribute. It is the public proc-macro entry point for code generation used by aggregate and scalar expression implementations.

Important APIs and control flow: `aggr_function_derive` parses a `DeriveInput`, converts it through `AggrFunctionOpts::from_derive_input`, and returns generated tokens or panics on validation error. `rpn_fn` passes attribute and function tokens to `rpn_function::transform`, returning either generated tokens or a compile-error token stream.

State and persistence behavior: compile-time only; it emits Rust code and keeps no runtime state.

Dependencies and integration: enables nightly proc-macro diagnostics, iterator ordering, and a higher recursion limit for large generated expressions. It depends on internal `aggr_function` and `rpn_function` modules.

Risks and test signals: derive path panics rather than emitting structured compile errors, whereas `rpn_fn` returns compile errors. Any public macro behavior change has broad downstream compile impact.
