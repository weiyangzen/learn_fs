# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/constants.rs

## Purpose
`json/constants.rs` centralizes byte-size, literal-value, and comparison-precedence constants for TiKV's binary JSON implementation. These constants are shared by JSON encoders, decoders, binary navigation, comparison, and semantic helpers.

## Important APIs, Types, and Functions
The file exports literal codes `JSON_LITERAL_NIL`, `JSON_LITERAL_TRUE`, and `JSON_LITERAL_FALSE`. Binary layout constants include fixed widths such as `TYPE_LEN`, `LITERAL_LEN`, `U16_LEN`, `U32_LEN`, `NUMBER_LEN`, `TIME_LEN`, `DURATION_LEN`, `HEADER_LEN`, `KEY_OFFSET_LEN`, `KEY_LEN_LEN`, `KEY_ENTRY_LEN`, `VALUE_ENTRY_LEN`, `ELEMENT_COUNT_LEN`, and `SIZE_LEN`.

Comparison precedence constants include `PRECEDENCE_BLOB`, `PRECEDENCE_BIT`, `PRECEDENCE_OPAQUE`, `PRECEDENCE_DATETIME`, `PRECEDENCE_TIME`, `PRECEDENCE_DATE`, `PRECEDENCE_BOOLEAN`, `PRECEDENCE_ARRAY`, `PRECEDENCE_OBJECT`, `PRECEDENCE_STRING`, `PRECEDENCE_NUMBER`, and `PRECEDENCE_NULL`.

## Control Flow
There is no executable control flow. The constants are consumed by other modules to compute offsets, lengths, and ordering categories. `HEADER_LEN` is derived from element-count and size lengths; key and value entry lengths are derived from their component widths.

## State and Persistence Behavior
The constants define the persisted binary JSON layout contract. Changing any length constant changes how JSON bytes are encoded and decoded. Changing precedence constants changes SQL-visible comparison behavior. The file itself holds no mutable state.

## Dependencies and Integration Points
This file has no imports. It is used by `binary.rs`, `jcodec.rs`, `comparison.rs`, and any other JSON module that needs binary layout or precedence definitions. The constants align TiKV's Rust implementation with TiDB's binary JSON format.

## Risks and Edge Cases
The major risk is drift from TiDB/MySQL binary JSON layout or precedence. Because many callers perform unchecked slicing based on these values, an incorrect size constant can cascade into panics or corrupt reads. There are no local tests, so coverage is indirect through JSON codec, navigation, comparison, containment, and depth tests.

## Test Signals
No tests live in this file. Effective test signals are the downstream tests in `binary.rs`, `jcodec.rs`, `comparison.rs`, `json_contains.rs`, and `json_depth.rs`, all of which rely on these constants for correct offsets and ordering.
