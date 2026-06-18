<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_test.go -->
# sources/storage-engines/pebble/sstable/colblk/data_block_test.go

## Purpose
`data_block_test.go` is the primary correctness and behavior test suite for columnar data blocks. It covers datadriven binary-format output, writer sizing, iteration commands, suffix rewriting, validation, random `SeekPrefixGE`/`NextWithSamePrefix` semantics, and benchmark setup helpers.

## Important APIs, Types, And Functions
`testKeysSchema` defines the default schema used by most tests. `dataBlockIterInternalIterator` adapts `DataBlockIter` to `itertest.RunInternalIterCmd`. `TestDataBlock` runs datadriven commands over `testdata/data_block`. Helper functions `makeTestKeyRandomKVs`, `randTestKey`, and `getInternalValuer` support benchmarks and randomized tests. `TestDataBlockIterSeekPrefixGENextWithSamePrefix` independently verifies prefix-seek and same-prefix iteration semantics. `BenchmarkDataBlockWriter` and `BenchmarkDataBlockDecoderInit` measure writer and metadata initialization costs.

## Control Flow
The datadriven test supports `init`, `write`, `write-block`, `rewrite`, `finish`, and `iter`. Writes parse internal keys and values, compute key comparisons with the encoder key writer, set value prefixes for in-place, value-handle, or blob-handle strings, mark shadowed duplicate point keys obsolete, and track sizes after each row. `finish` can serialize all rows or `rows=n`, decodes and formats the block, and runs `DataBlockValidator`. `iter` initializes `DataBlockIter` with optional synthetic seqnum/prefix/suffix and obsolete hiding, then delegates commands to `itertest`.

## State And Persistence Behavior
The tests persist blocks to byte slices and repeatedly decode them through `DataBlockDecoder`. They exercise `Finish(rows, sizes[rows-1])`, including omitting the last row, and confirm the returned last key. Rewriting replaces suffixes and updates decoder state to the rewritten block. The randomized prefix test builds a block with random obsolete bits and then compares visible iterator behavior against a linear-scan model under random transforms.

## Dependencies And Integration Points
The file connects `colblk` to `internal/base`, `internal/testkeys`, `itertest`, `binfmt`, `treeprinter`, `sstable/block`, and `sstable/blockiter`. It is the closest test proxy for how upper-level SSTable iterators consume `DataBlockIter`.

## Risks
The randomized test uses time seeds, so logs are required for exact reproduction. The datadriven lazy-value handler always returns a mock in-place value for external handles, so it verifies routing more than storage lookup. Tiering metadata has separate coverage in `data_block_meta_test.go`.

## Test Signals
Strong signals include golden binary layout, validator failures surfaced in output, iterator command transcripts, suffix rewrite output, randomized prefix-seek equivalence, and benchmarks for writer and metadata initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_test.go -->
