# sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr.rs

## Purpose

`types/expr.rs` defines the in-memory Reverse Polish Notation expression representation used by `tidb_query_expr`. It provides node variants for function calls, constants, and column references, plus a thin `RpnExpression` wrapper around a vector of nodes. Expression evaluation itself lives elsewhere (`expr_eval`), but this file defines the core shape that builders, evaluators, and tests share.

## Important APIs, types, and functions

`RpnExpressionNode` has three variants:

- `FnCall { func_meta, args_len, field_type, metadata }` represents a scalar function invocation. `func_meta` is the generated/executable `RpnFnMeta`, `args_len` describes stack arity, `field_type` stores the return type, and `metadata: Box<dyn Any + Send>` stores function-specific metadata such as parsed interval units.
- `Constant { value, field_type }` stores a scalar value and its TiDB field type.
- `ColumnRef { offset }` references a column by schema/evaluation offset.

Test-only helpers expose internals for assertions: `field_type`, `expr_tp`, `fn_call_func`, and `constant_value`. `expr_tp` maps stored `ScalarValue` eval types back to protobuf `ExprType`, including newer `VectorFloat32` as `TiDbVectorFloat32`.

`RpnExpression(Vec<RpnExpressionNode>)` implements `Deref<Target = Vec<RpnExpressionNode>>`, `DerefMut`, `From<Vec<RpnExpressionNode>>`, `AsRef<[RpnExpressionNode]>`, and `AsMut<[RpnExpressionNode]>`. Its public methods are:

- `ret_field_type(schema)` returns the field type of the expression result, using the last RPN node and consulting the external schema for a trailing `ColumnRef`.
- `into_inner()` unwraps the vector.
- `is_last_constant()` checks whether the final node is a constant.

## Control flow and behavior

The file contains simple pattern matching. RPN expressions are expected to be non-empty when asking for return type or last-constant status; both methods assert that invariant. `ret_field_type` uses the final node because RPN evaluation leaves the expression result at the top of the stack, so the final node determines result type for function calls/constants or identifies the result column for column references.

The test-only `expr_tp` helper maps constants by their `ScalarValue::eval_type()`. Function calls always report `ExprType::ScalarFunc`; column refs report `ExprType::ColumnRef`.

## State and persistence behavior

There is no persistence. The state is an owned vector of expression nodes. Per-function metadata is type-erased with `Any + Send`, which allows the builder to attach arbitrary immutable metadata while keeping the node enum uniform. That type erasure means consumers must downcast consistently with the selected `RpnFnMeta`; the safety of that contract is established by builder/codegen conventions rather than the Rust type system in this file.

## Dependencies and integration points

The file depends on `tidb_query_datatype::codec::data_type::ScalarValue`, `tipb::FieldType`, and `super::super::function::RpnFnMeta`. It is used by expression builders that translate protobuf `Expr` trees to RPN, by evaluators that execute RPN nodes over row batches, and by tests that inspect generated RPN structure.

The comments explicitly point to `RpnExpressionBuilder` as the preferred construction path and to the `expr_eval` file for evaluation. `lib.rs` supplies the function metadata that becomes `RpnExpressionNode::FnCall.func_meta`.

## Risks and edge cases

The main invariant risk is empty expressions: `ret_field_type` and `is_last_constant` panic if called on an empty expression. Another risk is schema mismatch for `ColumnRef`; `ret_field_type` indexes `schema[*offset]` directly and will panic if the offset is out of range. The type-erased `metadata` field is flexible but can hide mismatches until runtime if a function is paired with metadata of the wrong concrete type.

Because `Deref` and `DerefMut` expose the inner vector, callers can mutate the expression freely and potentially break builder invariants. That is convenient for internal code but should be treated as a trusted-module API rather than a defensive abstraction.

## Test signals

This file's helper methods are compiled only under `#[cfg(test)]`, so direct tests elsewhere can assert field types, protobuf expression types, function metadata identity, and constant values. There is no local test module in the file. Coverage comes indirectly from expression builder/evaluator tests across the crate, especially tests that build protobuf expressions and then evaluate or inspect RPN nodes.
