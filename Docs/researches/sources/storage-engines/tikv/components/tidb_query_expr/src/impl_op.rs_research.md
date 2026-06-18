# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_op.rs

## Purpose
`impl_op.rs` implements SQL logical, null, truthiness, unary, and bitwise operators for the RPN expression engine. It is the operator layer for three-valued boolean logic, `IS NULL`, `IS TRUE`, `IS FALSE`, unary negation, unary not, bit operations, and left/right shifts.

## Important APIs, Types, and Functions
Logical functions are `logical_and`, `logical_or`, and `logical_xor`. Unary predicates and operators include `unary_not_int`, `unary_not_real`, `unary_not_decimal`, `unary_not_json`, `unary_minus_uint`, `unary_minus_int`, `unary_minus_real`, and `unary_minus_decimal`.

Null checks are factored through `is_null_ref<'a, T: EvaluableRef<'a>>` with typed RPN wrappers `is_null<T>`, `is_null_bytes`, `is_null_json`, and `is_null_vector_float32`. Bitwise functions include `bit_and`, `bit_or`, `bit_xor`, `bit_neg`, `left_shift`, and `right_shift`.

`KeepNull` is a compile-time policy trait with `KeepNullOn` and `KeepNullOff`. It parameterizes `int_is_true`, `real_is_true`, `decimal_is_true`, `int_is_false`, `real_is_false`, and `decimal_is_false` so `IS TRUE` style signatures can either preserve `NULL` or collapse `NULL` to false depending on the TiDB scalar signature.

## Control Flow
The logical functions encode SQL three-valued logic directly. `logical_and` returns `0` if either side is explicit zero, returns `NULL` if no zero exists but at least one side is `NULL`, and otherwise returns `1`. `logical_or` returns `1` for any nonzero input, `0` only when both are zero, and `NULL` for `NULL OR false` or `NULL OR NULL`. `logical_xor` requires both operands to be non-null and returns whether exactly one operand is logically nonzero.

Unary not maps zero to `1` and nonzero to `0` for int, real, and decimal inputs. JSON unary not compares only against JSON numeric zero. Unary minus for signed integers checks `i64::MIN` overflow; unary minus for unsigned values interprets the input bits as `u64`, allows exactly `i64::MAX + 1` to become `i64::MIN`, and errors above that boundary.

`IS NULL` always returns a non-null integer result. Truthiness helpers use `KeepNull`: with `KeepNullOff`, `NULL` becomes `Some(0)`; with `KeepNullOn`, `NULL` remains `None`. Bit operations propagate `NULL` unless all required operands are present. Shifts cast the left operand to `u64`, treat shift counts whose `u64` representation is >= 64 as zero, and otherwise use wrapping shift operations before returning the bits as `i64`.

## State and Persistence Behavior
This module is stateless and has no durable persistence. All behavior is local to one scalar evaluation and its decoded input values.

## Dependencies and Integration Points
Dependencies are intentionally small: `tidb_query_codegen::rpn_fn`, `tidb_query_common::Result`, and TiDB codec data types plus `Error` for overflow. Integration is through `lib.rs`, which maps scalar signatures such as `LogicalAnd`, `UnaryMinusInt`, `IntIsNull`, `DecimalIsTrueWithNull`, `BitAndSig`, `LeftShift`, and `RightShift` to this module. `UnaryMinusInt` is selected through `map_unary_minus_int_func` so signed and unsigned field types route to the correct implementation.

## Risks and Edge Cases
The highest-risk area is SQL compatibility around `NULL` and truthiness. `IS TRUE` and `IS TRUE WITH NULL` look similar but differ by `KeepNull`, so signature mapping mistakes would produce visible SQL behavior changes. Shift operations intentionally cast signed operands to unsigned bits; negative shift counts therefore become huge `u64` counts and return zero. That matches the tested behavior but is non-obvious.

Unsigned unary minus is another compatibility-sensitive branch because the same physical `i64` value may represent an unsigned MySQL value. Overflow text uses the unsigned magnitude for unsigned values and the signed magnitude for signed values. JSON unary not only treats JSON numeric zero as false; arrays containing zero are true.

## Test Signals
Tests cover logical truth tables with nulls, unary not for int/real/decimal/json, signed and unsigned unary minus overflow boundaries, null predicates across int, real, decimal, bytes, time, duration, and JSON values, bit and/or/xor/negation, `IS TRUE` and `IS FALSE` with and without null preservation, and left/right shifts for positive, negative, zero, large, and null operands.
