# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/comparison.rs

## Purpose
`json/comparison.rs` implements ordering and equality for binary JSON values. It follows TiDB/MySQL JSON precedence rules across JSON types and provides type-specific comparisons for numbers, literals, strings, arrays, objects, opaque bytes, dates/datetimes/timestamps, and times.

## Important APIs, Types, and Functions
Helper functions include `compare`, `compare_i64_u64`, and `compare_f64_with_epsilon`. `JsonRef::get_precedence` maps each `JsonType` to constants from `constants.rs`, treating JSON null and booleans as separate precedence categories inside `Literal`. `JsonRef::as_f64` converts numeric and literal JSON values for mixed numeric comparison.

The file implements `Eq`, `Ord`, `PartialEq`, and `PartialOrd` for both `JsonRef<'_>` and owned `Json`. Owned comparisons delegate to `as_ref()`.

## Control Flow
`JsonRef::partial_cmp` first compares type precedence. If precedence differs, the value with the greater precedence constant sorts greater. If precedence matches, it dispatches by left-hand type. Signed and unsigned integers use exact mixed comparison that handles negative signed values. Float comparisons use epsilon equality. Literals compare decoded literal values, with JSON null equal to JSON null by precedence. Strings and opaque values compare decoded byte slices. Arrays compare lexicographically element by element and then by length. Objects compare raw binary value bytes. Date/datetime/timestamp values compare decoded `Time`; time values compare decoded `Duration`.

Several branches return `None` if decoding string, opaque, time, or array elements fails. The `Ord` implementations unwrap `partial_cmp`, so callers using total-order APIs assume valid comparable JSON.

## State and Persistence Behavior
Comparison is read-only. It traverses borrowed binary JSON buffers and may decode nested values but does not persist or mutate state. Its results affect SQL comparison predicates, sorting, hashing contexts that rely on equality, and JSON containment.

## Dependencies and Integration Points
The module depends on `Json`, `JsonRef`, `JsonType`, binary constants, `ToStringValue`, and the shared `Result`. It integrates with `binary.rs` for array traversal, typed getters from `json/mod.rs`, `Time`/`Duration` comparison, and `json_contains.rs`, which calls `partial_cmp(...).unwrap()` for scalar containment.

## Risks and Edge Cases
Numeric comparison between large integers and floats can be lossy because mixed float paths cast integers to `f64` and use `f64::EPSILON`. `Ord::cmp` and owned `PartialEq` unwrap `partial_cmp`; malformed JSON that makes comparison return `None` can panic. Object ordering is raw binary byte ordering rather than semantic key/value traversal beyond what the binary representation guarantees. Type precedence constants are negative values, so changing their order changes SQL-visible comparison behavior.

## Test Signals
Tests cover mixed numeric comparison among `i64`, `u64`, and `f64`; comparisons within same JSON type; comparisons across different JSON type precedence categories; and date/datetime/timestamp/time ordering using parsed `Time` and `Duration` values.
