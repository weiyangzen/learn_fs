# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/datum.rs

## Purpose
Implements the legacy dynamic `Datum` representation and the original datum byte codec used for TiDB-compatible key/value encoding. It covers datum variants, comparison/coercion rules, conversion to primitive/MySQL types, arithmetic helpers, JSON conversion, encoding/decoding, size estimation, datum splitting, and skip helpers.

## Important APIs, Types, And Functions
- Datum flags: null, bytes, compact bytes, signed/unsigned integers, float, decimal, duration, varint forms, JSON, vector-float32, and max marker.
- `Datum`: variants for null, signed/unsigned integers, float, duration, bytes, decimal, time, JSON, vector-float32, enum, set, min, and max.
- Accessors: `as_int`, `as_real`, `as_decimal`, `as_string`, `as_time`, `as_duration`, `as_json`.
- Comparison: `cmp`, typed comparison helpers, `cmp_f64`, enum/set compare stubs.
- Conversion: `into_bool`, `to_string`, `into_string`, `into_f64`, `into_i64`, `into_arith`, `into_dec`, `cast_as_json`, `into_json`, `to_json_path_expr`.
- Arithmetic: `coerce`, `checked_div`, `checked_add`, `checked_minus`, `checked_mul`, `checked_rem`, and `checked_int_div`.
- Codecs: `DatumDecoder::read_datum`, `decode`, `DatumEncoder::write_datum`, `encode`, `encode_key`, `encode_value`, `encode_to`, `split_datum`, and `skip_n`.

## Control Flow
Comparison first handles JSON cross-type ordering specially, then dispatches by the right-hand datum variant. Numeric comparisons coerce as needed across signed, unsigned, float, decimal, string, time, and duration forms. Encoding iterates a datum slice, writes one flag per datum, and chooses comparable fixed-width encodings for keys versus compact/varint encodings for values. Decoding reads a flag and consumes the corresponding payload. `split_datum` computes the encoded length for the leading datum based on flag-specific payload rules, including JSON and vector-float32 reference decoders. Arithmetic helpers perform checked operations and convert divide-by-zero cases to `Datum::Null` for division/remainder semantics.

## State And Persistence Behavior
`Datum` owns in-memory values. Its persistent behavior is the encoded byte stream shared with TiDB: comparable encodings preserve sort order for key encoding, while value encoding uses compact forms. `Min` is special-cased so it must be the last datum when encoded, and `Max` uses its own flag.

## Dependencies And Integration Points
This file depends on the standalone `codec` crate for number and byte encodings, MySQL decimal/time/duration/JSON/vector-float32 codecs, `EvalContext` for warning/error and conversion behavior, TiKV byte-slice helpers, and conversion traits. It is used by row/table/index codec layers and remains a compatibility bridge alongside newer `ScalarValue`/`VectorValue` APIs.

## Risks And Edge Cases
- Several comments note differences or uncertainty versus TiDB behavior, especially decimal/time coercion and comparison.
- `Datum::VectorFloat32` comparison is not implemented, and enum/set encoding and size estimation are `unimplemented!`.
- `Datum::Min` uses `BYTES_FLAG` for backward compatibility and sets a guard requiring it to be the last datum.
- Float comparison returns an invalid-type error for unordered NaN cases.
- Some conversions use default `EvalContext`, which may not preserve caller-specific SQL mode or warning behavior.
- Decimal multiplication unwraps the decimal result and may panic if the decimal operation returns `None`.
- `split_datum` must exactly match all encoding formats; mistakes here affect key prefix parsing and skip logic.

## Test Signals
Local tests are extensive. They verify key/value round-trip encoding for primitive, decimal, JSON, duration, and vector-float32 data; cross-type comparison and encoded comparable ordering; MySQL boolean conversion; datum splitting for key/value buffers; coercion; JSON casts; JSON conversion; and primitive conversions to f64/i64. Gaps remain around enum/set and vector-float32 comparison/encoding edge cases.
