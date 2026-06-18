# sources/storage-engines/raft-engine/src/codec.rs

## Purpose
Provides low-level numeric encoding and decoding helpers used by raft-engine binary formats, including mem-comparable big-endian encodings, descending-order encodings, protobuf-compatible varints, and little-endian primitives.

## Important APIs, Types, And Functions
Exports `BytesSlice`, codec `Error`, `Result`, trait `NumberEncoder`, and decoders such as `decode_i64`, `decode_u64`, `decode_var_u64`, `decode_var_i64`, `decode_f64`, little-endian decoders, and `read_u8`. Internal helpers include `order_encode_i64`, `order_decode_i64`, `order_encode_f64`, `order_decode_f64`, and `read_num_bytes`.

## Control Flow
Encoders are extension methods on any `Write`. Ordered integer encodings flip the sign bit or invert bytes for descending order. Ordered float encodings transform IEEE bits so lexicographic byte order matches numeric order for supported values. Varint encoding emits seven-bit chunks compatible with protobuf unsigned varints, and signed varints use zig-zag style transformation. Decoders consume from `&mut &[u8]`, advancing slices only after successful byte consumption.

## State And Persistence Behavior
This file directly defines on-disk byte layout for numbers embedded in log files and batches. It is stateless at runtime, but any format change would affect backward compatibility.

## Dependencies And Integration Points
Depends on `byteorder`, `thiserror`, protobuf tests, and Rust I/O traits. File-format code uses `NumberEncoder` and decoders to encode log headers and versions.

## Risks And Edge Cases
Incorrect order transforms would break sorted comparisons. Varint decoding uses unchecked indexing after length guards, so guard correctness is critical. Floating NaN is intentionally not part of ordering tests. Unexpected EOF and overflow must be distinguishable from format errors.

## Test Signals
Unit tests cover serialization round trips, lexicographic order, protobuf varint compatibility, little-endian helpers, EOF handling, overflow, and `read_u8` exhaustion.
