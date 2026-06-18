# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_other.rs

## Purpose
`impl_other.rs` is a small catch-all module for scalar functionality not assigned to the larger expression implementation files. In the current source it implements only SQL `BIT_COUNT`.

## Important APIs, Types, and Functions
The single exported RPN function is `bit_count(arg: &Int) -> Result<Option<Int>>`. It calls Rust's `count_ones()` on the `i64` value and converts the resulting `u32` count to the TiDB integer return type.

## Control Flow
The expression engine handles nullable argument propagation around the non-null `&Int` function signature. For non-null input, `bit_count` computes the population count of the raw two's-complement 64-bit representation and returns it as `Some(Int)`.

## State and Persistence Behavior
This module is pure and stateless. It has no persistence, allocation-heavy state, or external side effects.

## Dependencies and Integration Points
Dependencies are limited to `tidb_query_codegen::rpn_fn`, `tidb_query_common::Result`, and TiDB codec data type aliases. `lib.rs` maps `ScalarFuncSig::BitCount` to `bit_count_fn_meta()`.

## Risks and Edge Cases
The important edge case is negative input. Because `count_ones()` operates on the two's-complement representation of `i64`, `-1` has 64 set bits and `i64::MIN` has 1 set bit. That matches MySQL-style unsigned bit interpretation, but replacing it with arithmetic absolute-value logic would be wrong.

## Test Signals
The inline test covers positive values, zero, several negative values, `i64::MAX`, `i64::MIN`, and `NULL` propagation through the RPN evaluator.
