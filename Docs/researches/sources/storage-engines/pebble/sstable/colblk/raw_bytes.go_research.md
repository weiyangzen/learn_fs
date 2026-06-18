# sources/storage-engines/pebble/sstable/colblk/raw_bytes.go

## Purpose
Implements `RawBytes`, the columnar block representation for an array of byte slices. It serializes an offset table followed by concatenated byte data, allowing columnar readers to return stable `[]byte` slices without per-row copies.

## Important APIs, Types, and Functions
- `RawBytes` stores `slices`, `UnsafeOffsets`, and an unsafe pointer to the data payload.
- `DecodeRawBytes` decodes the offset table using `DecodeUnsafeOffsets`, validates the computed end offset, and returns a zero-copy accessor.
- `RawBytes.At`, `Slice`, `Offsets`, and `Slices` expose individual slices and metadata.
- `RawBytesBuilder` implements `ColumnWriter` for `DataTypeBytes`.
- `RawBytesBuilder.Put`, `PutConcat`, `UnsafeGet`, `Size`, and `Finish` append values, estimate serialized size, and write the encoded column.
- `rawBytesToBinFormatter` supports binary layout descriptions used by datadriven tests and layout debugging.

## Control Flow
The builder starts with an initial zero offset, appends bytes to `data`, and records the cumulative data length in a `UintBuilder`. `Size` first sizes `rows+1` offsets and then adds the final cumulative byte count. `Finish` serializes the offsets table and copies the selected data prefix. Decoding reverses this path by reading `count+1` offsets, deriving the data start from the offset table end, and using the last offset to compute the full encoded span.

## State and Persistence Behavior
The persisted form is an offsets table encoded as a uint column, followed by raw byte data. Offsets are relative to the data section, not the full block. `Reset` keeps allocated capacity, mangles old data under invariant hooks, and reinitializes the zero offset. Decoded `RawBytes` points directly into the backing block buffer, so callers must keep that buffer alive and must not mutate returned slices.

## Dependencies and Integration Points
Depends on `UintBuilder`/`UnsafeOffsets`, `binfmt`, `treeprinter`, `invariants`, and unsafe pointer helpers. It is used by columnar data blocks, key/value blocks, and reference liveness blocks for byte-valued columns.

## Risks and Edge Cases
`DecodeRawBytes` panics on `math.MaxUint32` counts and on offsets extending beyond the byte slice. Unsafe pointer access requires block buffers to remain pinned. A mismatch between `Size` and `Finish` would corrupt subsequent columns. Large individual values force wider offset encodings, increasing block size.

## Test Signals
Covered by `raw_bytes_test.go`, which datadriven-tests size, binary formatting, decoding end offsets, and `At` lookups, plus benchmarks for builder and access throughput across slice lengths.
