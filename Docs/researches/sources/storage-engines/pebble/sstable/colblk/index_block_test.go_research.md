<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/index_block_test.go -->
# sources/storage-engines/pebble/sstable/colblk/index_block_test.go

## Purpose
`index_block_test.go` validates columnar index-block encoding, decoding, formatted output, iterator positioning, synthetic transforms, and cache-handle initialization.

## Important APIs, Types, And Functions
`TestIndexBlock` is datadriven over `testdata/index_block`, using `IndexBlockWriter`, `IndexBlockDecoder`, and `IndexIter`. `TestIndexIterInitHandle` constructs a cache-backed block, stores initialized `IndexBlockDecoder` metadata, and repeatedly initializes iterators through `InitHandle` concurrently.

## Control Flow
The datadriven `build` command parses rows of separator, offset, length, and optional props, finishes a block with optional row truncation, prints `UnsafeSeparator(rows-1)`, initializes the decoder, and prints `DebugString`. The `iter` command initializes `IndexIter` with optional synthetic prefix/suffix transforms and executes commands including seek, first, last, next, prev, validity check, and invalidation.

## State And Persistence Behavior
Tests persist an index block in memory, decode it, and in the cache test copy it into a `block.Alloc` buffer with metadata initialized in place. The cache test creates a Pebble cache handle, stores the block, obtains `CacheBufferHandle`s, and verifies `Close` releases handles under concurrent reuse.

## Dependencies And Integration Points
The tests use `datadriven`, `crstrings`, `testkeys.Comparer`, `internal/cache`, `sstable/block`, and `sstable/blockiter`. The concurrent handle test mirrors higher-level block-cache usage.

## Risks
Datadriven expectations must be updated with any binary layout change. The concurrent test checks repeated read-only iterator initialization, but does not race writes because block metadata is immutable after initialization.

## Test Signals
Signals include golden debug strings, iterator transcript output, correct block handles and props, `IsDataInvalidated` transitions, and lack of data races or handle misuse across eight concurrent workers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/index_block_test.go -->
