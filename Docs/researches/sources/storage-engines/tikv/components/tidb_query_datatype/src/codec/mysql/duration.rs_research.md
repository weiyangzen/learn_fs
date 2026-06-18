# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/duration.rs

## Purpose
`duration.rs` implements MySQL `TIME`/duration semantics for TiKV expression evaluation. It represents a duration as signed nanoseconds plus fractional seconds precision (FSP), parses MySQL-compatible duration strings and numeric values, formats values for SQL output and numeric casts, performs checked arithmetic, and provides datum/chunk codecs.

## Important APIs, Types, and Functions
The file defines duration constants for nanoseconds, microseconds, seconds, minutes, hours, days, allowed FSP widths, and MySQL's maximum time range of `838:59:59`. `check_hour_part`, `check_minute_part`, `check_second_part`, `check_nanos_part`, and `check_nanos` enforce component and total range limits.

`Duration` is `#[repr(C)]` with `nanos: i64` and `fsp: u8`. Public APIs include component readers (`hours`, `minutes`, `secs`, `subsec_micros`, `subsec_nanos`, `fsp`), FSP normalization (`minimize_fsp`, `maximize_fsp`, `round_frac`), unit conversions (`to_secs`, `to_secs_f64`, `to_millis`, `to_micros`, `to_nanos`), constructors (`zero`, `from_secs`, `from_millis`, `from_micros`, `from_nanos`, `new_from_parts`, `from_i64`), parsers (`parse`, `parse_consider_overflow`, `parse_exactly`), and checked arithmetic (`checked_add`, `checked_sub`).

Codec traits include `DurationEncoder::write_duration_to_chunk`, `DurationDatumPayloadChunkEncoder` for int and varint datum payloads, and `DurationDecoder` for int, varint, and chunk layouts. Conversion traits produce `f64` and `Decimal`; `Display`, ordering, hashing, and `AsMySqlBool` are implemented around the stored nanoseconds.

## Control Flow
Parsing is implemented in the nested `parser` module using `nom`. It trims input, captures an optional negative sign, then tries `day hh:mm:ss`, colon-delimited `hh:mm:ss`, and compact `hhmmss` forms. Fractional seconds are parsed after an optional dot, taking one extra digit when rounding is needed, and scaled to nanoseconds. If a compact parse leaves trailing data and the original string can match a datetime shape, the parser falls back to `DateTime::parse_datetime` and converts the time part to `Duration` for TiDB compatibility.

`Duration::new_from_parts` validates components, folds hours, minutes, seconds, and fractional nanoseconds into one signed count, then calls `checked_round` to round according to FSP and enforce the global range. `from_secs`, `from_millis`, `from_micros`, and `from_nanos` all validate FSP first, convert to nanoseconds with checked multiplication where needed, and round to requested FSP. `from_i64` interprets numeric `HHMMSS` values, with a datetime parse fallback for large positive values that look like datetime literals.

Formatting routes through `format(sep)`: `Display` uses `:` separators, while `to_numeric_string` omits separators for numeric casts. Fractional output is truncated to the stored FSP after prior rounding. Checked addition/subtraction use Rust checked integer arithmetic, reapply the MySQL max range, and preserve the maximum FSP of the operands.

## State and Persistence Behavior
`Duration` has no persistence of its own. Datum storage carries nanoseconds as signed int or varint payloads; chunk storage writes the nanosecond count as little-endian `i64`. FSP is not stored in the chunk payload, so decoders reconstruct it from `FieldType.decimal()` or the caller-supplied FSP. `EvalContext` records warning/error behavior for truncated parses and overflow handling, including an `overflow_as_null` path in `parse_consider_overflow`.

## Dependencies and Integration Points
The module depends on `tipb::FieldType`, `FieldTypeAccessor`, `codec::prelude`, `TEN_POW`, `Decimal`, `check_fsp`, `DEFAULT_FSP`, `MIN_FSP`, `MAX_FSP`, `Time`/`TimeType` for datetime fallback, conversion traits, MySQL error codes, and `EvalContext`. It integrates with scalar casts from strings and numbers to time, vectorized chunk codecs, JSON/time conversion through shared datatype traits, and boolean evaluation.

## Risks and Edge Cases
The most subtle risk is compatibility parsing. Inputs like `2011-11-11`, `1234abc`, compact numbers, datetime-like strings, and strings with partial trailing garbage intentionally follow TiDB/MySQL quirks. Small changes to fallback conditions or truncation warnings can alter SQL results. FSP rounding can roll seconds, minutes, or hours forward, including negative values. Chunk decoding depends on external FSP because only nanoseconds are stored. Numeric `from_i64` has a special large positive datetime fallback but negative large values do not mirror that path.

## Test Signals
Tests cover component accessors, microsecond rounding, overflow-as-warning parsing, a large matrix of duration string formats and datetime fallback cases, overflow-as-null handling, numeric string and `Decimal`/`f64` conversion, `round_frac`, chunk codec round trips, checked addition/subtraction overflow, and `from_i64`. Benchmarks cover parser, component access, decimal conversion, rounding, codec, and arithmetic hot paths.
