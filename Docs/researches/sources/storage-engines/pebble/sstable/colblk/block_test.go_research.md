<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/block_test.go -->
# sources/storage-engines/pebble/sstable/colblk/block_test.go

## Purpose
`block_test.go` validates the generic columnar block envelope and provides shared test helpers for randomized blocks. It checks that heterogeneous column schemas can be encoded, decoded, and formatted without losing row data or corrupting header metadata.

## Important APIs, Types, And Functions
The test-local `testColumnSpec` records a column `DataType`, integer range metadata for uint columns, and bundle size for prefix-byte columns. `intRange` defines interesting uint ranges and expected encodings reused by other tests. `TestBlockWriter` is a datadriven test over `testdata/block_writer`; `randBlock`, `buildBlock`, and `testRandomBlock` generate and verify random blocks; `TestBlockWriterRandomized` drives single-column and multi-column randomized coverage.

## Control Flow
The datadriven test accepts `init`, `write`, and `finish` commands. `init` builds a schema and the corresponding column writers, `write` parses rows into the proper builders, and `finish` calls `FinishBlock`, decodes the result, and returns `FormattedString`. The randomized path builds in-memory expected column values, encodes them through concrete builders, decodes with `DecodeBlock`, checks header column count and row count, validates data types, and compares cloned decoded arrays against the expected values.

## State And Persistence Behavior
The tests model persistence by serializing a full block byte slice through `FinishBlock` and immediately treating it as the decoder input. Randomized tests cover value distributions that force distinct uint physical encodings and prefix-byte bundle choices. Prefix-byte input is sorted before encoding because that encoding requires lexicographic order.

## Dependencies And Integration Points
The tests depend on concrete column writers (`BitmapBuilder`, `UintBuilder`, `RawBytesBuilder`, `PrefixBytesBuilder`) and typed block decoder accessors. They use `datadriven` for golden-format output, `crbytes.CommonPrefix` for prefix-byte construction, and `Clone` from `column.go` to materialize decoded arrays.

## Risks
The datadriven `write` command currently sets bool and uint builder rows starting at the per-command row index rather than the aggregate row index, so it is best suited for simple scripted cases. Randomized coverage is seed-based with logged time seeds; failures are reproducible only if the seed is captured. The randomized tests check equality after decode but do not fuzz malformed headers or inconsistent column offsets.

## Test Signals
This file is itself the direct test signal for the block envelope. It exercises type dispatch, row/header metadata, `FinishBlock`, `DecodeBlock`, formatted output, and randomized combinations of up to nine columns.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/block_test.go -->
