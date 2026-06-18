# sources/storage-engines/pebble/sstable/colblk/unsafe_uints.go

## Purpose
Provides zero-copy decoders for compact uint columns and offset tables, translating `UintEncoding` metadata into unsafe accessors.

## Important APIs, Types, and Functions
- `UnsafeUints` implements `Array[uint64]` with pointer, delta base, and byte width.
- `DecodeUnsafeUints` reads the encoding byte, optional delta base, aligns the data pointer, and returns the accessor plus end offset.
- `makeUnsafeUints` validates allowed widths.
- `UnsafeOffsets` specializes offset access for non-delta 0/1/2/4-byte values.
- `DecodeUnsafeOffsets` rejects delta and 8-byte offset encodings.
- `unsafeGetUint32`, `unsafeSetUint32`, and `unsafeGetUint64` are no-bounds-check helpers.

## Control Flow
For zero rows, decoding returns an accessor pointing at `&b[off]` with width zero, relying on columnar blocks carrying a trailing padding byte. Non-empty decoding validates the encoding, consumes the optional base, aligns to element width, and computes the end offset from `rows * width`.

## State and Persistence Behavior
The accessor stores a pointer into immutable serialized block memory. `UnsafeUints.At` and `UnsafeOffsets.At/At2` are provided by endian-specific files and apply base/width decoding when accessed.

## Dependencies and Integration Points
Used throughout columnar block decoders, especially for uint columns and raw-byte offsets. Integrates with `UintBuilder`, endian helpers, and invariant bounds checks.

## Risks and Edge Cases
The zero-row path assumes callers provide an allocated padding byte. Offset decoding is intentionally stricter than generic uint decoding. Incorrect end-offset calculation can desynchronize subsequent column decoders.

## Test Signals
Covered by `unsafe_uints_test.go` across encoding ranges, row counts, offset specialization, and benchmarks.
