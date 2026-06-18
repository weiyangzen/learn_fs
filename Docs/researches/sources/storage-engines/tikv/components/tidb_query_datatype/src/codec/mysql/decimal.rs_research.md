# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/decimal.rs

## Purpose
`decimal.rs` implements TiKV's MySQL-compatible fixed precision decimal value, arithmetic, conversions, comparison, hashing, and binary encoders. It mirrors TiDB `MyDecimal` behavior while fitting values into a fixed nine-word base-1e9 buffer, so it is used anywhere pushed-down expression evaluation needs MySQL `DECIMAL` semantics instead of Rust floating point behavior.

## Important APIs, Types, and Functions
`Res<T>` is the local status wrapper for decimal operations. It carries a value plus `Ok`, `Truncated`, or `Overflow` status and can be converted through `EvalContext` so SQL mode decides whether the status becomes an error or warning.

`Decimal` is `#[repr(C)]`, asserted to be 40 bytes, and stores `int_cnt`, `frac_cnt`, `result_frac_cnt`, a sign flag, and `[u32; 9]` words. Each word stores up to 9 decimal digits. Public helpers include `zero`, `is_negative`, `prec_and_frac`, `frac_cnt`, `convert_to`, `round`, `shift`, `as_i64`, `as_i64_with_ctx`, `as_u64`, `from_f64`, `from_bytes`, `approximate_encoded_size`, `div`, and `is_zero`.

`RoundMode` supports `HalfEven`, `Truncate`, and a limited `Ceiling` path. Arithmetic is provided through trait implementations for `Add`, `Sub`, `Mul`, `Div`, `Rem`, and `Neg`, backed by `do_add`, `do_sub`, `do_mul`, and `do_div_mod_impl`. Bounds helpers `max_decimal` and `max_or_min_dec` synthesize maximum decimal values for a precision and scale.

The codec surface is split between comparable datum bytes and chunk bytes. `DecimalEncoder::write_decimal` writes precision, scale, and order-preserving bytes using sign inversion. `DecimalDecoder::read_decimal` reverses that format. `write_decimal_to_chunk` and `read_decimal_from_chunk` copy the raw 40-byte `Decimal` layout for vectorized/chunk execution. `DecimalDatumPayloadChunkEncoder` bridges datum payload bytes into chunk layout.

## Control Flow
Parsing starts in `from_bytes_with_word_buf`: trim whitespace, read optional sign, split integer and fractional digits, cap word counts with `fix_word_cnt_err`, fill integer words from right to left and fractional words from left to right, then optionally apply scientific notation with `shift`. Non-space trailing garbage marks the result as truncated; oversized integer/fractional parts produce `Overflow` or `Truncated` status while still returning a clipped value.

Addition and subtraction first align integer and fractional word counts. If signs match, addition propagates base-1e9 carries from the least significant word. If signs differ, subtraction calls `calc_sub_carry` to compare absolute values, possibly swaps operands, and then subtracts from the least significant aligned word while preserving the correct sign. Multiplication uses word-by-word long multiplication, then normalizes leading zero words and turns negative zero into zero. Division and modulo share `do_div_mod_impl`, which normalizes the divisor, estimates each quotient word, subtracts products from a temporary buffer, corrects overestimates, and either writes quotient words or reconstructs the remainder.

Rounding and shifting work at digit and word boundaries. `round_with_word_buf_len` decides target fractional words, clears discarded words, calls `handle_incr` to apply half-up/ceiling/truncate increment rules, and uses `handle_carry` to propagate a carry that may grow the integer part. `shift_with_word_buf_len` computes occupied digit bounds, handles huge shift overflow/truncation, performs small digit shifts inside words, then performs whole-word movement.

Encoding computes the requested integer and fractional byte widths from `(prec, frac)`. Negative values are masked with `u32::MAX`, and the first byte is XORed with `0x80` so lexicographic bytes remain comparable. Decoding reads the metadata, determines the sign mask from the first payload byte, rebuilds words, validates partial leading/trailing words, and restores zero normalization.

## State and Persistence Behavior
The decimal value is pure in-memory state; this file does not persist directly to disk. Its encoded bytes are persisted indirectly through TiKV datum storage and exchanged through coprocessor/chunk execution. The comparable codec is a logical storage format. The chunk codec is a raw memory-layout format guarded by `#[repr(C)]` and `const_assert_eq!(DECIMAL_STRUCT_SIZE, mem::size_of::<Decimal>())`, so it is intended for compatible TiDB/TiKV vectorized payloads rather than an independently portable wire format.

`EvalContext` is the side-effect surface for warnings and errors. Conversion from `Res<T>` calls `handle_truncate`, `handle_truncate_err`, or `handle_overflow_err`, which means the same arithmetic result can be accepted, warned, or rejected depending on SQL flags.

## Dependencies and Integration Points
The module depends on `codec::prelude` buffer traits, `TEN_POW`, `EvalContext`, conversion traits (`ConvertTo`, `ToStringValue`), MySQL datatype definitions (`Real`, `Bytes`, `Json`, `JsonRef`, `JsonType`), `DEFAULT_DIV_FRAC_INCR`, and TiKV logging/error helpers. It integrates with JSON decimal conversion, integer/float/string casts, expression boolean evaluation through `AsMySqlBool`, datum encoding, and vectorized chunk payload conversion.

## Risks and Edge Cases
The arithmetic is dense and boundary-heavy: carries can grow integer precision, subtraction trims leading and trailing zero words before comparing, multiplication truncates differently depending on operand order, and division manually estimates quotient words. Any change to word count, rounding, or sign normalization can break MySQL compatibility.

`RoundMode::Ceiling` is explicitly incomplete in one digit path, and comments note several TiDB compatibility gaps in cast error handling. `from_f64` uses Rust's canonical float string, not the exact binary float value. `read_decimal_from_chunk` and `write_decimal_to_chunk` rely on raw struct layout and endianness assumptions. `read_decimal` performs validation, but malformed lengths or inconsistent precision/scale remain high-risk inputs because many later operations index `word_buf` by computed word counts.

## Test Signals
The embedded tests are broad: integer and float conversion, decimal to integer/float, shifting, rounding, string formatting, comparable codec, raw chunk codec including TiDB bytes, ordering, hashing, max/min synthesis, add/sub/mul/div/rem, negation, floor/ceil, byte conversion with `EvalContext` warning modes, and `Res::into_result_impl`. These tests directly cover the main compatibility and overflow/truncation surfaces.
