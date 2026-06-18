# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_math.rs

## Purpose
`impl_math.rs` implements TiDB/TiKV RPN scalar functions for SQL mathematical operations. It covers constants and checksums, logarithms, trigonometry, exponentiation, sign and square root, ceiling/floor/absolute value variants, MySQL-compatible random numbers, base conversion through `CONV`, rounding, and truncation for integer, unsigned integer, real, and decimal values.

## Important APIs, Types, and Functions
Functions are exported through `#[rpn_fn]` metadata and are wired from `tidb_query_expr/src/lib.rs` by `ScalarFuncSig` entries such as `Pi`, `Crc32`, `Log1Arg`, `CeilReal`, `FloorDecToInt`, `AbsInt`, `Sin`, `Pow`, `Rand`, `Conv`, `RoundWithFracReal`, and `TruncateDecimal`.

The file uses trait families to share generic RPN entry points while preserving SQL type-specific return types. `ceil<C: Ceil>` dispatches to implementations such as `CeilReal`, `CeilDecToDec`, `CeilIntToDec`, `CeilDecToInt`, and `CeilIntToInt`. `floor<T: Floor>` mirrors that with `FloorReal`, `FloorIntToDec`, `FloorDecToInt`, `FloorDecToDec`, and `FloorIntToInt`.

Key helpers include `f64_to_real`, which maps non-finite floating results to SQL `NULL`; `truncate_real`, which avoids changing values when decimal shifting overflows to infinity; `i64_to_usize`, a shared signed/unsigned magnitude helper used by string functions; and `IntWithSign`, which models signed base and signed numeric conversion for `CONV`. `MySqlRng` stores MySQL-compatible `RAND` state with `seed1` and `seed2`; a thread-local `MYSQL_RNG: RefCell<MySqlRng>` backs unseeded `RAND()`.

## Control Flow
Most functions are thin, type-specific RPN leaves: arguments are already decoded by the expression engine, operations run over TiDB wrapper types such as `Real` and `Decimal`, and return values are `Result<Option<T>>` so SQL `NULL` and evaluation errors are distinct.

Floating functions generally compute with Rust `f64`, then call `Real::new(...).ok()` or `f64_to_real`. Invalid mathematical domains such as logarithm of non-positive numbers, square root of negative values, and inverse trig outside range become `None`, while explicit overflows in `exp`, `cot`, `pow`, and `degrees` become `Error::overflow`.

Decimal ceiling, floor, rounding, and truncation delegate to `Decimal` APIs and convert codec results through `into_result(ctx)` when an `EvalContext` is needed for warning/error handling. Integer truncation selects a signed or unsigned path based on the mapped RHS field type in `lib.rs`: non-negative precision returns the original integer; sufficiently negative precision collapses to zero; intermediate negative precision divides and multiplies by a power of ten.

`CONV` trims input bytes as UTF-8 lossy text, validates source and target bases in the inclusive range 2..=36, extracts an optional sign and the maximal valid digit prefix, parses with `u64::from_str_radix`, clamps signed values where MySQL behavior requires it, and formats with uppercase digits in the target base. Invalid bases return `NULL`; strings without a valid digit prefix return `"0"`; numeric overflow returns a `BIGINT UNSIGNED` overflow error.

## State and Persistence Behavior
This file has no durable storage behavior. The only state is per-thread process memory in `MYSQL_RNG`. `rand()` advances the thread-local generator every call. `rand_with_seed_first_gen(seed)` constructs a temporary `MySqlRng` and returns only the first generated value, so it is deterministic for a given seed and does not mutate `MYSQL_RNG`.

## Dependencies and Integration Points
Dependencies include `tidb_query_codegen::rpn_fn`, `tidb_query_common::Result`, TiDB datatype wrappers from `tidb_query_datatype::codec::data_type`, `EvalContext`, MySQL decimal round modes, `file_system::calc_crc32_bytes`, `tikv_util::time::get_time`, and `num`/`num_traits` math helpers. Integration is through `lib.rs` scalar signature dispatch, plus `impl_string.rs` imports `i64_to_usize` for string-position logic.

## Risks and Edge Cases
The highest-risk behavior is compatibility with MySQL/TiDB numeric semantics rather than algorithmic complexity. Floating operations must consistently choose between `NULL` and overflow errors for `NaN` or infinite results. `Real::new(f64::INFINITY).unwrap()` appears in tests for some paths, so behavior depends on the local `Real` wrapper allowing infinity while rejecting `NaN` in other paths.

`CONV` is subtle because negative bases mean signed interpretation, positive bases mean unsigned interpretation, and signed overflow is clamped rather than always errored. The target-base sign flag also affects whether a negative sign is emitted or the value is formatted through two's-complement representation.

Rounding and truncation for very large positive/negative precisions clamp to `i32` or `i8` ranges. `round_with_frac_int` uses floating arithmetic to round integers at negative precisions, which is compact but can be precision-sensitive for very large integers. `RAND()` state is thread-local, so parallel evaluation can produce per-thread sequences.

## Test Signals
Inline tests are broad. They cover pi, crc32, logarithm domains, all ceiling/floor variants, absolute value overflow on `i64::MIN`, sign, sqrt, radians/degrees, exp overflow, trig functions, cot and pow overflow, seeded and unseeded random generation, inverse trig domains, `CONV` valid/invalid/error cases, round/truncate variants for signed, unsigned, real, and decimal inputs, fractional rounding, and direct `MySqlRng` seed behavior.
