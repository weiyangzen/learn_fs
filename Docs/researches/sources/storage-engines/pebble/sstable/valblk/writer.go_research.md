# sources/storage-engines/pebble/sstable/valblk/writer.go

## Purpose
Writes value blocks and the value-block index for SSTables that separate values from data blocks.

## Important APIs, Types, And Functions
`Writer`, `bufferedValueBlock`, `NewWriter`, `AddValue`, `Size`, `Finish`, `writeValueBlocksIndex`, `Release`, `WriterStats`, and `LayoutWriter` are the main APIs. `valueBlockWriterPool` reuses writers.

## Control Flow
`AddValue` appends non-empty values to the current uncompressed buffer, flushing it through `compressAndFlush` when the block flush governor says it would grow too large. `Finish` flushes the final block, writes buffered physical value blocks through `LayoutWriter`, converts relative handles to file offsets, computes compact field widths, writes the metadata index block, and returns stats. `Release` frees blocks/buffers and returns the writer to the pool.

## State And Persistence Behavior
The writer buffers compressed value blocks in memory until final layout order is known. Persisted output is a sequence of value blocks plus a metadata index block. `WriterStats` records block/value counts and total value-block/index size.

## Dependencies And Integration Points
Depends on block flush governance, physical block maker, block kinds, `valblk.IndexHandle`, and SSTable layout writer methods. Used by raw SSTable writers when value separation is enabled.

## Risks And Edge Cases
All finished value blocks are retained in memory until `Finish`, creating memory pressure for many separated values. Empty values are rejected only under invariants. Errors during layout writes must release owned physical blocks through the layout contract.

## Test Signals
Direct unit tests cover lower-level encodings; end-to-end value-block writer behavior is covered indirectly by SSTable writer tests with value separation.
