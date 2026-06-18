# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/compat_v1.rs

## Purpose
This file converts row-format-v2 encoded column values into v1 datum-compatible encodings. It is the bridge for code that decodes or transports row v2 data through older datum APIs.

## Important APIs, Types, and Functions
`decode_v2_u64` reads 1, 2, 4, or 8 byte little-endian unsigned integer payloads, matching TiDB's compact row v2 integer encoding. The private `decode_v2_i64` does the signed equivalent through sign-extending casts from 1, 2, 4, or 8 byte payloads. `V1CompatibleEncoder` extends `DatumFlagAndPayloadEncoder` with helpers for v2 signed/unsigned integers, duration, and the central `write_v2_as_datum(src, ft)`.

`write_v2_as_datum` maps `FieldTypeTp` to v1 datum flags and payload encodings. Integer-like fields choose signed or unsigned by field flag. Float/double, decimal, JSON, and vector payloads are copied after writing the corresponding datum flag. String/blob/geometry fields use compact bytes. Date/time/enum/bit/set use unsigned integer datum encoding. Year uses signed integer encoding. Duration intentionally uses `DURATION_FLAG` instead of TiDB's varint choice because the fixed payload is faster in TiKV.

## Control Flow and State
The conversion is stateless and writes directly into the destination buffer. Invalid compact integer widths and unsupported field types return `Error::InvalidDataType`. Null field type writes only `NIL_FLAG`.

## Dependencies and Integration Points
The file depends on `codec::number::NumberCodec`, `BufferWriter`, field metadata traits, and datum codec helpers. It integrates with `encoder_for_test` in tests and with `RawDatumDecoder` to prove that converted bytes decode as the expected high-level scalar values. It also recognizes `FieldTypeTp::TiDbVectorFloat32`, linking row compatibility to vector datum support.

## Risks and Edge Cases
Correctness depends on field metadata matching the v2 payload bytes. A mismatched type can copy arbitrary payload bytes under a misleading datum flag. Compact integer widths outside 1, 2, 4, or 8 bytes are rejected. The duration behavior intentionally differs from TiDB, so cross-component assumptions about exact v1 bytes should account for the TiKV-specific `DURATION_FLAG` choice.

## Test Signals
Tests encode values through the v2 test encoder, convert with `V1CompatibleEncoder`, and decode with `RawDatumDecoder`. Covered types include signed and unsigned integers, real numbers including infinities, decimals, bytes including non-ASCII data, date/datetime/timestamp, JSON, and duration.
