# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/jcodec.rs

## Purpose
`json/jcodec.rs` implements binary JSON encoding and decoding for TiKV MySQL JSON values. It writes owned or borrowed JSON documents into TiDB-compatible binary layout and reads that layout back into owned `Json` values. It also provides a simple datum-payload-to-chunk bridge for JSON.

## Important APIs, Types, and Functions
`JsonRef::encoded_len` returns the number of bytes a value contributes to the value area; literals are encoded inline in value entries and contribute zero appended bytes.

`JsonEncoder` provides `write_json`, `write_json_obj_from_keys_values`, `write_json_obj`, `write_json_ref_array`, `write_json_array`, `write_value_entry`, and scalar writers for literal, i64, u64, f64, string, and opaque values. Object and array writers build headers, entry tables, and value sections. `JsonDatumPayloadChunkEncoder::write_json_to_chunk_by_datum_payload` copies a JSON datum payload directly into chunk output. `JsonDecoder::read_json` reconstructs owned `Json` by reading the type byte and then the type-specific payload length.

## Control Flow
Top-level encoding writes the one-byte `JsonType` first, then writes the value bytes. Object encoding sorts key/value entries by key when given unsorted `Vec<(&[u8], JsonRef)>`; `BTreeMap` object encoding relies on map order. It computes key-entry length, value-entry length, key/value payload length, and total size, writes element count and size, writes key entries with offsets and lengths, writes value entries with either inline literal bytes or offsets, then appends keys and non-literal values.

Array encoding computes the value-entry table and appended value size, writes header and value entries, then appends non-literal values. `write_value_entry` writes literal values inline padded to four bytes, while all other types store a little-endian offset and advance the mutable value offset.

Decoding reads the type byte and then determines payload length by type: arrays/objects read their embedded size from the header, strings and opaque values read varint lengths, fixed-width numerics read eight bytes, literals read one byte, date/datetime/timestamp read eight bytes, and time reads twelve bytes.

## State and Persistence Behavior
The encoder defines persisted binary JSON bytes. It does not maintain mutable state beyond the output buffer and local offset counters. The chunk encoder preserves JSON datum payload bytes exactly, so JSON chunk values use the same binary representation as datum payloads.

## Dependencies and Integration Points
The module depends on `codec::prelude` buffer traits, `NumberCodec`, `BTreeMap`, `FieldTypeTp`, `Json`, `JsonRef`, `JsonType`, binary constants, and shared codec errors. It integrates with constructors and typed getters in `json/mod.rs`, navigation in `binary.rs`, comparison and JSON scalar functions, and vectorized chunk execution.

## Risks and Edge Cases
Object key lengths are cast to `u16` and offsets/sizes to `u32`; oversized JSON objects or keys could truncate if not rejected earlier. Decoding arrays/objects reads size from `value[ELEMENT_COUNT_LEN..]` after the type byte, so malformed or too-short buffers can panic before `read_bytes` returns an EOF error. Literal inline encoding assumes `v.value()[0]` exists. Opaque decoding assumes the first payload byte is a MySQL type code before the varint length. Correctness depends on matching `constants.rs` layout exactly.

## Test Signals
`test_json_binary` round-trips null, boolean, signed and unsigned integers, double, UTF-8 string, and nested object/array JSON values by writing with `write_json`, reading with `read_json`, and comparing string output.
