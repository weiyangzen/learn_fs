# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_set.rs

## Purpose
Stores `Option<Set>` values as set-value bitmaps plus shared set-name data.

## Important APIs, Types, And Functions
`ChunkedVecSet` stores `data: Arc<BufferVec>`, validity `bitmap`, and per-row `value: Vec<u64>`. It implements `get`, `ChunkedVec<Set>`, `PartialEq`, `ChunkRef<SetRef>`, `From<Vec<Option<Set>>>`, and `UnsafeRefInto`.

## Control Flow
`push_data` sets bitmap true and pushes the set bitmask. `push_null` sets bitmap false and pushes zero. `get` returns `SetRef::new(&data, value[idx])` for non-null rows. `append` drains row values and bitmap from another vector but keeps the receiver's shared `data`.

## State And Persistence
In-memory row data plus an `Arc` to the set element names. The name buffer is not populated by the public API here; tests set it directly.

## Dependencies And Integration Points
Uses `tikv_util::buffer_vec::BufferVec`, `Arc`, `BitVec`, and evaluator `ChunkRef`. Integrates with MySQL SET scalar types.

## Risks
Appending vectors with different `data` dictionaries can produce wrong names because only row bitmasks are appended. Comments note missing setter support and future refactor needs. Bitmap and value vector must stay aligned.

## Test Signals
Local tests cover basics, truncation, append behavior, and equality over data, bitmap, and values.
