# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_bytes.rs

## Purpose
Stores `Option<Bytes>` column data compactly for vectorized evaluation.

## Important APIs, Types, And Functions
`ChunkedVecBytes` stores contiguous `data`, validity `bitmap`, logical `length`, and `var_offset` with a leading zero. Public helpers include `push_data_ref`, `push_ref`, `get`, and `into_writer`. Writer types `BytesWriter`, `PartialBytesWriter`, and `BytesGuard` support staged construction.

## Control Flow
Non-null pushes set the bitmap, append bytes, then call `finish_append` to push the new end offset and increment length. Null pushes only set bitmap false and duplicate the current offset. `get` slices `data[var_offset[idx]..var_offset[idx + 1]]` when valid. `append` drains another chunk's data and bitmap, offsets the other `var_offset` entries by the current data length, then resets the other chunk.

## State And Persistence
All state is in memory. Writers consume and return the chunk through guard types, preventing accidental partial ownership leaks in normal use.

## Dependencies And Integration Points
Implements `ChunkedVec<Bytes>` and `ChunkRef<BytesRef>`, uses `BitVec`, and exports byte writer utilities used by encoding lower/upper implementations.

## Risks
Offset invariants are critical; manual mutation could panic or slice incorrectly. `capacity` is approximate. Partial writer must be finished to record a row. `UnsafeRefInto` extends lifetimes for evaluator plumbing and must only be used while storage outlives refs.

## Test Signals
Local tests cover slice/vector construction, get basics, truncate, append/drain behavior, writer APIs including partial writes, plus benches for append and iteration.
