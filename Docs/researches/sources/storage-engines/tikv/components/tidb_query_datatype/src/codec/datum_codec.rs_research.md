# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/datum_codec.rs

## Purpose
Provides the newer unified trait-based datum codec for evaluable types. It separates payload decoding/encoding from flag-and-payload encoding, then exposes typed raw datum decoders for vectorized storage paths.

## Important APIs, Types, And Functions
- `DatumPayloadDecoder`: reads typed payloads after the datum flag, wrapping codec errors as `Error::InvalidDataType`.
- `DatumPayloadEncoder`: writes payloads for integers, floats, decimals, compact bytes, JSON, vector-float32, and enum numeric values.
- `DatumFlagAndPayloadEncoder`: writes complete datum flag plus payload for null, integer, float, decimal, bytes, duration, datetime, JSON, vector-float32, and enum-as-uint.
- `EvaluableDatumEncoder`: semantically named encoder for eval values, mapping eval types to datum encodings.
- `ColumnIdDatumEncoder`: writes column IDs as var-int datum values.
- Typed decoders: `decode_int_datum`, `decode_real_datum`, `decode_decimal_datum`, `decode_bytes_datum`, `decode_date_time_datum`, `decode_duration_datum`, `decode_json_datum`, `decode_vector_float32_datum`, and `decode_enum_datum`.
- `RawDatumDecoder<T>`: generic trait implemented for `&[u8]` for supported eval types.

## Control Flow
Decoder helpers first check for an empty buffer, then strip the leading flag and validate that the flag is legal for the requested eval type. They accept both index and record encodings where TiDB uses different flags, for example bytes as comparable or compact bytes, datetime as `UINT` or `VAR_UINT`, and duration as duration or var-int. Encoding methods write the flag and delegate payload layout to lower-level codec traits. `decode_real_datum` also truncates double precision to float precision when the field type is `Float`, and wraps valid non-NaN results in `Real`.

## State And Persistence Behavior
This file has no in-memory state. Its persistence contract is exact datum byte compatibility across record/index encodings. All methods operate on caller-provided buffers or byte slices.

## Dependencies And Integration Points
It integrates `tipb::FieldType`, `FieldTypeAccessor`, `FieldTypeTp`, `EvalContext`, legacy datum flag constants, and MySQL encoders/decoders for decimal, duration, enum, JSON, time, and vector-float32. `ScalarValueRef` and `VectorValue` encoding paths call `EvaluableDatumEncoder`; table/row decoding can use `RawDatumDecoder`.

## Risks And Edge Cases
- Set decoding is `unimplemented!`; any generic set raw-decoder use will panic.
- Unsupported flags return detailed `InvalidDataType` errors, so callers must pass the correct field type and source encoding kind.
- Decimal encoding derives precision/fraction from the value, with a FIXME asking whether field type should provide them.
- Real decoding maps NaN to `None` through `Real::new(v).ok()`, which can blur invalid data and null semantics.
- Date/time and duration decoding require field metadata to unflatten packed values correctly.

## Test Signals
There is no local test module. Coverage is indirect through `ScalarValueRef`/`VectorValue` encoding and table/row codec decoding tests. Missing direct tests should enumerate accepted flags for each eval type and verify rejection messages for unsupported flags, especially record-vs-index encodings.
