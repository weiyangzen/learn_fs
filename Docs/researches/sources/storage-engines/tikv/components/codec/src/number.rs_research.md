# sources/storage-engines/tikv/components/codec/src/number.rs

## Purpose
Implements primitive numeric encoding and decoding for fixed-width memory-comparable values, little-endian non-comparable values, and protobuf-style varints. Extension traits connect those routines to TiKV buffer readers and writers.

## APIs and control flow
`NumberCodec` includes direct encode/decode routines for `u8`, `u16`, `u32`, `u64`, descending `u64`, comparable `i64` and `f64`, little-endian `u16/i16/u32/i32/f32/u64/i64/f64`, and varint `u64/i64`. Comparable fixed-width values use big-endian bytes; descending values invert the comparable `u64`; signed and float forms delegate to `convert.rs`. Varint encoding writes 7-bit groups with continuation bits. Varint decoding has a fast path for buffers at least 10 bytes and a bounded slow path for shorter buffers; `get_first_encoded_var_int_len` returns the complete prefix length or the available incomplete length.

`NumberDecoder` extends `BufferReader` with methods that validate remaining bytes before advancing. `NumberEncoder` extends `BufferWriter` with symmetric writers; fixed-width writers require exact remaining capacity, while varint writers require reservation of 10 bytes but advance by actual encoded length.

## State, dependencies, and integration
The module is stateless except for mutating buffer cursors. It depends on `byteorder`, crate `buffer`, crate errors, and conversion helpers. It is a central dependency of byte compact encoding and any TiKV binary format using the codec prelude.

## Risks and test signals
Many routines use unsafe pointer reads/writes and rely on prior capacity checks. Varint decoding accepts the 10th byte with only one payload bit, matching u64 width but without explicit validation of overlong encodings. Tests are extensive: sample generation covers numeric boundaries, ordering checks verify memory-comparable encodings, cursor tests verify no mutation on insufficient space, varint tests compare protobuf output and incomplete-buffer behavior, and benches compare TiKV, byteorder, bytes, protobuf, and older implementations.
