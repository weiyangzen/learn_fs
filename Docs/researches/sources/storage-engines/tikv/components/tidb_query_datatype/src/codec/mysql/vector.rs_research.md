# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/vector.rs

## Purpose
This file implements TiKV's MySQL vector-float32 scalar representation and codec helpers. It stores vectors as raw little-endian `f32` bytes to avoid alignment requirements when data originates from protobuf or row buffers.

## Important APIs, Types, and Functions
`VectorFloat32` owns a `Vec<u8>` and validates through `VectorFloat32Ref::new`. `VectorFloat32Ref<'a>` borrows the byte slice and exposes `len`, `is_empty`, `encoded_len`, `to_owned`, `from_f32`, distance functions, formatting, and ordering. Supported metrics are `l2_squared_distance`, `l2_distance`, `inner_product`, `cosine_distance`, `l1_distance`, and `l2_norm`.

`VectorFloat32Encoder` writes a `u32` little-endian element count followed by raw bytes. `VectorFloat32Decoder` reads that format and validates the resulting slice. `VectorFloat32DatumPayloadChunkEncoder` copies datum payload bytes directly because the chunk format matches the binary format.

## Control Flow and State
Validation checks that byte length is a multiple of four and rejects NaN or infinite values by reading each element with `read_unaligned`. Ordering is lexicographic by float values, then by length. Distance operations first enforce equal dimensions through `check_dims`, then loop over elements using an unsafe unchecked accessor. `l2_norm` intentionally accumulates in `f64` to align with pgvector behavior, while the other metrics accumulate intermediate values in `f32` and return `f64`.

## Dependencies and Integration Points
The module depends on `codec::prelude` for buffer reader/writer traits and number encoding, `bytemuck::cast_slice` for `f32` to byte-slice views, and local `crate::codec::Result`. It integrates with MySQL datum handling through the `FieldTypeTp::TiDbVectorFloat32` path in row v2 compatibility and datum payload/chunk encoders.

## Risks and Edge Cases
The implementation only supports little-endian targets for encode/decode. Borrowed slices can be unaligned by design, so all float reads use `read_unaligned`; this is correct but concentrates safety around index bounds. `index` and debug bounds in `index_unchecked` use `idx > self.len()` instead of `idx >= self.len()`, so direct calls with `idx == len` would read past the logical end; current loops use `0..len`, but this is a risk for future changes. Cosine distance returns `NaN` on zero-norm division and clamps non-NaN similarity to `[-1, 1]`.

## Test Signals
Tests cover NaN/infinity rejection, string formatting, invalid byte length, lexicographic comparison, binary encoding layout, decoding with remaining bytes, empty-vector decoding, and error preservation when decoding incomplete data.
