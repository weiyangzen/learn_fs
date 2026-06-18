<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/index_block.go -->
# sources/storage-engines/pebble/sstable/colblk/index_block.go

## Purpose
`index_block.go` implements columnar SSTable index blocks. These blocks map separator keys to data-block handles and optional block properties, and the same writer supports first-level and second-level index blocks.

## Important APIs, Types, And Functions
`IndexBlockWriter` owns `RawBytesBuilder` separators, uint offset/length builders, raw block-property bytes, row count, and a `BlockEncoder`. It exposes `Init`, `Reset`, `Rows`, `AddBlockHandle`, `UnsafeSeparator`, `Size`, and `Finish`. `IndexBlockDecoder` decodes separators, offsets, lengths, block properties, and the embedded `BlockDecoder`. `IndexIter` implements `blockiter.Index` with initialization from a decoder, raw bytes, or a block-cache handle; navigation methods; separator comparison helpers; `BlockHandleWithProperties`; invalidation; close; and tree-step diagnostics.

## Control Flow
Writing appends one row per index entry and serializes four columns in fixed order: separator, offset, length, properties. `Finish(rows)` supports all rows or all but the last row and uses the common block envelope. Decoding initializes typed column accessors. `IndexIter.SeekGE` performs binary search over separators, applying synthetic prefix/suffix transforms if configured. Navigation methods update the row index and return validity. `BlockHandleWithProperties` reads the current row's offset, length, and props into a `block.HandleWithProperties`.

## State And Persistence Behavior
Persistent state is a four-column columnar block with no custom header. Offsets and lengths are uint columns, separators and properties are raw bytes columns. `IndexIter` may own a `block.BufferHandle`; `Init`, `InitHandle`, and `Close` release any previous handle before replacing or clearing it. Synthetic transforms are transient and materialized into `keyBuf` for comparisons and returned separators.

## Dependencies And Integration Points
The file integrates with `sstable/block` handles and cache handles, `blockiter.Index`, `base.Comparer`, and block-cache metadata initialized by `InitIndexBlockMetadata` in `data_block.go`. Higher-level table iterators use this iterator to locate data blocks.

## Risks
Separators can be equal in snapshot scenarios, so binary search and comparison semantics must use greater-or-equal carefully. Transform handling currently materializes keys during binary search, which is correct but potentially expensive. `BlockHandleWithProperties` panics in invariant builds if called on an invalid row. Decoder initialization assumes well-formed aligned block data.

## Test Signals
`index_block_test.go` provides datadriven build/format/iterator coverage, synthetic transform checks through iterator commands, and a concurrent `InitHandle` cache test that validates block metadata use, handle release, iteration, and invalidation behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/index_block.go -->
