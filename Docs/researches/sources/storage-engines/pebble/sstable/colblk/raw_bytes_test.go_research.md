# sources/storage-engines/pebble/sstable/colblk/raw_bytes_test.go

## Purpose
Datadriven and benchmark coverage for `RawBytesBuilder`, `DecodeRawBytes`, binary formatting, and random access over raw byte columns.

## Important APIs, Types, and Functions
- `TestRawBytes` runs `testdata/raw_bytes` commands.
- `build` command resets the builder, parses an artificial start offset, appends input lines, optionally truncates by `count`, writes to aligned storage, formats the encoded structure, and decodes it.
- `at` command reads values from the last decoded `RawBytes`.
- `BenchmarkRawBytes` measures builder throughput and `At` traversal for slice lengths 8, 128, and 1024 over 32 KiB of data.

## Control Flow
Each datadriven `build` command creates a fresh serialized column, validates `Size` against `Finish`, uses `rawBytesToBinFormatter` to display offsets/data, decodes from the adjusted start offset, and verifies decoded end offset. Later `at` commands operate on the retained decoded column.

## State and Persistence Behavior
The test intentionally allocates aligned buffers through `crbytes.AllocAligned`, exercising the same alignment assumptions as block serialization. It validates offset-relative persistence by varying start offset and checking decoded end offsets against the original absolute finish offset.

## Dependencies and Integration Points
Uses `datadriven`, `crstrings`, `crbytes`, `binfmt`, and `treeprinter`. It indirectly verifies `UintBuilder` offset serialization because `RawBytesBuilder` delegates its offset table to the uint column path.

## Risks and Edge Cases
The datadriven suite depends on stable binary-format output. Benchmarks discard output through `io.Discard`, so they test cost but not semantics. The `count` override exercises finishing a prefix of appended rows.

## Test Signals
Strong signal for exact serialized layout and access semantics. Benchmarks give performance regression coverage for both encoding and zero-copy lookup.
