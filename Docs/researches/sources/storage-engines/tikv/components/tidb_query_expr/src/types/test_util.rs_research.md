# sources/storage-engines/tikv/components/tidb_query_expr/src/types/test_util.rs

## Purpose
This file provides `RpnFnScalarEvaluator`, a test helper for evaluating one RPN scalar function over scalar constants without constructing full batch columns manually. It is intentionally test-oriented and trades efficiency for ergonomic function tests.

## Important APIs, Types, and Control Flow
`RpnFnScalarEvaluator` accumulates parameters with `RpnExpressionBuilder`, optional return field type, optional `EvalContext`, and optional function metadata. `push_param`, `push_params`, and `push_param_with_field_type` add constant nodes. `return_field_type`, `context`, and `metadata` configure evaluation. `evaluate_raw` builds child expression descriptors from accumulated RPN nodes, constructs a scalar-function expression with a requested `ScalarFuncSig`, maps it through the real function registry, validates arguments, prepares metadata if not provided, pushes the function call, evaluates one output row, and returns the first scalar result plus the final context. `evaluate<T>` infers the return field type from `EvaluableRet` and converts `ScalarValue` into `Option<T>`.

## State, Dependencies, and Integration
The helper uses production `RpnExpressionBuilder`, `map_expr_node_to_rpn_func`, and `expr.eval`, so tests exercise the same validator, metadata, and function-pointer path as real evaluation. It integrates with `LazyBatchColumnVec::empty` because all inputs are scalar constants.

## Risks and Test Signals
The helper builds synthetic protobuf child descriptors, so it can miss issues that depend on real column refs, lazy decoding, or logical rows. It also deliberately ignores previously configured `return_field_type` in `evaluate_raw`. Its value is high for scalar function unit tests because validation failures and context mutations are surfaced directly.
