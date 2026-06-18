# sources/storage-engines/tikv/components/tidb_query_aggr/src/util.rs

Purpose: shared aggregate parser utilities for arity validation and expression rewriting. It centralizes child-expression support checks and cast insertion for numeric and bit-operation aggregate families.

Important APIs and control flow: `check_aggr_exp_supported_one_child` requires exactly one child and delegates child expression validation to `RpnExpressionBuilder::check_expr_tree_supported`. `rewrite_exp_for_sum_avg` inspects the RPN return type and appends a cast node when SUM/AVG/VARIANCE require decimal or real output: ints become decimal except MySQL BIT becomes double; non numeric-ish values become double. `rewrite_exp_for_bit_op` casts non-int inputs to `LongLong`.

State and persistence behavior: no state is kept. The functions mutate `RpnExpression` by pushing cast nodes.

Dependencies and integration: uses `FieldTypeAccessor`, `FieldTypeBuilder`, `FieldTypeTp`, `EvalType`, and `get_cast_fn_rpn_node` from query expression code. It is called by aggregate parsers before schema and implementation selection.

Risks and test signals: rewrite correctness must match TiDB type inference (`typeInfer4Sum`, `typeInfer4Avg`) or parser output schemas will reject requests. Cast insertion relies on `exp.is_last_constant()` and original field type metadata. Tests are indirect through SUM, variance, and bit-op integration tests.
