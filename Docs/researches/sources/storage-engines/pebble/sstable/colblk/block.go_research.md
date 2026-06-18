<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/block.go -->
# sources/storage-engines/pebble/sstable/colblk/block.go

## Purpose
`block.go` defines the common on-disk/in-memory columnar block envelope used by data, index, keyspan, and simple key/value blocks. It documents the block format: a custom header area, a fixed columnar header containing version, column count, row count, one 5-byte header per column, encoded column payloads, and a final padding byte that keeps "one past the column" pointers inside an allocated object.

## Important APIs, Types, And Functions
Key exports are `Version`, `Header`, `HeaderSize`, `DecodeHeader`, `BlockEncoder`, `FinishBlock`, `DecodeColumn`, and `BlockDecoder`. `BlockEncoder.Init` allocates or reuses aligned storage through `crbytes.AllocAligned`, writes the fixed header at the custom-header offset, and tracks the next column-header slot plus the next data page offset. `BlockEncoder.Encode` asks a `ColumnWriter` to finish each physical column and records its `DataType` and page start. `BlockEncoder.Finish` writes the trailing padding byte and asserts that the computed offset consumed the entire allocation. `BlockDecoder` owns a decoded `Header`, raw block bytes, and `customHeaderSize`, and exposes typed accessors for bitmap, raw bytes, prefix bytes, and uint columns.

## Control Flow
Encoding is size-first: callers compute a full block size, initialize a `BlockEncoder`, encode each column writer in order, then finish. Decoding is header-first: `DecodeBlock` or `BlockDecoder.Init` records metadata, and typed column access validates the column index and type before invoking the column's `DecodeFunc`. `DecodeColumn` also checks that the decoded end offset equals the next column's page start, so malformed column decoders or inconsistent offsets panic early.

## State And Persistence Behavior
The persistent representation is little-endian for header fields and column page offsets. `BlockEncoder.Reset` mangles old buffers in invariant builds and drops very large retained buffers above `maxBlockRetainedSize`. The final padding byte is part of the persisted block image. `BlockDecoder.Header` returns custom header bytes, while `pageStart` reads column offsets with unsafe pointer arithmetic into the block buffer.

## Dependencies And Integration Points
The file depends on `ColumnWriter`/`DecodeFunc` from `column.go` and concrete column encodings such as `Bitmap`, `UnsafeUints`, `RawBytes`, and `PrefixBytes`. It integrates with `binfmt` and `treeprinter` through `FormattedString`, `HeaderToBinFormatter`, and `ColumnToBinFormatter`, enabling datadriven golden tests and human binary-format inspection. Higher-level files add custom headers for data and keyspan blocks on top of this same envelope.

## Risks
Risks are concentrated around unsafe access, alignment, and offset accounting. The caller must supply a correctly computed size, aligned buffer, correct custom-header size, and a matching column schema. The format has no defensive bounds checks beyond panics, so production callers generally rely on block-cache metadata initialization converting panics to corruption errors in higher-level code. Adding a new `DataType` requires updating formatter and typed decoder dispatch paths.

## Test Signals
`block_test.go` exercises this file directly with datadriven format output and randomized round trips across bool, uint, raw bytes, and prefix bytes columns. Other block tests indirectly stress `HeaderSize`, `BlockEncoder`, `BlockDecoder`, and typed decoding through data, index, keyspan, and key/value formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/block.go -->
