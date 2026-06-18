# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/enums.rs

## Purpose
`enums.rs` implements TiKV's MySQL `ENUM` value wrapper and codecs. It keeps the SQL-visible enum name together with the numeric enum index, while comparison, hashing, boolean conversion, and integer casts use the numeric value as MySQL does.

## Important APIs, Types, and Functions
`Enum` owns `name: Vec<u8>` and `value: u64`. `Enum::new` forces the name to empty when `value == 0`, since MySQL enum value zero represents the empty invalid value. Accessors expose `value`, `value_ref`, `name`, and `as_ref`. `Enum::get_value_name` maps a 1-based enum value to `FieldType.elems[value - 1]`, or empty bytes for zero.

`EnumRef<'a>` borrows `name` and `value`, supports `new`, `to_owned`, `is_empty`, `value`, `value_ref`, `name`, `as_str`, and `len`. It implements `Display`, `ToInt`, and `ToStringValue`.

`EnumEncoder` writes either comparable uint datum bytes (`write_enum_uint`) or chunk bytes (`write_enum_to_chunk`, little-endian `u64` followed by raw name bytes). `EnumDatumPayloadChunkEncoder` converts compact-bytes, fixed uint, or varuint datum payloads into chunk layout using `FieldType.elems`. `EnumDecoder` reads the same datum forms or chunk form and reconstructs `Enum`.

## Control Flow
Datum decode reads the numeric enum value, looks up the corresponding name from the protobuf field type, and constructs an owned `Enum`. Datum-to-chunk conversion follows the same path but writes the chunk layout directly. Chunk decode reads an eight-byte little-endian value and treats all remaining bytes in the reader as the enum name. Display returns an empty string for value zero and UTF-8-lossy text for nonzero names.

## State and Persistence Behavior
`Enum` itself is in-memory. Persisted datum payloads store only the numeric enum value; the name is derived from schema metadata (`FieldType.elems`) at decode time. Chunk payloads store both value and name bytes for execution. This means schema metadata is part of correct interpretation for datum reads, and chunk decoding consumes the remaining buffer as a name.

## Dependencies and Integration Points
The file depends on `codec::prelude` number codecs, `tipb::FieldType`, `FieldTypeTp`, `ToInt`, `ToStringValue`, and `EvalContext`. It integrates with table schema field metadata, scalar casts to integer/string, vectorized chunk execution, ordering, hashing, and boolean evaluation.

## Risks and Edge Cases
`Enum::get_value_name` indexes `elems[value - 1]` without an explicit bounds check, so invalid stored enum values or mismatched schema metadata can panic. Equality, ordering, and hashing ignore the name, so two enums with the same value but different names compare equal. `read_enum_from_chunk` consumes all remaining bytes as the name, so callers must frame chunk data correctly. UTF-8 validation only occurs through `EnumRef::as_str`; display and string conversion are lossy.

## Test Signals
Tests cover display/string conversion, UTF-8 string access, zero-value emptiness, fixed uint/varuint/compact-bytes datum decoding, chunk encoding, and datum-payload-to-chunk conversion for all supported payload forms.
