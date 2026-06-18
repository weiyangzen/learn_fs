# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_control.rs

Purpose: Implements MySQL/TiDB control-flow scalar functions in the RPN engine: `IFNULL`, searched `CASE WHEN`, and `IF`. The file provides generic fixed-width implementations plus separate bytes and JSON variants where borrowed values must be converted to owned results.

Important APIs, types, and functions: `if_null<T>`, `if_null_json`, and `if_null_bytes` return the first argument when it is non-null, otherwise the second. `case_when<T>`, `case_when_bytes`, and `case_when_json` consume raw varargs as `(condition, result)` chunks with an optional trailing else value. `if_condition<T>`, `if_condition_json`, and `if_condition_bytes` select between true/false values based on an integer condition. `case_when_validator<T>` validates child return types for raw vararg CASE expressions.

Control flow: `IFNULL` is a simple two-way branch on `lhs.is_some()`. `CASE WHEN` iterates over `args.chunks(2)`: a single final chunk is treated as ELSE; otherwise the first item is borrowed as `Option<Int>` and evaluated as false when null or zero, true for any nonzero integer. The first true condition returns its paired result immediately. If no condition matches and no ELSE exists, it returns `None`. `IF` uses the same integer truthiness rule: null or zero selects the false value. Bytes and JSON functions mirror generic flow but use `EvaluableRef`/`as_*` borrowing and produce owned `Vec<u8>` or `Json`.

State and persistence: These evaluators are stateless. They do not modify `EvalContext` or persist metadata. Validation happens at expression build time through the `extra_validator` hook for CASE functions.

Dependencies and integration points: Uses `tidb_query_codegen::rpn_fn`, `tidb_query_common::Result`, and scalar data traits from `tidb_query_datatype::codec::data_type::*`. The validators call `super::function::validate_expr_return_type`, so CASE type safety is coordinated with the broader scalar-function mapper and generated RPN argument model.

Risks and edge cases: Raw vararg access relies on validators to guarantee alternating int/result types; a missing or incorrect validator could turn `borrow_scalar_value_ref` assumptions into runtime failures. SQL truthiness is intentionally integer-only here; nonzero negative values are true and null is false for conditions. The file does not implement lazy evaluation itself: it selects from already supplied scalar references in the RPN call shape, so upstream expression planning determines whether branch expressions have already been evaluated. Bytes/JSON variants must clone/to_owned to avoid returning borrowed data beyond the evaluation call.

Test signals: Tests cover `IFNULL` null combinations, CASE first-match and ELSE behavior, null conditions, null result values, bytes CASE, and `IF` choosing true/false branches with null-as-false semantics.
