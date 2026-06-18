# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_vector_float32.rs

## Purpose
Stores nullable `VectorFloat32` values compactly as contiguous encoded bytes for vector-search related evaluation paths.

## Important APIs, Types, And Functions
`ChunkedVecVectorFloat32` stores `data`, `bitmap`, `length`, and `var_offset`. It implements `get`, `ChunkedVec<VectorFloat32>`, `ChunkRef<VectorFloat32Ref>`, `From<Vec<Option<VectorFloat32>>>`, and `UnsafeRefInto`.

## Control Flow
`push_data` marks the row valid, encodes `VectorFloat32Ref` into `data` using `write_vector_float32`, records the end offset, and increments length. `push_null` records a false bitmap and duplicate offset. `get` slices the row bytes, decodes a `VectorFloat32Ref` with `read_vector_float32_ref`, then unsafely extends the reference lifetime for return. `append`, `truncate`, and `to_vec` mirror other variable-length chunk vectors.

## State And Persistence
In-memory encoded vector bytes. Decoding borrows from `data`, so returned refs are tied to chunk storage despite unsafe lifetime adjustment.

## Dependencies And Integration Points
Depends on `VectorFloat32`, `VectorFloat32Ref`, MySQL vector encoder/decoder traits, `BitVec`, and chunk traits. Integrates vector data into the same nullable column abstraction as scalar types.

## Risks
`unwrap()` on encode/decode can panic if serialization fails or data is corrupt. Unsafe lifetime widening must not outlive backing storage. No local tests were present in the file, so regressions may rely on higher-level vector tests.

## Test Signals
No local unit tests. Expected coverage should come from vector codec and expression/chunk tests.
