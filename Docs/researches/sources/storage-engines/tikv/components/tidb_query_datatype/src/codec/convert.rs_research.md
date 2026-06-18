# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/convert.rs

## Purpose
Implements MySQL/TiDB-compatible scalar conversions among integers, floats, decimals, strings/bytes, datetime/duration, JSON, enum, and field-type-constrained output values.

## Important APIs, Types, And Functions
Traits: `ToInt`, `ToStringValue`, `ConvertTo<T>`, and `ConvertFrom<T>`. Bound helpers: `integer_unsigned_upper_bound`, `integer_signed_upper_bound`, `integer_signed_lower_bound`. Conversion helpers include `truncate_binary`, `truncate_f64`, `get_valid_utf8_prefix`, `bytes_to_int_without_context`, `bytes_to_uint_without_context`, `produce_dec_with_specified_tp`, `produce_float_with_specified_tp`, `produce_str_with_specified_tp`, `pad_zero_for_binary_type`, `get_valid_int_prefix(_helper)`, and `get_valid_float_prefix(_helper)`.

## Control Flow
Generic `ConvertTo` routes through `ToInt`, `ConvertTo<f64>`, or `ToStringValue`. Numeric conversions clamp to type bounds and route warnings/errors through `EvalContext`. String-to-int first keeps the valid UTF-8 prefix, trims, extracts a numeric prefix, rounds float-like input to integer strings without losing decimal precision, parses, and clamps overflow. String-to-float extracts a valid float prefix and maps parse infinities to min/max with truncation handling. Field-type producers enforce `flen`, `decimal`, unsigned flags, multi-byte character truncation, binary zero padding, and statement-mode warning behavior.

## State And Persistence
No persistent state. All mutable effects are warnings/errors recorded in `EvalContext`.

## Dependencies And Integration Points
Depends on protobuf `FieldType`, field accessors, `FieldTypeTp`, `Collation`, MySQL decimal/time/json/vector data types, charset constants, `EvalContext`, flags, and result wrappers. Used broadly by expression evaluation and cast functions.

## Risks
Compatibility rules are subtle: signed/unsigned overflow, truncate-as-warning, invalid UTF-8 prefixes, exponent rounding, and binary padding all affect SQL-visible results. Some functions panic for unsupported field types. Float rounding differs between signed and unsigned paths (`round_ties_even` vs `round`). `ToStringValue` uses specialization and has FIXME notes for missing TiDB produce-string steps.

## Test Signals
Extensive local tests cover int/uint conversions, overflows, truncation, JSON casts, float parsing, valid-prefix extraction, binary truncation, float truncation, string production for UTF-8/GBK/GB18030/ASCII and invalid UTF-8, and decimal field-type production.
