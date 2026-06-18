# sources/storage-engines/pebble/sstable/colblk/uints.go

## Purpose
Defines compact unsigned integer column encodings for columnar blocks. It chooses among zero-width, 1-, 2-, 4-, and 8-byte storage with optional delta-base encoding to reduce per-row bytes.

## Important APIs, Types, and Functions
- `Uint` is the generic unsigned-integer constraint.
- `UintEncoding` stores width in low bits and delta mode in `uintEncodingDeltaBit`.
- `DetermineUintEncoding` and `DetermineUintEncodingNoDelta` choose encodings from min/max and row count.
- `byteWidth` maps integer bit length to 0/1/2/4/8 bytes.
- `UintBuilder` implements `ColumnWriter` for `DataTypeUint`.
- `UintBuilder.Init`, `InitWithDefault`, `Reset`, `Get`, `Set`, `Size`, and `Finish` build and serialize columns.
- `uintColumnSize` and `uintColumnFinish` encode the on-disk layout.
- `reduceUints`, `computeMinMax`, and `uintsToBinFormatter` support narrowing, slow-path stats, and human-readable formatting.

## Control Flow
`Set` grows the backing `[]uint64`, updates running min/max, and records the row that last changed the chosen encoding. `Size` and `Finish` ask `determineEncoding`; the fast path reuses stats when the caller includes the decisive row, otherwise `recalculateEncoding` scans the prefix. `uintColumnFinish` writes an encoding byte, optional little-endian 64-bit delta base, alignment padding, and a width-specific packed array.

## State and Persistence Behavior
A uint column persists as one encoding byte, optional delta base, aligned fixed-width values, and no payload for constant-zero or constant-delta encodings. `InitWithDefault` treats unset rows as zero and may leave elements unset, with `Finish` padding missing values as zero for non-delta encodings. Alignment is part of the persisted column layout and depends on the column offset.

## Dependencies and Integration Points
Used by raw byte offset tables, columnar key/value encoders, index writers, and liveness metadata. Depends on `encoding/binary`, `bits`, unsafe slice casting, endian conversion helpers, `binfmt`, `treeprinter`, and invariant assertions.

## Risks and Edge Cases
Delta encoding is avoided for very small row counts if the eight-byte base is not worth the per-row savings. `useDefault` is intentionally pessimistic for encoding choice. Unsafe casts require correct alignment and sufficient buffer sizing. Incorrect min tracking would either corrupt values or choose an oversized encoding. Width 8 must not be delta encoded.

## Test Signals
Covered by `uints_test.go` for byte width boundaries, encoding choice thresholds, datadriven binary layouts, and randomized encode/decode comparisons through `DecodeUnsafeUints`.
