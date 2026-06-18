# sources/storage-engines/pebble/sstable/rowblk_writer.go

## Purpose
Implements Pebble's row-oriented SSTable writer (`RawRowWriter`) for table formats through Pebblev4. It coordinates point, range deletion, range key, index, filter, value block, property, footer, and suffix-rewrite output using row-oriented blocks.

## Important APIs, Types, And Functions
`RawRowWriter` implements the row-block `RawWriter` surface: `Add`, blob-handle rejection methods, `EncodeSpan`, `ComparePrev`, `IsLikelyMVCCGarbage`, `Error`, `Close`, `EstimatedSize`, `Metadata`, suffix/data-block copy helpers, and internal block/property/filter setters. Important helpers include `coordinationState`, `sizeEstimate`, `indexBlockBuf`, `dataBlockEstimates`, `dataBlockBuf`, `bufferedIndexBlock`, `makeAddPointDecisionV2`, `makeAddPointDecisionV3`, `addPoint`, `addTombstone`, `addRangeKey`, `flush`, `maybeFlush`, `finishDataBlockProps`, `addIndexEntry`, `writeTwoLevelIndex`, and `assertFormatCompatibility`.

## Control Flow And State
`newRowWriter` validates row format use, applies defaults, initializes metadata, flush governors, block writers, optional value-block writer, filter writer, property collectors, obsolete collector, and range-key encoder. Point adds check ordering, decide obsolete status, optionally write older SET values to value blocks in Pebblev3, maybe flush the current data block, update block properties and filters, encode the key/value into the active `rowblk.Writer`, and update table properties.

When a data block flushes, the writer finishes block properties, finalizes the row block, updates tombstone-density counters, compresses/checksums the block, computes an index separator, possibly rotates a lower-level index block, schedules the write through `writeQueue`, and starts a fresh data block. `Close` drains the queue, finalizes the last data block or an empty block, writes filters, single- or two-level indexes, range deletion and range key blocks, value blocks, table properties, metaindex/footer via `layoutWriter`, then records metadata and returns pooled buffers.

## Persistence And Integration
This file is the persistence boundary for row-format SSTables. It writes data blocks, index blocks, meta blocks, properties, filters, range blocks, optional value blocks, and the footer to an `objstorage.Writable`. It integrates with `sstable.Writer`, `layoutWriter`, `rowblk.Writer`, `valblk.Writer`, block property collectors, Bloom filters, `rangedel`/`rangekey` encoders, table format compatibility, and suffix-rewrite/copy APIs.

## Dependencies
Major dependencies include `internal/base` for key kinds and comparers, `keyspan`, `rangedel`, `rangekey`, `objstorage`, `sstable/block`, `blockkind`, `rowblk`, `valblk`, `blob`, `bytealloc`, `invariants`, and `sync.Pool` for reusable block buffers.

## Risks
Correctness depends on strict key ordering, fragmented range tombstones/range keys, accurate block handle offsets, sequential block property collector calls, queue draining before close, and consistent table-format feature gating. The writer contains subtle lifetime rules: separators and properties must be copied or encoded before scratch buffers are reused, and block buffers are pooled after close. Obsolete-key marking in strict-obsolete tables is complex around MERGE, point deletes, lowest-level writes, and forced range-delete obsolescence. Suffix-copy paths intentionally reset or recompute only selected properties and require collector support.

## Test Signals
Direct tests are spread across SSTable writer/reader suites outside this work item. Within this subset, `suffix_rewriter_test.go` exercises `rewriteSuffixes`, filter copying, property remapping, and close/metadata behavior; `rowblk_writer_test.go` protects the underlying block encoder; `single_lvl_iter_benchmark_test.go` builds an SST through `NewWriter` and reads it with row-block iterators.
