# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_json.rs

## Purpose
Stores `Option<Json>` values compactly in contiguous bytes for vectorized execution.

## Important APIs, Types, And Functions
`ChunkedVecJson` stores `data`, `bitmap`, `length`, and `var_offset`. It implements `get`, `ChunkedVec<Json>`, `ChunkRef<JsonRef>`, `From<Vec<Option<Json>>>`, and `UnsafeRefInto`.

## Control Flow
For non-null JSON, `push_data` sets bitmap true, writes one byte of `JsonType`, appends raw JSON value bytes, records end offset, and increments length. Nulls record the current offset with bitmap false. `get` checks bitmap, converts the first stored byte to `JsonType`, and returns `JsonRef` over the payload. `append` drains another chunk and offsets variable positions.

## State And Persistence
In-memory only. The first byte of every non-null row is type metadata; payload interpretation is delegated to JSON codecs.

## Dependencies And Integration Points
Depends on `Json`, `JsonRef`, `JsonType`, `BitVec`, and common chunk macros. Used by expression columns carrying JSON values.

## Risks
`JsonType::try_from(...).unwrap()` panics if stored bytes are corrupt. Offset invariants are critical. `UnsafeRefInto` must not outlive the backing vector.

## Test Signals
Local tests cover slice construction, basics, truncation, append/drain, string and numeric JSON examples.
