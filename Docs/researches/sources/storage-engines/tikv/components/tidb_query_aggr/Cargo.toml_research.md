# Research: sources/storage-engines/tikv/components/tidb_query_aggr/Cargo.toml

## sources/storage-engines/tikv/components/tidb_query_aggr/Cargo.toml

Purpose: manifest for `tidb_query_aggr`, the vector aggregate-function crate for TiDB pushed-down query execution inside TiKV.

Dependencies include `tidb_query_codegen` for `AggrFunction` derive machinery, `tidb_query_common` results/errors, `tidb_query_datatype` for vector values and field types, `tidb_query_expr` for RPN expression evaluation, `tipb` protobuf expressions, `tikv_util`, and `match-template`. Dev dependencies are `panic_hook` and `tipb_helper` for tests.

Control flow is Cargo-level; the source modules parse aggregate expression definitions, rewrite child expressions as needed, maintain aggregate states, and push vectorized partial results. State/persistence are in in-memory aggregate state structs only.

Risks include tight coupling to TiDB protobuf field-type contracts and codegen macro APIs. Test signals are per-aggregate unit/integration tests that build `tipb` expressions, parse them into aggregate functions, evaluate RPN over lazy columns, and assert vector outputs.
