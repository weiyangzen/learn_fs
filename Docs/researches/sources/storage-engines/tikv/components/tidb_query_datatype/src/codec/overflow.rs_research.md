# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/overflow.rs

## Purpose
This file provides checked division helpers for mixed signed and unsigned integer arithmetic where MySQL/TiDB semantics require division-by-zero and unsigned overflow errors instead of Rust panics or wrapping behavior.

## Important APIs, Types, and Functions
`div_i64(a, b)` returns signed division or `Error::division_by_zero`; it detects the `i64::MIN / -1` overflow through `overflowing_div`. `div_u64_with_i64(a, b)` divides an unsigned numerator by a signed denominator, returning unsigned results and raising overflow when a negative divisor would imply an out-of-range unsigned result. `div_i64_with_u64(a, b)` handles a signed numerator and unsigned divisor similarly.

## Control Flow and State
Each function first rejects a zero divisor. The signed/signed function delegates overflow detection to Rust's intrinsic checked flag. The mixed functions branch on the signed operand's negativity: negative combinations either return `0` when the absolute magnitude is below the divisor or raise `UNSIGNED BIGINT` overflow when the result would not fit MySQL unsigned semantics.

## Dependencies and Integration Points
The module depends only on `crate::codec::{Error, Result}`. It is a utility for codec/expression arithmetic paths that need consistent TiDB/MySQL error codes, especially `ERR_DIVISION_BY_ZERO` and `ERR_DATA_OUT_OF_RANGE`.

## Risks and Edge Cases
The exact overflow thresholds are subtle around `i64::MIN`, because negating it overflows and the code uses `overflowing_neg().0` before casting to `u64`. Current behavior is intentional and tested, but future simplification could easily change edge semantics. Error messages identify `"UNSIGNED BIGINT"` for overflow, so callers may depend on that type string.

## Test Signals
The test matrix covers signed overflow, positive and negative signed division, mixed signed/unsigned boundary cases, and division by zero for all three helpers with expected codec error codes.
