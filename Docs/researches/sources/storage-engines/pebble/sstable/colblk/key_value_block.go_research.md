<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/key_value_block.go -->
# sources/storage-engines/pebble/sstable/colblk/key_value_block.go

## Purpose
`key_value_block.go` implements a simple two-column key/value block used as a drop-in columnar replacement for SSTable metaindex and properties blocks.

## Important APIs, Types, And Functions
`KeyValueBlockWriter` owns raw-byte key and value builders, row count, and a `BlockEncoder`. It exposes `Init`, `Rows`, `AddKV`, `Finish`, and an internal `size`. `KeyValueBlockDecoder` owns raw-byte key/value arrays plus a `BlockDecoder`, and exposes `Init`, `DebugString`, `Describe`, `BlockDecoder`, `KeyAt`, `ValueAt`, and `All`.

## Control Flow
Writing initializes raw-byte builders, appends key/value pairs row by row, computes a two-column block size plus trailing padding, and encodes keys then values. Decoding initializes the generic block decoder and typed raw-byte columns. `All` returns an `iter.Seq2` that yields each key/value pair until exhausted or the callback stops.

## State And Persistence Behavior
Persistent state is a two-column columnar block with no custom header. Keys and values are copied into `RawBytesBuilder` storage and serialized as raw byte slices. The decoder returns slices backed by the block data, so callers must respect block lifetime and immutability.

## Dependencies And Integration Points
This block format shares the common block envelope and `RawBytes` column encoding. Tests encode block handles for metaindex values and arbitrary properties values. The `iter` package integration provides a convenient range-over API for consumers that want sequential key/value access.

## Risks
There is no explicit `Reset` method, so writer reuse currently requires `Init` and relies on builder initialization behavior. `Finish(rows)` does not enforce `rows == Rows()` or `Rows()-1` in this file, so callers must pass a sensible row count. Decoded key/value slices alias block memory.

## Test Signals
`key_value_block_test.go` builds metaindex and properties blocks from datadriven inputs and verifies debug-format output after decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/key_value_block.go -->
