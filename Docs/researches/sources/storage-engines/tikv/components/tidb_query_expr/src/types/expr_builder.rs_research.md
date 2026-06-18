# sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr_builder.rs

## Purpose
This file converts TiDB protobuf expression trees (`tipb::Expr`) into `RpnExpression` node lists used by the batch expression evaluator. It is the validation and lowering bridge between TiDB request expressions and TiKV's typed RPN runtime. The builder performs supported-expression screening, field-type to `EvalType` checks, postorder traversal, function metadata binding, column-offset validation, and constant decoding.

## Important APIs, Types, and Control Flow
`RpnExpressionBuilder` is a thin `Vec<RpnExpressionNode>` wrapper with production entry points `check_expr_tree_supported`, `is_expr_eval_to_scalar`, and `build_from_expr_tree`. Test-only helpers construct constants, column refs, and function calls directly. `append_rpn_nodes_recursively` is the main lowering routine: scalar functions are handled by `handle_node_fn_call`, column references by `handle_node_column_ref`, and all other supported literal nodes by `handle_node_constant`. Function calls are mapped through `map_expr_node_to_rpn_func`, validated through the macro-generated validator, given optional metadata through `metadata_expr_ptr`, then children are recursively appended before the function node is pushed.

Constant decoding maps protobuf expression types plus `FieldType` into `ScalarValue`: integers, unsigned integers, bytes, reals, MySQL time/duration/decimal/json/enum/bit, nulls, and TiDB vector-float32 values. Time decoding uses `EvalContext` and field decimal precision, while enum/json/vector decoding delegates to datatype codecs.

## State, Dependencies, and Integration
The builder consumes `Expr` values by taking child lists, values, and field types. It does not persist state beyond the produced `RpnExpression`. Its correctness depends on `tidb_query_datatype` codecs, protobuf field metadata, TiDB expression signatures, and the function registry. `max_columns` is a schema-size guard for column refs, not a complete schema validator.

## Risks and Test Signals
Risks center on mismatched `ExprType` and `EvalType`, unchecked casts from unsigned values to signed ints, recursive depth, and stale assumptions in `check_expr_tree_supported` about provided eval types. Tests cover validator behavior for fixed, variadic, and raw variadic functions; postorder conversion; column bounds; and bit literal decoding.
