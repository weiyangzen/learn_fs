# sources/storage-engines/pebble/sstable/colblk_writer.go

## Purpose
Implements `RawColumnWriter`, the SSTable raw writer for `TableFormatPebblev5+` column-oriented data, index, and keyspan blocks. It coordinates point/range key ingestion, block flushing, index buffering, value/blob metadata, filters, properties, and final file layout.

## Important APIs, Types, and Functions
- `RawColumnWriter` holds writer options, metadata, properties, columnar data/index/keyspan writers, value-block writer, blob liveness writer, filter writer, block property collectors, async write queue, and `layoutWriter`.
- `newColumnarWriter` initializes defaults, flush governors, encoders, collectors, filters, value blocks, and the data-block write goroutine.
- Public/raw writer methods include `Error`, `EstimatedSize`, `ComparePrev`, `IsLikelyMVCCGarbage`, `SetSnapshotPinnedProperties`, `Metadata`, `EncodeSpan`, `Add`, `AddWithBlobHandle`, `AddWithDualTierBlobHandles`, `Close`, `rewriteSuffixes`, `copyDataBlocks`, `addDataBlock`, `copyProperties`, and `SetValueSeparationProps`.
- Internal helpers include `evaluatePoint`, `internalAdd`, `flushDataBlockWithoutNextKey`, `enqueueDataBlock`, `enqueuePhysicalBlock`, `finishIndexBlock`, `flushBufferedIndexBlocks`, `drainWriteQueue`, `getExistingFilter`, and `shouldFlushWithoutLatestKV`.

## Control Flow
`Add` validates point key kind, evaluates ordering/obsolete/value-block decisions, stores values in-place or in value blocks, updates tiering metadata, and delegates to `internalAdd`. `internalAdd` appends to the current data block, decides whether to flush before the latest KV, updates block properties, filters, writer metadata, and table properties. Data blocks are compressed/checksummed and sent to a write queue; index entries are buffered and may create two-level indexes. `Close` flushes pending data, drains the write queue, writes index/filter/range/value/blob/tiering/properties blocks, finalizes attributes and footer, records metadata, and clears resources.

## State and Persistence Behavior
Persistent state includes columnar data blocks, columnar index blocks, optional two-level top index, table filter, range deletion/key blocks, value blocks/index, blob reference liveness block, tiering histogram, properties block, metaindex, and footer. Writer state tracks obsolete bits, sequence number bounds, smallest/largest keys, raw size/count properties, tombstone-dense block counts, compression stats, and block property collector outputs. Data blocks are written asynchronously but metadata blocks are written synchronously after the data queue drains.

## Dependencies and Integration Points
Integrates with `colblk` data/index/keyspan encoders, `layoutWriter`, `block.PhysicalBlockMaker`, `valblk.Writer`, blob handles, tiered metadata, block property collectors, table filters, suffix rewriting, and `CopySpan`. It depends on writer options from `options.go`, table format capabilities from `format.go`, and properties serialization from `properties.go`.

## Risks and Edge Cases
Key order checks and obsolete-bit correctness are critical, especially strict-obsolete SSTables. Value blocks are only used for likely MVCC garbage and require careful prefix comparison. Blob handles require v6+ and dual-tier handles require tiering columns. `Close` must preserve data block write ordering and detect write-queue errors. Copy/suffix rewrite paths deliberately skip or copy some derived metadata, which can overcount properties or omit block properties. The writer is not reusable after `Close`.

## Test Signals
Covered by `colblk_writer_test.go` datadriven layout/properties tests, broader `data_test.go` helpers, writer tests outside this subset, copier tests, and invariant validation of encoded data blocks when enabled.
