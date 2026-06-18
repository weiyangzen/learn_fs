# sources/storage-engines/tikv/components/tidb_query_codegen/src/aggr_function.rs

Purpose: implements the derive macro backend for aggregate function structs. It generates the boilerplate `crate::AggrFunction` implementation from a `#[aggr_function(state = expr)]` attribute.

Important APIs and control flow: `AggrFunctionStateExpr` parses `state = <expr>`. `AggrFunctionOpts` captures the deriving type's ident, generics, and forwarded `aggr_function` attributes. `generate_tokens` parses the first attribute, turns the struct name into the `name()` string, preserves generics/where clauses, and emits `create_state` returning `Box::new(state_expr)`.

State and persistence behavior: no runtime state beyond generated aggregate state creation. The supplied state expression controls actual aggregate state initialization.

Dependencies and integration: uses `darling::FromDeriveInput`, `syn`, and `quote`. Concrete aggregate structs in `tidb_query_aggr` derive this macro.

Risks and test signals: missing or malformed `#[aggr_function]` attributes panic during macro expansion. It assumes the target crate has `crate::AggrFunction` and `crate::AggrFunctionState` in scope. Coverage is mainly compile-time through downstream aggregate modules.
