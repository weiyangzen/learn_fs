# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_arithmetic.rs

## Purpose
Implements TiDB/TiKV scalar arithmetic RPN functions for integer, unsigned integer, real, and decimal operands. The file supplies reusable generic wrappers plus concrete operator structs for addition, subtraction, modulo, multiplication, floating/decimal division, and integer division, matching MySQL/TiDB overflow, unsignedness, NULL, division-by-zero, and decimal precision behavior.

## Important APIs, Types, and Functions
`arithmetic<A: ArithmeticOp>` and `arithmetic_with_ctx<A: ArithmeticOpWithCtx>` are `#[rpn_fn]` entry points used by the RPN function metadata layer. The context-free wrapper delegates to `A::calc(lhs, rhs)`, while the context-aware wrapper captures `EvalContext` for division-by-zero warnings/errors, overflow handling, and decimal division configuration.

`ArithmeticOp` and `ArithmeticOpWithCtx` define the implementation contract. Both require `T: Evaluable + EvaluableRet`; the context-aware version receives `&mut EvalContext`.

Concrete integer operators include signed/unsigned combinations for plus, minus, multiply, modulo, and integer division: `IntIntPlus`, `IntUintPlus`, `UintIntPlus`, `UintUintPlus`, analogous minus/multiply/mod structs, plus `IntDivideInt`, `IntDivideUint`, `UintDivideUint`, and `UintDivideInt`. Unsigned values are carried through the `Int` representation as `i64` bit patterns and cast to `u64` where needed.

Real arithmetic is implemented by `RealPlus`, `RealMinus`, `RealMod`, `RealMultiply`, and `RealDivide`. These operate on `Real` wrappers and reject infinite or non-finite results as overflow where appropriate.

Decimal arithmetic is implemented by `DecimalPlus`, `DecimalMinus`, `DecimalMod`, `DecimalMultiply`, and `DecimalDivide`. Decimal division uses `ctx.cfg.div_precision_increment`; modulo and division report divide-by-zero through `EvalContext`.

`int_divide_decimal` and `int_divide_decimal_unsigned` are RPN functions that divide decimals via `DecimalDivide`, then convert the decimal result to signed or unsigned integer semantics with overflow checks.

## Control Flow
RPN dispatch in `tidb_query_expr/src/lib.rs` maps `ScalarFuncSig` variants to these generic wrappers. Direct signatures such as `PlusReal` or `DivideDecimal` bind to a concrete operator, while generic integer signatures such as `PlusInt`, `MinusInt`, `MultiplyInt`, `IntDivideInt`, and `ModInt` first use unsignedness-aware mapper functions before selecting the correct signed/unsigned implementation.

Each `calc` method is intentionally small and deterministic. Integer addition, subtraction, and multiplication rely on Rust checked arithmetic or explicit `u64` checked operations. Overflows become `tidb_query_datatype::codec::Error::overflow` with MySQL type names like `BIGINT`, `BIGINT UNSIGNED`, `DOUBLE`, `REAL`, or `DECIMAL`.

Modulo and division short-circuit on zero divisor. Integer and real modulo return `Ok(None)` directly. Decimal modulo and decimal/real division call `EvalContext::handle_division_by_zero`, so SQL mode and evaluation flags decide whether the outcome is NULL, warning, or error.

Decimal multiply treats `Res::Truncated(t)` as a successful value, while other decimal result states are converted through the codec result path. Decimal divide and modulo use `into_result_with_overflow_err` to attach context-sensitive overflow handling.

## State and Persistence Behavior
The arithmetic operators do not persist state. They consume borrowed scalar inputs and return `Result<Option<T>>`, where `None` represents SQL NULL or NULL-like divide-by-zero results.

The only mutable state is `EvalContext` for context-aware operations. It can record warnings, return errors depending on SQL mode/configuration, consult `div_precision_increment`, and handle overflow/division-by-zero policy. No file, network, transaction, or storage-engine state is touched.

## Dependencies and Integration Points
The file depends on `tidb_query_codegen::rpn_fn` to expose Rust functions as RPN evaluators, `tidb_query_common::Result` for query expression errors, and `tidb_query_datatype` for `Int`, `Real`, `Decimal`, `EvalContext`, codec errors, decimal result handling, and helper division routines (`div_i64`, `div_i64_with_u64`, `div_u64_with_i64`).

Integration is through `tidb_query_expr/src/lib.rs`, where `map_expr_node_to_rpn_func` maps TiDB protobuf `ScalarFuncSig` values to `arithmetic_fn_meta`, `arithmetic_with_ctx_fn_meta`, or unsignedness mappers. Batch/RPN expression evaluation then invokes these functions through generated metadata. Tests use `RpnFnScalarEvaluator` to exercise the same public scalar function signatures.

## Risks
Unsigned integer arithmetic is represented as `i64` values with `u64` casts, so correctness depends on selecting the right operator from field type flags. A mapper regression could silently change overflow behavior or signedness of results.

Division-by-zero behavior is split: integer and real modulo return NULL directly, while decimal modulo and decimal/real division route through `EvalContext`. Changes must preserve TiDB/MySQL mode-dependent warning/error behavior.

Floating overflow checks are not completely uniform: plus/minus reject non-finite results, multiply rejects infinity, and divide routes overflow through `EvalContext::handle_overflow_err`. NaN inputs are mostly constrained by `Real::new`, but any future path that bypasses it would need care.

Decimal operations rely on codec `Res` variants and conversion helpers. Treating truncation as acceptable in multiplication and decimal-to-int conversion is deliberate and should be checked against TiDB compatibility before changing.

`int_divide_decimal_unsigned` has a special case where a truncated signed zero after unsigned overflow conversion returns `0`; this is subtle compatibility behavior and a high-risk area for simplification.

## Test Signals
Inline tests cover NULL propagation, signed/unsigned integer addition and subtraction, integer modulo sign behavior, unsigned modulo boundary cases, decimal/real modulo with zero divisors, decimal multiply with large operands, integer division signedness and overflow, decimal integer division conversion and overflow, real/decimal division precision, floating overflow, and SQL-mode-sensitive divide-by-zero warnings/errors.

High-value regression cases include `i64::MIN / -1`, unsigned `u64::MAX` encoded as `i64`, negative signed values combined with unsigned operands, decimal division with different `div_precision_increment` values, real overflow from `f64::MAX`, and SQL modes involving `ERROR_FOR_DIVISION_BY_ZERO`, `STRICT_ALL_TABLES`, `IN_UPDATE_OR_DELETE_STMT`, and `DIVIDED_BY_ZERO_AS_WARNING`.
