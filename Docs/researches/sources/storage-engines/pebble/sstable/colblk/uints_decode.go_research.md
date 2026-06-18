# sources/storage-engines/pebble/sstable/colblk/uints_decode.go

## Purpose
Provides a compact unsafe decoder holder for aligned little-endian 64-bit integer arrays in columnar blocks.

## Important APIs, Types, and Functions
- `unsafeUint64Decoder` holds only an unsafe pointer to keep embedded block decoders small.
- `makeUnsafeUint64Decoder` validates zero-length cases, pointer alignment, and buffer length before returning the decoder.
- The `At` method is implemented in endian-specific files outside this work item.

## Control Flow
Construction returns an empty decoder for `n == 0`. Otherwise it uses `unsafe.SliceData`, checks alignment against `align64`, verifies that `len(buf)` can hold `n` 64-bit values, and stores the raw pointer.

## State and Persistence Behavior
This file does not serialize data itself. It assumes the persisted buffer already contains little-endian 64-bit values and records a pointer into that buffer. The source buffer must outlive the decoder.

## Dependencies and Integration Points
Used by columnar block decoders that need low-overhead uint64 access. Depends on shared alignment constants and endian-specific methods in the `colblk` package.

## Risks and Edge Cases
Misaligned buffers panic. The decoder is intentionally unsafe and depends on callers validating buffer lifetime and bounds. Endianness behavior is split across build-specific files, so changes must stay compatible with those implementations.

## Test Signals
Indirectly tested by uint and unsafe uint tests that encode and then decode uint columns across widths and row counts.
