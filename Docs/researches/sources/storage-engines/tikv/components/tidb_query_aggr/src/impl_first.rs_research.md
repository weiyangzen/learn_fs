# sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_first.rs

Purpose: implements TiDB pushed-down `FIRST` aggregation for the batch aggregate executor. The parser validates a single child expression, verifies the output field type matches the child expression evaluation type, appends one output schema column and one RPN expression, then selects a typed `AggrFnFirst<T>` implementation for scalar, bytes-like, JSON, enum/set, and vector-float values.

Important APIs and control flow: `AggrFnDefinitionParserFirst` implements `AggrDefinitionParser::check_supported` and `parse_rpn`. `AggrFnFirst<T>` derives `AggrFunction`, whose generated `create_state` returns `AggrFnStateFirst<T>`. The state is `Empty` until the first logical row is observed, then becomes `Valued(Option<T::EvaluableType>)`, preserving `NULL` if the first row is null. `update_repeat` ignores repeat count after asserting it is nonzero; `update_vector` looks only at the first logical row and delegates to `update`.

State and persistence behavior: state is in-memory and per aggregate group; there is no durable persistence. `push_result` emits exactly one column and clones the captured owned value. The first value is never replaced, so correctness depends on caller row order matching TiDB aggregation semantics.

Dependencies and integration: uses `tidb_query_codegen::AggrFunction`, `tidb_query_datatype` evaluable refs and `VectorValue`, `tidb_query_expr::RpnExpression`, and `tipb::ExprType::First`. It integrates through `parser.rs` dispatch and the generic update macros in `lib.rs`.

Risks and test signals: unsupported or mismatched output types fail in parsing; mismatched runtime update types panic through the aggregate-state trait layer. A TODO notes cloning could be avoided. Tests cover empty output, first-null behavior, enum/set ownership, repeated update, vector logical-row ordering, and illegal return-type requests.
